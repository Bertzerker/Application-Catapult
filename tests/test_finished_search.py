import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'native'))
import host, gemini


class FinishedSearchTests(unittest.TestCase):
    def test_search_excludes_existing_list_and_journal(self):
        import json
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder/'ApplicationsList.json').write_text('[{"name": "Existing", "address": "Road", "emails": ["a@example.org"]}]', encoding='utf-8')
            state = folder/'Bewerbungskatapult'; state.mkdir()
            (state/'journal.json').write_text(json.dumps({'saved': {'name': 'Saved', 'status': 'saved'}}))
            answer = {'table': '|Firmenname|Adresse|E-Mail|\n|---|---|---|\n|Existing|Road|a@example.org|\n|Saved|Road|a@example.org|\n|New|Road|a@example.org|\n', 'text':'results', 'sources':[], 'suggestions':''}
            with patch.object(gemini, 'search', return_value=answer):
                result = host.dispatch({'action':'searchJobs','folder':directory,'providers':['gemini']})
            self.assertEqual([r['name'] for r in result['rows']], ['New'])
            self.assertEqual(result['excludedFinished'], 2)

    def test_empty_fields_and_search_filter(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder/'ApplicationFinished.json').write_text('[{"name": "Done GmbH", "address": "", "emails": []}]',encoding='utf-8')
            self.assertEqual(host.companies(folder/'ApplicationFinished.json')[0]['emails'], [])
            answer = {'table':'|Firmenname|Adresse|E-Mail|\n|-|-|-|\n|DONE GmbH|Road 1|a@example.org|\n|New GmbH|Road 2|b@example.org|\n',
                      'text':'Done GmbH and New GmbH', 'sources':[], 'suggestions':''}
            with patch.object(gemini,'search',return_value=answer):
                result=host.dispatch({'action':'searchJobs','folder':directory,'providers':['gemini']})
            self.assertEqual([r['name'] for r in result['rows']], ['New GmbH'])
            self.assertEqual(result['excludedFinished'],1)
            self.assertNotIn('DONE GmbH',result['text'])
            self.assertEqual(result['duplicates'],0)

    def test_selected_finished_file_and_invalid_path(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            (folder/'custom.json').write_text('[{"name": "Done", "address": "", "emails": []}]',encoding='utf-8')
            answer={'table':'|Firmenname|Adresse|E-Mail|\n|-|-|-|\n|Done|Road|a@example.org|\n','text':'Done','sources':[], 'suggestions':''}
            with patch.object(gemini,'search',return_value=answer) as search:
                result=host.dispatch({'action':'searchJobs','folder':directory,'providers':['gemini'],'finished':'custom.json'})
                self.assertEqual(result['rows'],[])
                with self.assertRaises(ValueError):
                    host.dispatch({'action':'searchJobs','folder':directory,'providers':['gemini'],'finished':'../outside.md'})
                self.assertEqual(search.call_count,1)
