import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'native'))
import host
import gemini


class SearchTests(unittest.TestCase):
    def test_english_file(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'English.csv'
            path.write_text('Company Name,Postal Address,Email Address\nExample,"10 Test Street, London SW1A 1AA",jobs@example.org\n', encoding='utf-8')
            row = host.companies_from_table(path)[0]
            self.assertEqual(row['name'], 'Example')
            self.assertEqual(row['street'], '10 Test Street')
            self.assertEqual(row['city'], 'London SW1A 1AA')

    def test_append_selected_deduplicate_and_preserve(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp); state = folder / 'Bewerbungskatapult'; state.mkdir()
            token = 'a' * 32
            result = {'rows': [{'key': 'example', 'name': 'Example', 'address': 'Street 1, City', 'emails': ['jobs@example.org']},
                               {'key': 'unselected', 'name': 'Unselected', 'address': 'Street 2', 'emails': ['other@example.org']}]}
            (state / ('search-' + token + '.json')).write_text(json.dumps(result), encoding='utf-8')
            req = {'action': 'appendSearch', 'folder': temp, 'token': token, 'selected': ['example']}
            self.assertEqual(host.dispatch(req)['added'], 1)
            first = (folder / 'ApplicationList.json').read_bytes()
            self.assertEqual(host.dispatch(req)['added'], 0)
            self.assertEqual((folder / 'ApplicationList.json').read_bytes(), first)
            self.assertEqual(len(host.companies(folder / 'ApplicationList.json')), 1)

    def test_no_grounding_rejected(self):
        with patch.object(gemini, 'api', return_value={'candidates': [{'finishReason': 'STOP', 'content': {'parts': [{'text': '| Firmenname | Adresse | E-Mail |'}]}}]}):
            with self.assertRaisesRegex(ValueError, 'Keine Webquellen'):
                gemini.search({'city': 'Essen', 'role': 'Developer'})

    def test_grounded_search_and_payload(self):
        table = '| Firmenname | Adresse | E-Mail |\n| --- | --- | --- |\n| Example | Street 1 | jobs@example.org |\n\nSOURCES\nExample: https://example.org/jobs'
        response = {'candidates': [{'finishReason': 'STOP', 'content': {'parts': [{'text': table}]},
            'groundingMetadata': {'groundingChunks': [{'web': {'uri': 'https://example.org/jobs', 'title': 'Jobs'}}]}}]}
        with patch.object(gemini, 'api', return_value=response) as call:
            result = gemini.search({'city': 'Essen', 'role': 'Developer', 'language': 'en'})
            self.assertEqual(len(result['sources']), 1)
            self.assertIn('Example', result['table'])
            payload = call.call_args.args[1]
            self.assertEqual(payload['tools'], [{'google_search': {}}])
            self.assertIn('currently advertised vacancies', payload['contents'][0]['parts'][0]['text'])


if __name__ == '__main__': unittest.main()
