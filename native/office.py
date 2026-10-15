"""Isolated LibreOffice process; uses the Python shipped with LibreOffice."""
import json
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
import uno


def prop(name, value):
    p = uno.createUnoStruct('com.sun.star.beans.PropertyValue')
    p.Name, p.Value = name, value
    return p


def execute(request):
    program = next(p for p in Path(sys.executable).parents if (p / 'soffice.exe').is_file())
    with tempfile.TemporaryDirectory(prefix='bewerbung-office-') as profile:
        pipe = 'bewerbung_' + uuid.uuid4().hex
        process = subprocess.Popen([
            str(program / 'soffice.exe'),
            '-env:UserInstallation=' + Path(profile).as_uri(), '--headless',
            '--norestore', '--nodefault', '--nofirststartwizard',
            '--accept=pipe,name=' + pipe + ';urp;StarOffice.ComponentContext'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        desktop = doc = None
        try:
            local = uno.getComponentContext()
            resolver = local.ServiceManager.createInstanceWithContext(
                'com.sun.star.bridge.UnoUrlResolver', local)
            for attempt in range(100):
                try:
                    ctx = resolver.resolve('uno:pipe,name=' + pipe + ';urp;StarOffice.ComponentContext')
                    break
                except Exception:
                    if process.poll() is not None:
                        raise RuntimeError('LibreOffice konnte nicht gestartet werden.')
                    time.sleep(.1)
            else:
                raise RuntimeError('Zeitüberschreitung beim Start von LibreOffice.')
            desktop = ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', ctx)
            source = 'private:factory/scalc' if request['kind'] == 'exportFinished' else Path(request['source']).as_uri()
            doc = desktop.loadComponentFromURL(source, '_blank', 0,
                (prop('Hidden', True), prop('ReadOnly', True), prop('MacroExecutionMode', 0),
                 prop('UpdateDocMode', 0)))
            if doc is None:
                raise ValueError('Dokument konnte nicht geöffnet werden.')
            if request['kind'] == 'exportFinished':
                sheet = doc.Sheets.getByIndex(0)
                sheet.Name = 'Bereits bearbeitet'
                rows = [['Firmenname', 'Adresse', 'E-Mail', 'Hinweise']]
                rows.extend([r['name'], r['address'], '; '.join(r['emails']), str(r.get('emailText', ''))]
                            for r in request['rows'])
                for y, row in enumerate(rows):
                    for x, value in enumerate(row):
                        # Explicit text prevents company data from becoming formulas.
                        sheet.getCellByPosition(x, y).String = value
                area = sheet.getCellRangeByPosition(0, 0, 3, len(rows)-1)
                area.CharFontName = 'Calibri'
                area.CharHeight = 11
                area.IsTextWrapped = True
                header = sheet.getCellRangeByPosition(0, 0, 3, 0)
                header.CellBackColor = 0x185F69
                header.CharColor = 0xFFFFFF
                header.CharWeight = 150.0
                for x, width in enumerate((6500, 8500, 9000, 8000)):
                    sheet.Columns.getByIndex(x).Width = width
                area.Rows.OptimalHeight = True
                doc.CurrentController.freezeAtPosition(0, 1)
                doc.storeToURL(Path(request['target']).as_uri(),
                    (prop('FilterName', 'Calc MS Excel 2007 XML'), prop('Overwrite', False)))
                return {'count': len(rows)-1}
            if request['kind'] == 'table':
                sheet = doc.Sheets.getByIndex(0)
                cursor = sheet.createCursor()
                cursor.gotoEndOfUsedArea(False)
                area = cursor.RangeAddress
                if area.EndRow > 50000 or area.EndColumn > 100:
                    raise ValueError('Tabelle zu groß (maximal 50001 Zeilen / 101 Spalten).')
                return {'rows': [[sheet.getCellByPosition(c, r).String
                    for c in range(area.EndColumn + 1)] for r in range(area.EndRow + 1)]}
            values = request['values']
            replacements = {
                '{{Company}}': values['name'], '{{CompanyName}}': values['name'],
                '{{Address}}': values['street'], '{{AddressLine2}}': values['city'],
                '^Company name$': values['name'], '^Address,$': values['street'], '^Address line 2$': values['city'],
                '{{Firmenname}}': values['name'], '{{Name}}': values['name'],
                '{{Adresse}}': values['street'], '{{Adresszusatz}}': values['city'],
                '{{Email}}': '; '.join(values['emails']), '{{E-Mail}}': '; '.join(values['emails']),
                '^Firmenname$': values['name'], '^Adresse,$': values['street'],
                '^Adresszusatz$': values['city']}
            counts = {}
            for old, new in replacements.items():
                search = doc.createSearchDescriptor()
                search.SearchString = old
                search.SearchRegularExpression = old.startswith('^')
                matches = doc.findAll(search)
                counts[old] = matches.Count
                for i in reversed(range(matches.Count)):
                    matches.getByIndex(i).String = new
            if not any(counts[k] for k in ('{{Company}}', '{{CompanyName}}', '^Company name$', '{{Firmenname}}', '{{Name}}', '^Firmenname$')):
                raise ValueError('Kein Firmenname-Platzhalter in der Vorlage gefunden.')
            if not any(counts[k] for k in ('{{Address}}', '^Address,$', '{{Adresse}}', '^Adresse,$')):
                raise ValueError('Kein Adress-Platzhalter in der Vorlage gefunden.')
            doc.storeToURL(Path(request['target']).as_uri(),
                (prop('FilterName', 'writer_pdf_Export'), prop('Overwrite', True)))
            return {'target': request['target'], 'replacements': counts}
        finally:
            if doc is not None:
                doc.close(True)
            if desktop is not None:
                desktop.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


if __name__ == '__main__':
    request = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    try:
        result = execute(request)
    except Exception as exc:
        result = {'error': str(exc)}
    Path(sys.argv[2]).write_text(json.dumps(result, ensure_ascii=False), encoding='utf-8')
