import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'native'))
import host

HEADER = '| Firmenname | Adresse | E-Mail |\n| --- | --- | --- |\n'
def table(path, names):
    path.write_text(json.dumps([{'name':n,'address':'Road 1','emails':['jobs@example.org']} for n in names]),encoding='utf-8')

class ImportGuardTests(unittest.TestCase):
    def test_save_mail_backup_validation_and_conflict(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'mail.md'
            original = 'Betreff\n\nGrüße'
            path.write_text(original, encoding='utf-8')
            old_bytes = path.read_bytes()
            request = {'action':'saveMail','folder':directory,'mail':'mail.md',
                       'originalText':original,'mailText':'Neu\n\nNeuer Text'}
            with self.assertRaises(ValueError):
                host.dispatch({**request,'mailText':'Ungültig'})
            self.assertEqual(path.read_bytes(),old_bytes)
            host.dispatch(request)
            self.assertEqual(host.dispatch({'action':'readMail','folder':directory,'mail':'mail.md'})['text'],'Neu\n\nNeuer Text')
            self.assertEqual(path.with_name('mail.md.bak').read_bytes(),old_bytes)
            with self.assertRaises(ValueError): host.dispatch(request)
            self.assertEqual(path.read_text(encoding='utf-8'),'Neu\n\nNeuer Text')
            with self.assertRaises(ValueError): host.dispatch({**request,'mail':'../outside.md'})

    def test_stale_results_finished_existing_journal_and_repeat(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory); state=folder/'Bewerbungskatapult'; state.mkdir()
            target=folder/'ApplicationsList.json'; table(target,['Existing'])
            table(folder/'ApplicationsFinished.json',['Done'])
            (state/'journal.json').write_text(json.dumps({'saved':{'name':'Saved','status':'saved'},'pending':{'name':'Pending','status':'pending'}}))
            token='a'*32
            rows=[{'name':n,'key':host.key(n),'address':'Road 1','emails':['new@example.org']} for n in ['Existing','Done','Saved','Pending','New']]
            (state/('search-'+token+'.json')).write_text(json.dumps({'rows':rows}))
            request={'action':'appendSearch','folder':directory,'token':token,'selected':[r['key'] for r in rows]}
            result=host.dispatch(request)
            self.assertEqual(result['added'],1)
            self.assertEqual([r['name'] for r in host.companies(target)],['Existing','New'])
            self.assertEqual(host.companies(target)[0]['emails'],['jobs@example.org'])
            original=target.read_bytes()
            self.assertEqual(host.dispatch(request)['added'],0)
            self.assertEqual(original,target.read_bytes())
            self.assertFalse((folder/'ApplicationList.json').exists())

    def test_selected_destination_and_edited_mail(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory); table(folder/'custom.json',['Ready']); table(folder/'done.json',[])
            (folder/'template.odt').write_bytes(b'test')
            (folder/'mail.txt').write_text('Original\n\nOriginal body')
            cfg={'folder':directory,'list':'custom.json','finished':'done.json','template':'template.odt','mail':'mail.txt'}
            self.assertEqual(host.dispatch({**cfg,'action':'readMail'})['text'],'Original\n\nOriginal body')
            job=host.dispatch({**cfg,'action':'preview','mailText':'Edited\n\nEdited body'})
            self.assertEqual((job['subject'],job['body']),('Edited','Edited body'))
            self.assertEqual((folder/'mail.txt').read_text(),'Original\n\nOriginal body')
            with self.assertRaises(ValueError): host.dispatch({**cfg,'action':'preview','mailText':'No blank line'})
            token='b'*32
            (folder/'Bewerbungskatapult'/('search-'+token+'.json')).write_text(json.dumps({'list':'custom.json','finished':'done.json','rows':[{'name':'Later','key':'later','address':'Road','emails':['a@example.org']}]}))
            table(folder/'done.json',['Later'])
            self.assertEqual(host.dispatch({'action':'appendSearch','folder':directory,'token':token,'selected':['later']})['added'],0)

if __name__=='__main__': unittest.main()
