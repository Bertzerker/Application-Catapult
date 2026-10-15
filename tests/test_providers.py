import json
import io
import urllib.error
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'native'))
import credentials, dedupe, gemini, openai_search, host


def row(name, address='Testweg 1, 12345 Essen', emails=None):
    return {'name': name, 'key': host.key(name), 'address': address, 'emails': emails or ['jobs@example.org']}


class ProviderTests(unittest.TestCase):
    def test_model_display_names(self):
        for value in ['Gemini 2.5 Pro', 'gemini-2.5-pro', '  GEMINI 2.5 PRO  ', 'models/gemini-2.5-pro', '2.5 pro']:
            self.assertEqual(gemini.normalize_model(value), 'gemini-2.5-pro')
        with self.assertRaises(ValueError): gemini.normalize_model('../../invalid')

    def test_keys_preserve_other_provider_and_do_not_return_secret(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(credentials, 'ROOT', Path(directory)):
            credentials.save({'gemini': 'dummy-gemini-key-12345'})
            result = credentials.save({'openai': 'dummy-openai-key-12345', 'gemini': ''})
            self.assertEqual(credentials.read('gemini'), 'dummy-gemini-key-12345')
            self.assertEqual(credentials.read('openai'), 'dummy-openai-key-12345')
            self.assertEqual(result, {'gemini': True, 'openai': True})
            with self.assertRaises(ValueError): credentials.save({'gemini': 'bad\nINJECT=x'})
            self.assertEqual(credentials.read('gemini'), 'dummy-gemini-key-12345')

    def test_merge_preserves_emails_and_distinct_companies(self):
        a = row('Example GmbH', emails=['one@example.org'])
        b = row('EXAMPLE GmbH.', emails=['two@example.org'])
        c = row('Other Firm')
        merged = dedupe.merge([a, b, c])
        self.assertEqual(len(merged), 2)
        self.assertEqual(merged[0]['emails'], ['one@example.org','two@example.org'])
        self.assertFalse(dedupe.same(row('Alpha'), row('Beta')))
        # Shared address alone and shared email alone must not merge unrelated records.
        self.assertFalse(dedupe.same(row('Alpha', emails=['a@example.org']), row('Beta', emails=['b@example.org'])))

    def test_existing_file_cleanup_and_backup(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory); path = folder / 'ApplicationList.json'
            original = '[{"name": "Example GmbH", "address": "Street 1", "emails": ["a@example.org"]}, {"name": "EXAMPLE GmbH.", "address": "Street 1", "emails": ["b@example.org"]}]'
            path.write_text(original, encoding='utf-8')
            result = host.dispatch({'action': 'dedupeList', 'folder': directory})
            self.assertEqual(result['removed'], 1)
            self.assertEqual(path.with_name(path.name+'.bak').read_text(encoding='utf-8'), original)
            self.assertEqual(host.companies(path)[0]['emails'], ['a@example.org','b@example.org'])
            self.assertEqual(host.dispatch({'action':'dedupeList','folder':directory})['removed'], 0)

    def test_one_provider_failure_retains_other_results(self):
        answer = {'table': '| Firmenname | Adresse | E-Mail |\n| --- | --- | --- |\n| Example | Street 1 | a@example.org |\n',
                  'sources': [{'uri':'https://example.org/jobs','title':'Jobs'}], 'text':'Result', 'suggestions':''}
        with tempfile.TemporaryDirectory() as directory, patch.object(gemini,'search',side_effect=ValueError('Gemini HTTP 429')), patch.object(openai_search,'search',return_value=answer):
            result = host.dispatch({'action':'searchJobs','folder':directory,'providers':['gemini','openai']})
            self.assertEqual(len(result['rows']),1)
            self.assertEqual(result['rows'][0]['providers'],['openai'])
            self.assertIn('429',result['errors'][0])

    def test_single_provider_and_dual_provider_deduplication(self):
        answer = {'table': '| Firmenname | Adresse | E-Mail |\n| --- | --- | --- |\n| Example | Street 1 | a@example.org |\n',
                  'sources': [{'uri':'https://example.org/jobs','title':'Jobs'}], 'text':'Result', 'suggestions':''}
        with tempfile.TemporaryDirectory() as directory, patch.object(gemini,'search',return_value=answer) as g, patch.object(openai_search,'search',return_value=answer) as o:
            result = host.dispatch({'action':'searchJobs','folder':directory,'providers':['gemini']})
            o.assert_not_called()
            result = host.dispatch({'action':'searchJobs','folder':directory,'providers':['gemini','openai']})
            self.assertEqual(len(result['rows']),1)
            self.assertEqual(result['duplicates'],1)
            self.assertEqual(result['rows'][0]['providers'],['gemini','openai'])

    def test_openai_payload_and_citations(self):
        response = {'status':'completed','output':[{'type':'message','content':[{'type':'output_text',
            'text':'| Firmenname | Adresse | E-Mail |\n| --- | --- | --- |\n| Example | Street 1 | a@example.org |',
            'annotations':[{'type':'url_citation','url':'https://example.org/jobs','title':'Jobs'}]}]}]}
        with patch.object(openai_search, 'api', return_value=response) as call:
            result = openai_search.search({'city':'Essen','role':'Developer'})
            self.assertEqual(result['sources'][0]['uri'],'https://example.org/jobs')
            payload=call.call_args.args[1]
            self.assertFalse(payload['store'])
            self.assertEqual(payload['tools'],[{'type':'web_search'}])

    def test_quota_error_is_distinct_and_redacted(self):
        body = json.dumps({'error': {'code': 'insufficient_quota', 'message': 'private-detail-not-for-output'}}).encode()
        error = urllib.error.HTTPError('https://api.openai.com/v1/responses', 429, 'Limit', {}, io.BytesIO(body))
        with patch.object(credentials, 'read', return_value='dummy-openai-key'), patch.object(openai_search.urllib.request, 'urlopen', side_effect=error):
            with self.assertRaises(ValueError) as caught:
                openai_search.api('responses', {})
            self.assertIn('API-Guthaben', str(caught.exception))
            self.assertNotIn('private-detail', str(caught.exception))

if __name__ == '__main__': unittest.main()
