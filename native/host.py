"""Native host: local document processing and optional Gemini search. No mail sending."""
import base64
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile
import unicodedata
import uuid

ROOT = Path(__file__).resolve().parent.parent
EMAIL = re.compile(r'[A-Za-z0-9.!#$%&\'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,}')


def key(name):
    return ' '.join(unicodedata.normalize('NFKC', name).casefold().split())


def clean(value):
    return str(value).strip().strip('*').strip()


def textfile(path):
    raw = path.read_bytes()
    if raw.startswith((b'\xff\xfe', b'\xfe\xff')):
        return raw.decode('utf-16')
    try:
        return raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        return raw.decode('cp1252')


def office(request):
    with tempfile.TemporaryDirectory(prefix='bewerbung-request-') as folder:
        source, result = Path(folder) / 'in.json', Path(folder) / 'out.json'
        source.write_text(json.dumps(request, ensure_ascii=False), encoding='utf-8')
        subprocess.run([sys.executable, str(Path(__file__).with_name('office.py')), str(source), str(result)],
            check=True, timeout=180, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        data = json.loads(result.read_text(encoding='utf-8'))
        if 'error' in data:
            raise ValueError(data['error'])
        return data


def read_rows(path):
    if path.suffix.lower() in ('.xls', '.xlsx', '.ods'):
        return office({'kind': 'table', 'source': str(path)})['rows']
    content = textfile(path)
    if content.lstrip().startswith('|'):
        rows = []
        for line in content.splitlines():
            if not line.strip():
                continue
            cells = re.split(r'(?<!\\)\|', line.strip().strip('|'))
            cells = [clean(c.replace('\\|', '|')) for c in cells]
            if all(re.fullmatch(r'[:\-\s]+', c) for c in cells):
                continue
            # Supplied company name contains an unescaped pipe: last two columns are address/email.
            if len(cells) > 3:
                cells = [' | '.join(cells[:-2]), *cells[-2:]]
            rows.append(cells)
        return rows
    try:
        dialect = csv.Sniffer().sniff(content[:8192], delimiters=';,\t')
    except csv.Error:
        dialect = csv.excel
    return list(csv.reader(io.StringIO(content), dialect))


def companies(path):
    rows = read_rows(path)
    if not rows:
        return []
    headers = [key(clean(c)) for c in rows[0]]
    aliases = [('firmenname', 'firma', 'name', 'company', 'company name'), ('adresse', 'anschrift', 'address', 'postal address'), ('e-mail', 'email', 'e-mail-adresse', 'email address', 'e-mail address')]
    try:
        columns = [next(i for i, h in enumerate(headers) if h in group) for group in aliases]
    except StopIteration:
        raise ValueError('Spalten benötigt: Firmenname, Adresse, E-Mail.')
    result = []
    for number, row in enumerate(rows[1:], 2):
        if not any(str(c).strip() for c in row):
            continue
        if len(row) <= max(columns):
            raise ValueError(f'Unvollständige Tabellenzeile {number}.')
        name, address, email = [clean(row[i]) for i in columns]
        if not name:
            raise ValueError(f'Firmenname fehlt in Zeile {number}.')
        emails = list(dict.fromkeys(e.lower() for e in EMAIL.findall(email)))
        match = re.match(r'^(.*?)[,\n]\s*(\d{5}\s+.+)$', address, re.S)
        if not match:
            match = re.match(r'^(.*?)[,\n]\s*(.+)$', address, re.S)
        result.append({'name': name, 'address': address, 'emails': emails,
            'street': match.group(1).strip() if match else address,
            'city': match.group(2).strip() if match else '', 'key': key(name)})
    return result


def inside(folder, filename, extensions):
    path = (folder / filename).resolve()
    if path.parent != folder or path.suffix.lower() not in extensions or not path.is_file():
        raise ValueError('Ungültige Dateiauswahl: ' + filename)
    return path


def atomic(path, data):
    temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(temp, path)


def dispatch(req):
    action = req['action']
    if action == 'defaults':
        return {'folder': str(ROOT / 'Data')}
    if action in ('keyStatus', 'saveKeys'):
        import credentials
        return {'keys': credentials.status() if action == 'keyStatus' else credentials.save(req.get('keys', {}))}
    if action in ('checkGemini', 'checkOpenAI'):
        import gemini, openai_search
        return (gemini if action == 'checkGemini' else openai_search).check()
    if action == 'modelCatalog':
        import model_catalog
        return model_catalog.read()
    if action == 'checkCLI':
        import cli_search
        if req.get('provider') not in ('codex', 'gemini-cli'):
            raise ValueError('Unknown CLI')
        return cli_search.check(req['provider'])
    if action == 'searchJobs':
        import gemini, openai_search, dedupe, cli_search
        handlers = {'gemini': gemini.search, 'openai': openai_search.search,
                    'codex': lambda r: cli_search.search(r, 'codex'),
                    'gemini-cli': lambda r: cli_search.search(r, 'gemini-cli')}
        from concurrent.futures import ThreadPoolExecutor, as_completed
        providers = req.get('providers', ['gemini'])
        if not isinstance(providers, list) or not providers or any(p not in handlers for p in providers):
            raise ValueError('Mindestens eine KI auswählen / Select at least one AI')
        folder = Path(req['folder']).resolve(strict=True)
        state_dir = folder / 'Bewerbungskatapult'
        state_dir.mkdir(exist_ok=True)
        token = uuid.uuid4().hex
        results, errors = {}, []
        with ThreadPoolExecutor(max_workers=4) as executor:
            jobs = {executor.submit(handlers[provider], req): provider for provider in dict.fromkeys(providers)}
            for future in as_completed(jobs):
                provider = jobs[future]
                try:
                    result = dict(future.result())
                    table = state_dir / (token + '-' + provider + '.md')
                    table.write_text(result['table'], encoding='utf-8')
                    result['rows'] = [{**r, 'providers': [provider]} for r in companies(table)]
                    results[provider] = result
                except Exception as exc:
                    errors.append(provider + ': ' + str(exc))
        if not results:
            raise ValueError(' | '.join(errors))
        ordered = [results[p] for p in handlers if p in results]
        raw_rows = [r for result in ordered for r in result['rows']]
        rows = dedupe.merge(raw_rows)
        result = {'rows': rows, 'duplicates': len(raw_rows) - len(rows), 'errors': errors,
                  'text': '\n\n'.join(p.upper() + '\n' + results[p]['text'] for p in handlers if p in results),
                  'sources': [source for result in ordered for source in result['sources']],
                  'suggestions': results.get('gemini', {}).get('suggestions', '')}
        atomic(state_dir / ('search-' + token + '.json'), result)
        return {**result, 'token': token}
    if action == 'sound':
        import winsound
        winsound.MessageBeep(winsound.MB_OK)
        return {}
    folder = Path(req['folder']).resolve(strict=True)
    if not folder.is_dir():
        raise ValueError('Datenordner nicht gefunden.')
    if action == 'files':
        return {'files': sorted(p.name for p in folder.iterdir() if p.is_file())}
    state_dir = folder / 'Bewerbungskatapult'
    state_dir.mkdir(exist_ok=True)
    lock = state_dir / '.lock'
    with lock.open('a+b') as handle:
        import msvcrt
        handle.seek(0)
        if handle.read(1) == b'':
            handle.write(b'0'); handle.flush()
        handle.seek(0)
        try:
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            raise ValueError('Ein anderer Vorgang arbeitet gerade in diesem Ordner.')
        try:
            return locked(req, folder, state_dir)
        finally:
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)


