"""Real LibreOffice export test; synthetic data only."""
import sys
import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'native'))
import host

class ExcelExportTests(unittest.TestCase):
    def test_export_text_empty_list_and_source_preservation(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);source=folder/'done.json'
            rows=[{'name':'=1+1','address':'Müllerstraße 1, Köln\nHaus B','emails':['a@example.org','b@example.org'],'emailText':'Nicht öffentlich gelistet'}]
            host.atomic(source,rows);original=source.read_bytes()
            req={'action':'exportFinished','folder':directory,'finished':'done.json'}
            result=host.dispatch(req)
            target=Path(result['path'])
            self.assertEqual(target.parent,folder)
            self.assertEqual(result['count'],1)
            self.assertEqual(source.read_bytes(),original)
            with zipfile.ZipFile(target) as z:
                ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                sheet=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
                self.assertEqual(sheet.findall('.//m:f',ns),[])
                strings=ET.fromstring(z.read('xl/sharedStrings.xml'))
                values=[''.join(si.itertext()) for si in strings]
                for value in ['Firmenname','=1+1','Müllerstraße 1, Köln\nHaus B','a@example.org; b@example.org','Nicht öffentlich gelistet']:
                    self.assertIn(value,values)
            host.atomic(source,[])
            empty=host.dispatch(req)
            self.assertEqual(empty['count'],0)
            self.assertNotEqual(empty['path'],result['path'])
            self.assertTrue(target.exists())
            with self.assertRaises(ValueError):host.dispatch({**req,'finished':'../done.json'})

if __name__=='__main__':unittest.main()
