"""Exercise the real XLS/XLSX/ODS import through an isolated LibreOffice profile."""
from pathlib import Path
import subprocess
import sys
import tempfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'native'))
import host

out = ROOT / 'tests' / 'output' / 'sheets'
out.mkdir(exist_ok=True)
source = out / 'firmen.csv'
source.write_text('Firmenname,Adresse,E-Mail\nTestfirma,"Testweg 4, 12345 Testort",a@example.org / b@example.org\n', encoding='utf-8')
program = next(p for p in Path(sys.executable).parents if (p / 'soffice.exe').is_file())
for fmt in ('xls:MS Excel 97', 'xlsx:Calc MS Excel 2007 XML', 'ods:calc8'):
    with tempfile.TemporaryDirectory(prefix='bewerbung-sheet-test-') as profile:
        subprocess.run([str(program / 'soffice.com'), '-env:UserInstallation=' + Path(profile).as_uri(),
            '--headless', '--convert-to', fmt, '--outdir', str(out), str(source)],
            check=True, timeout=90, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
    target = source.with_suffix('.' + fmt.split(':')[0])
    assert target.exists(), fmt
    rows = host.companies(target)
    assert rows[0]['name'] == 'Testfirma', rows
    assert rows[0]['city'] == '12345 Testort', rows
    assert len(rows[0]['emails']) == 2, rows
    print(target.suffix, 'OK')