def locked(req, folder, state_dir):
    action = req['action']
    if action in ('appendSearch', 'dedupeList'):
        import dedupe
        incoming = []
        if action == 'appendSearch':
            token = req.get('token', '')
            if not re.fullmatch('[a-f0-9]{32}', token):
                raise ValueError('Ungültiger Auftrag / Invalid request')
            result = json.loads((state_dir / ('search-' + token + '.json')).read_text(encoding='utf-8'))
            selected = set(req.get('selected', []))
            incoming = [r for r in result['rows'] if r['key'] in selected and r['emails'] and r['address']]
        destination = folder / 'ApplicationList.MD'
        existing = companies(destination) if destination.exists() else []
        old = textfile(destination) if destination.exists() else ''
        if old.strip() and not old.lstrip().startswith('|'):
            raise ValueError('Zieldatei ist keine Markdown-Tabelle / Target is not a Markdown table')
        baseline = dedupe.merge(existing)
        if action == 'dedupeList' and len(baseline) == len(existing):
            return {'added': 0, 'removed': 0, 'filename': destination.name}
        merged = dedupe.merge([*existing, *incoming])
        content = '| Firmenname | Adresse | E-Mail |\n| --- | --- | --- |\n'
        for row in merged:
            values = [row['name'], row['address'], ' / '.join(row['emails'])]
            content += '| ' + ' | '.join(v.replace('|', '\\|').replace('\n', ' ').replace('\r', ' ') for v in values) + ' |\n'
        if (existing or incoming) and content != old:
            if destination.exists():
                destination.with_name(destination.name + '.bak').write_bytes(destination.read_bytes())
            temporary = destination.with_name(destination.name + '.tmp')
            temporary.write_text(content, encoding='utf-8')
            os.replace(temporary, destination)
        return {'added': max(0, len(merged)-len(baseline)), 'removed': len(existing)-len(baseline), 'filename': destination.name}
    journal_path = state_dir / 'journal.json'
    journal = json.loads(journal_path.read_text(encoding='utf-8')) if journal_path.exists() else {}
    if action == 'preview':
        source = inside(folder, req['list'], ('.txt', '.md', '.csv', '.xls', '.xlsx', '.ods'))
        finished = inside(folder, req['finished'], ('.txt', '.md', '.csv', '.xls', '.xlsx', '.ods'))
        template = inside(folder, req['template'], ('.doc', '.docx', '.odt'))
        mail = textfile(inside(folder, req['mail'], ('.txt', '.md'))).replace('\r\n', '\n')
        lines = mail.split('\n')
        if len(lines) < 3 or not lines[0].strip() or lines[1].strip() or not '\n'.join(lines[2:]).strip():
            raise ValueError('Maildatei: Betreff, Leerzeile, danach Anschreiben erforderlich.')
        done = {c['key'] for c in companies(finished)}
        seen, rows = set(), []
        for company in companies(source):
            k = company['key']
            status = ('Bereits bearbeitet' if k in done else
                      'Bereits gespeichert' if journal.get(k, {}).get('status') == 'saved' else
                      'Unklarer früherer Vorgang – Entwürfe prüfen' if k in journal else
                      'Doppelte Firma' if k in seen else
                      'Keine E-Mail-Adresse' if not company['emails'] else
                      'Adresse fehlt' if not company['address'] else 'Bereit')
            seen.add(k)
            rows.append({**company, 'status': status})
        token = uuid.uuid4().hex
        job = {'rows': rows, 'template': str(template), 'finished': str(finished),
               'subject': lines[0].strip(), 'body': '\n'.join(lines[2:]).strip(),
               'hash': hashlib.sha256(template.read_bytes()).hexdigest()}
        atomic(state_dir / (token + '.json'), job)
        return {**job, 'token': token}
    token = req.get('token', '')
    if not re.fullmatch('[a-f0-9]{32}', token):
        raise ValueError('Ungültiger Auftrag.')
    job = json.loads((state_dir / (token + '.json')).read_text(encoding='utf-8'))
    company = next(c for c in job['rows'] if c['key'] == req['key'] and c['status'] == 'Bereit')
    k = company['key']
    pdf = state_dir / (token + '-' + hashlib.sha256(k.encode()).hexdigest()[:12] + '.pdf')
    if action == 'generate':
        if k in journal or k in {c['key'] for c in companies(Path(job['finished']))}:
            raise ValueError('Firma wurde inzwischen bearbeitet oder muss geprüft werden.')
        if hashlib.sha256(Path(job['template']).read_bytes()).hexdigest() != job['hash']:
            raise ValueError('Vorlage wurde verändert. Bitte Vorschau neu laden.')
        office({'kind': 'pdf', 'source': job['template'], 'target': str(pdf), 'values': company})
        if not pdf.read_bytes().startswith(b'%PDF-'):
            raise ValueError('PDF-Erstellung fehlgeschlagen.')
        return {'size': pdf.stat().st_size, 'name': 'Bewerbung_' + re.sub(r'[^\w -]', '_', company['name']) + '.pdf'}
    if action == 'chunk':
        offset = int(req['offset'])
        if offset < 0:
            raise ValueError('Ungültiger Dateiabschnitt.')
        with pdf.open('rb') as stream:
            stream.seek(offset)
            return {'data': base64.b64encode(stream.read(384 * 1024)).decode('ascii')}
    if action == 'reserve':
        if k in journal or k in {c['key'] for c in companies(Path(job['finished']))}:
            raise ValueError('Firma wurde inzwischen bearbeitet.')
        journal[k] = {'status': 'pending', 'token': token, 'name': company['name']}
        atomic(journal_path, journal)
        return {}
    if action == 'commit':
        if journal.get(k, {}).get('token') != token:
            raise ValueError('Reservierung fehlt.')
        journal[k] = {**journal[k], 'status': 'saved', 'drafts': req.get('drafts', [])}
        atomic(journal_path, journal)
        # Keep the original format; spreadsheets are not silently rewritten.
        finished = Path(job['finished'])
        if finished.suffix.lower() in ('.xls', '.xlsx', '.ods'):
            return {'warning': 'Fertig-Liste ist eine Tabelle: Erfolg im journal.json gespeichert; bitte Liste manuell ergänzen.'}
        old = textfile(finished)
        if k not in {c['key'] for c in companies(finished)}:
            backup = finished.with_name(finished.name + '.bak')
            if not backup.exists():
                backup.write_bytes(finished.read_bytes())
            values = [company['name'], company['address'], ' / '.join(company['emails'])]
            if old.lstrip().startswith('|'):
                extra = '| ' + ' | '.join(v.replace('|', '\\|').replace('\n', ' ') for v in values) + ' |\n'
            else:
                dialect = csv.Sniffer().sniff(old[:8192], delimiters=';,\t')
                headers = next(csv.reader(io.StringIO(old), dialect))
                mapping = {'firmenname': values[0], 'firma': values[0], 'name': values[0],
                           'company': values[0], 'company name': values[0], 'postal address': values[1],
                           'email address': values[2], 'e-mail address': values[2],
                           'adresse': values[1], 'anschrift': values[1], 'address': values[1],
                           'e-mail': values[2], 'email': values[2], 'e-mail-adresse': values[2]}
                out = io.StringIO()
                csv.writer(out, dialect).writerow([mapping.get(key(clean(h)), '') for h in headers])
                extra = out.getvalue()
            temp = finished.with_name(finished.name + '.tmp')
            temp.write_text(old.rstrip('\r\n') + '\n' + extra, encoding='utf-8-sig')
            os.replace(temp, finished)
        return {}
    raise ValueError('Unbekannte Aktion.')


def main():
    if os.name == 'nt':
        import msvcrt
        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    header = sys.stdin.buffer.read(4)
    if len(header) != 4:
        return
    size = struct.unpack('<I', header)[0]
    try:
        if size > 1024 * 1024:
            raise ValueError('Anfrage zu groß.')
        request = json.loads(sys.stdin.buffer.read(size))
        result = {'ok': True, **dispatch(request)}
    except Exception as exc:
        result = {'ok': False, 'error': str(exc)}
    output = json.dumps(result, ensure_ascii=False).encode('utf-8')
    sys.stdout.buffer.write(struct.pack('<I', len(output)) + output)
    sys.stdout.buffer.flush()


if __name__ == '__main__':
    main()
