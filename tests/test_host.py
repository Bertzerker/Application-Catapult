import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'native'))
import host

class JsonListTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);self.folder=Path(tmp.name)
        self.rows=[{'name':'Müller | Partner','address':'Weg 2, 12345 Köln','emails':['a@example.org','b@example.org'],'emailText':'Kontakt über Personalabteilung'}, {'name':'Empty','address':'','emails':[]}]
        host.atomic(self.folder/'ApplicationList.json',self.rows)
        host.atomic(self.folder/'ApplicationFinished.json',[])
        (self.folder/'template.odt').write_bytes(b'preview fixture')
        (self.folder/'mail.txt').write_text('Betreff\n\nText',encoding='utf-8')
        self.cfg={'folder':str(self.folder),'list':'ApplicationList.json','finished':'ApplicationFinished.json','template':'template.odt','mail':'mail.txt'}

    def test_json_workflow_and_preserved_fields(self):
        rows=host.companies(self.folder/'ApplicationList.json')
        self.assertEqual(rows[0]['city'],'12345 Köln')
        job=host.dispatch({**self.cfg,'action':'preview'})
        self.assertEqual([r['status'] for r in job['rows']],['Bereit','Keine E-Mail-Adresse'])
        request={'folder':str(self.folder),'token':job['token'],'key':job['rows'][0]['key']}
        host.dispatch({**request,'action':'reserve'})
        host.dispatch({**request,'action':'commit','drafts':[123]})
        host.dispatch({**request,'action':'commit','drafts':[123]})
        data=json.loads((self.folder/'ApplicationFinished.json').read_text(encoding='utf-8'))
        self.assertEqual(data,[self.rows[0]])
        self.assertEqual(json.loads((self.folder/'ApplicationFinished.json.bak').read_text()),[])
        self.assertEqual([r['name'] for r in host.dispatch({**self.cfg,'action':'preview'})['rows']], ['Empty'])
        self.assertEqual(json.loads((self.folder/'ApplicationList.json').read_text(encoding='utf-8')), [self.rows[1]])

    def test_cleanup_recovers_saved_but_keeps_pending_and_new(self):
        extra = {'name':'Pending','address':'Road','emails':['p@example.org']}
        host.atomic(self.folder/'ApplicationList.json', [*self.rows, extra])
        state = self.folder/'Bewerbungskatapult'; state.mkdir()
        host.atomic(state/'journal.json', {host.key(self.rows[0]['name']):{'status':'saved'}, 'pending':{'status':'pending'}})
        result = host.dispatch({**self.cfg, 'action':'cleanupFinished'})
        self.assertEqual(result, {'removed':1, 'remaining':2})
        self.assertEqual([r['name'] for r in host.companies(self.folder/'ApplicationFinished.json')], [self.rows[0]['name']])
        job=host.dispatch({**self.cfg,'action':'preview'})
        self.assertEqual([r['status'] for r in job['rows']], ['Keine E-Mail-Adresse','Unklarer früherer Vorgang – Entwürfe prüfen'])
        self.assertEqual(host.dispatch({**self.cfg, 'action':'cleanupFinished'})['removed'],0)
        with self.assertRaises(ValueError): host.dispatch({**self.cfg,'action':'cleanupFinished','finished':'ApplicationList.json'})

    def test_bad_json_and_legacy_formats_rejected(self):
        path=self.folder/'bad.json'
        for value in [{},[{}],[{'name':'A','address':'Road','emails':'a@example.org'}],[{'name':'A','address':'Road','emails':['invalid']}]]:
            host.atomic(path,value)
            with self.assertRaises(ValueError):host.companies(path)
        path.write_text('{')
        with self.assertRaises(ValueError):host.companies(path)
        legacy=self.folder/'ApplicationList.MD';legacy.write_text('|Firmenname|Adresse|E-Mail|\n|---|---|---|')
        with self.assertRaises(ValueError):host.companies(legacy)
        with self.assertRaises(ValueError):host.dispatch({**self.cfg,'action':'preview','list':legacy.name})
        with self.assertRaises(ValueError):host.dispatch({**self.cfg,'action':'dedupeList','list':legacy.name})
        self.assertEqual(legacy.read_text(),'|Firmenname|Adresse|E-Mail|\n|---|---|---|')

    def test_path_escape(self):
        with self.assertRaises(ValueError):host.dispatch({**self.cfg,'action':'preview','list':'../outside.json'})

if __name__=='__main__':unittest.main()
