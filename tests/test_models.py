import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'native'))
import model_catalog, cli_search


class ModelTests(unittest.TestCase):
    def test_catalog_edit_add_remove_and_bad_file(self):
        with tempfile.TemporaryDirectory() as d, patch.object(model_catalog, 'PATH', Path(d)/'models.json'):
            data = {'codex':['', 'gpt-example'], 'antigravity':['gemini-example'], 'gemini':['gemini-example'], 'openai':['gpt-example']}
            model_catalog.PATH.write_text(json.dumps(data))
            self.assertEqual(model_catalog.read()['models']['codex'], ['', 'gpt-example'])
            data['codex'] = ['gpt-new']
            model_catalog.PATH.write_text(json.dumps(data))
            self.assertEqual(model_catalog.read()['models']['codex'], ['gpt-new'])
            data['codex'] = ['--evil']
            model_catalog.PATH.write_text(json.dumps(data))
            with self.assertRaises(ValueError): model_catalog.read()
            model_catalog.PATH.write_text('{invalid')
            with self.assertRaises(ValueError): model_catalog.read()

    def test_models_passed_as_individual_arguments(self):
        with patch.object(cli_search,'check'), patch.object(cli_search,'command',side_effect=lambda _: ['fake.exe']), patch.object(cli_search,'run',return_value='') as run, patch.object(cli_search,'parse',return_value={}):
            base={'city':'Essen','role':'IT','radius':25}
            cli_search.search({**base,'codexModel':'gpt-example'},'codex')
            args=run.call_args.args[0]
            self.assertEqual(args[args.index('--model')+1],'gpt-example')
            cli_search.search({**base,'antigravityModel':'gemini-example'},'gemini-cli')
            args=run.call_args.args[0]
            self.assertEqual(args[args.index('--model')+1],'gemini-example')
            self.assertIn('--print',args)
            self.assertNotIn('--dangerously-skip-permissions',args)
