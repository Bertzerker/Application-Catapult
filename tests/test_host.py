import csv
import io
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'native'))
import host


class ParsingTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.data = Path(temporary.name)
        rows = ['| Firmenname | Adresse | E-Mail |', '| --- | --- | --- |']
        for i in range(8):
            name = 'Example | Team' if i == 5 else f'Example {i}'
            email = '' if i == 7 else f'jobs{i}@example.org'
            if i == 0: email += ' / contact@example.org'
            rows.append('| ' + name.replace('|', r'\|') + ' | Testweg 1, 45128 Essen | ' + email + ' |')
        (self.data / 'ApplicationList.MD').write_text('\n'.join(rows), encoding='utf-8')
        (self.data / 'ApplicationFinished.MD').write_text('\n'.join(rows[:2] + [f'| Old {i} | Old Street | old{i}@example.org |' for i in range(7)]), encoding='utf-8')
        (self.data / 'ApplicationMail.MD').write_text('Test subject\n\nTest body', encoding='utf-8')
        # Preview only hashes the file; this test never invokes document conversion.
        (self.data / 'ApplicationLetter.odt').write_bytes(b'synthetic preview fixture')

    def test_supplied_list(self):
        rows = host.companies(self.data / 'ApplicationList.MD')
        self.assertEqual(len(rows), 8)
        self.assertEqual(rows[0]['city'], '45128 Essen')
        self.assertEqual(len(rows[0]['emails']), 2)
        self.assertEqual(rows[5]['name'], 'Example | Team')
        self.assertEqual(rows[-1]['emails'], [])

    def test_csv_quotes_and_encoding(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'list.csv'
            path.write_bytes('Firmenname;Adresse;E-Mail\n"Müller; Partner";"Weg 2, 12345 Köln";"a@example.org / b@example.org"\n'.encode('cp1252'))
            row = host.companies(path)[0]
            self.assertEqual(row['name'], 'Müller; Partner')
            self.assertEqual(row['city'], '12345 Köln')
            self.assertEqual(len(row['emails']), 2)

    def test_native_protocol(self):
        data = json.dumps({'action': 'defaults'}).encode()
        result = subprocess.run([sys.executable, str(ROOT / 'native' / 'host.py')],
            input=struct.pack('<I', len(data)) + data, capture_output=True, check=True)
        size = struct.unpack('<I', result.stdout[:4])[0]
        self.assertEqual(size, len(result.stdout[4:]))
        self.assertTrue(json.loads(result.stdout[4:])['ok'])

    def test_workflow(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            for file in (self.data).iterdir():
                if file.is_file(): shutil.copy2(file, target / file.name)
            cfg = dict(folder=folder, list='ApplicationList.MD', finished='ApplicationFinished.MD',
                       template='ApplicationLetter.odt', mail='ApplicationMail.MD')
            preview = host.dispatch(dict(cfg, action='preview'))
            self.assertEqual(sum(r['status'] == 'Bereit' for r in preview['rows']), 7)
            row = preview['rows'][0]
            request = dict(folder=folder, token=preview['token'], key=row['key'])
            host.dispatch(dict(request, action='reserve'))
            with self.assertRaises(ValueError): host.dispatch(dict(request, action='reserve'))
            host.dispatch(dict(request, action='commit', drafts=[123]))
            host.dispatch(dict(request, action='commit', drafts=[123]))
            self.assertEqual(len(host.companies(target / 'ApplicationFinished.MD')), 8)
            refreshed = host.dispatch(dict(cfg, action='preview'))
            self.assertEqual(refreshed['rows'][0]['status'], 'Bereits bearbeitet')
            self.assertTrue((target / 'ApplicationFinished.MD.bak').exists())

    def test_path_escape(self):
        with self.assertRaises(ValueError):
            host.inside(self.data, '../Todo.txt', ('.txt',))

    def test_reordered_finished_csv(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            for file in (self.data).iterdir():
                if file.is_file(): shutil.copy2(file, target / file.name)
            finished = target / 'done.csv'
            finished.write_text('E-Mail;Firmenname;Adresse\nold@example.org;Alte Firma;Alter Weg\n', encoding='utf-8')
            cfg = dict(folder=folder, list='ApplicationList.MD', finished='done.csv',
                       template='ApplicationLetter.odt', mail='ApplicationMail.MD')
            preview = host.dispatch(dict(cfg, action='preview'))
            request = dict(folder=folder, token=preview['token'], key=preview['rows'][0]['key'])
            host.dispatch(dict(request, action='reserve'))
            host.dispatch(dict(request, action='commit', drafts=[123]))
            self.assertEqual(host.companies(finished)[-1]['name'], preview['rows'][0]['name'])


if __name__ == '__main__':
    unittest.main()
