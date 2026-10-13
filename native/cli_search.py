"""Account-authenticated local CLI search. Never falls back to a paid API key."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from gemini import search_prompt, result_table


def command(provider):
    name = 'codex' if provider == 'codex' else 'agy'
    found = shutil.which(name + '.exe') or shutil.which(name)
    if name == 'codex' and not found:
        candidates = list((Path(os.environ.get('LOCALAPPDATA', '')) / 'OpenAI/Codex/bin').glob('*/codex.exe'))
        if candidates:
            found = str(max(candidates, key=lambda p: p.stat().st_mtime))
    if found and Path(found).suffix.lower() == '.exe':
        return [found]
    if name == 'agy':
        for base in [Path(os.environ.get('LOCALAPPDATA', '')), Path.home() / 'AppData/Local']:
            binary = base / 'agy/bin/agy.exe'
            if binary.is_file():
                return [str(binary)]
    raise ValueError(name + ': Zusatzprogramm fehlt. Siehe Zusatzprogramme.md / CLI missing; see Zusatzprogramme.md')


def environment():
    return {k: v for k, v in os.environ.items() if k.upper() not in (
        'OPENAI_API_KEY', 'CODEX_API_KEY', 'GEMINI_API_KEY', 'GOOGLE_API_KEY',
        'GOOGLE_APPLICATION_CREDENTIALS', 'GOOGLE_GENAI_USE_VERTEXAI', 'GOOGLE_GENAI_USE_GCA')}


def run(args, cwd, prompt=None, timeout=300):
    try:
        result = subprocess.run(args, input=prompt, text=True, encoding='utf-8', errors='replace',
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, env=environment(),
            timeout=timeout, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    except subprocess.TimeoutExpired:
        raise ValueError('Zusatzprogramm: Zeitlimit erreicht / CLI timed out') from None
    except OSError:
        raise ValueError('Zusatzprogramm konnte nicht gestartet werden / Cannot start CLI') from None
    if result.returncode:
        # CLI diagnostics can contain credentials or local context: never forward verbatim.
        raise ValueError('Zusatzprogramm fehlgeschlagen (Code ' + str(result.returncode) +
            '). Anmeldung, Kontingent und Version prüfen / Check login, quota and version')
    return result.stdout


def check(provider):
    args = command(provider)
    with tempfile.TemporaryDirectory(prefix='bewerbung-check-') as directory:
        if provider == 'codex':
            # Some versions write login status to stderr.
            result = subprocess.run(args + ['login', 'status'], capture_output=True, text=True,
                encoding='utf-8', errors='replace', env=environment(), cwd=directory, timeout=20,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            if result.returncode or 'ChatGPT' not in result.stdout + result.stderr:
                raise ValueError('Codex: Bitte mit ChatGPT anmelden (codex login) / Sign in with ChatGPT')
        else:
            run(args + ['models'], directory, timeout=45)
    return {'available': True}


def parse(provider, output):
    events = [json.loads(line) for line in output.splitlines() if line.strip().startswith('{')]
    searched = False
    parts = []
    completed = False
    for event in events:
        if provider == 'codex':
            if event.get('type') in ('turn.failed', 'error'):
                raise ValueError('Codex: Suche fehlgeschlagen / Search failed')
            item = event.get('item', {})
            if event.get('type') == 'item.completed':
                searched |= item.get('type') == 'web_search'
                if item.get('type') == 'agent_message':
                    parts.append(item.get('text', ''))
            completed |= event.get('type') == 'turn.completed'
        else:
            step = event.get('step_update', {})
            if event.get('event') == 'step_update' and step.get('state') == 'DONE':
                searched |= step.get('tool_name') in ('search_web', 'google_web_search', 'web_search')
            if event.get('event') == 'result':
                result = event.get('result', {})
                if result.get('denied_actions') and not result.get('response'):
                    raise ValueError('Antigravity: Quellenabruf benötigt Freigabe. In agy /permissions prüfen / Source access needs approval in agy /permissions')
                completed = result.get('status') == 'SUCCESS'
                parts = [result.get('response', '')]
    text = '\n'.join(parts) if provider == 'codex' else ''.join(parts)
    urls = list(dict.fromkeys(re.findall(r'https://[^\s<>"\])]+', text)))
    if not completed or not searched or not urls:
        raise ValueError('Keine abgeschlossene Websuche mit Quellen / No completed web search with sources')
    return {'table': result_table(text), 'text': text,
            'sources': [{'uri': u, 'title': u} for u in urls], 'suggestions': ''}


def search(req, provider):
    prompt = search_prompt(req) + ' Use only web search and web fetch. Do not read local files or run commands.'
    check(provider)
    with tempfile.TemporaryDirectory(prefix='bewerbung-search-') as directory:
        args = command(provider)
        if provider == 'codex':
            args += ['--search', 'exec', '--ignore-user-config', '--sandbox', 'read-only',
                     '--skip-git-repo-check', '--ephemeral', '--json', '-c', 'features.shell_tool=false', '-']
            model = str(req.get('codexModel', '')).strip()
            if model:
                validate_model(model)
                args[-1:-1] = ['--model', model]
        else:
            model = str(req.get('antigravityModel', 'gemini-3.8-flash-high')).strip()
            validate_model(model)
            prompt += (' For this headless search use ONLY search_web, at most 6 searches. '
                       'Direct page reading (read_url_content) is not pre-approved; do not request it. '
                       'Use only facts supported by the web search results. Omit companies whose contact details '
                       'cannot be verified that way. Return the final table and source URLs after searching; '
                       'do not create a plan or ask questions. Fewer than 10 entries, including zero, are acceptable.')
            args += ['--print', prompt, '--output-format', 'stream-json',
                     '--disable-slash-commands', '--mode', 'plan', '--print-timeout', '240s', '--model', model]
            prompt = None
        return parse(provider, run(args, directory, prompt))


def validate_model(value):
    if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9._:-]{0,100}', value):
        raise ValueError('Ungültiger Modellname / Invalid model name')
