import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'native'))
import cli_search, host, gemini, openai_search

ANSWER = '| Firmenname | Adresse | E-Mail |\n| --- | --- | --- |\n| Example | Street 1 | jobs@example.org |\nSOURCES\nhttps://example.org/jobs'


class CLITests(unittest.TestCase):
    def test_codex_requires_actual_search_and_completed_turn(self):
        events = [{'type':'item.completed','item':{'type':'agent_message','text':ANSWER}}, {'type':'turn.completed'}]
        with self.assertRaises(ValueError): cli_search.parse('codex', '\n'.join(map(json.dumps,events)))
        events.insert(0, {'type':'item.completed','item':{'type':'web_search'}})
        self.assertEqual(cli_search.parse('codex','\n'.join(map(json.dumps,events)))['sources'][0]['uri'], 'https://example.org/jobs')
        events[-1] = {'type':'turn.failed'}
        with self.assertRaises(ValueError): cli_search.parse('codex','\n'.join(map(json.dumps,events)))

    def test_gemini_stream_and_failure(self):
        events = [{'event':'step_update','step_update':{'state':'DONE','tool_name':'search_web','step_type':'tool'}},
                  {'event':'result','result':{'status':'SUCCESS','response':ANSWER}}]
        result = cli_search.parse('gemini-cli','\n'.join(map(json.dumps,events)))
        self.assertEqual(result['text'], ANSWER)
        events[-1]['result']['status'] = 'ERROR'
        with self.assertRaises(ValueError): cli_search.parse('gemini-cli','\n'.join(map(json.dumps,events)))

    def test_no_api_fallback_environment(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY':'dummy', 'GEMINI_API_KEY':'dummy', 'CODEX_API_KEY':'dummy'}):
            env = cli_search.environment()
        self.assertNotIn('OPENAI_API_KEY',env)
        self.assertNotIn('GEMINI_API_KEY',env)
        self.assertNotIn('CODEX_API_KEY',env)

    def test_antigravity_denied_access_is_actionable(self):
        event = {'event':'result','result':{'status':'SUCCESS','response':'','denied_actions':[{'action':'read_url'}]}}
        with self.assertRaisesRegex(ValueError, '/permissions'):
            cli_search.parse('gemini-cli',json.dumps(event))

    def test_four_providers_merge_and_partial_failure(self):
        answer={'table':ANSWER.split('SOURCES')[0], 'text':ANSWER,'sources':[], 'suggestions':''}
        with tempfile.TemporaryDirectory() as d, patch.object(gemini,'search',return_value=answer), patch.object(openai_search,'search',side_effect=ValueError('quota')), patch.object(cli_search,'search',return_value=answer) as cli:
            result=host.dispatch({'action':'searchJobs','folder':d,'providers':['codex','gemini-cli','gemini','openai']})
            self.assertEqual(cli.call_count,2)
            self.assertEqual(len(result['rows']),1)
            self.assertEqual(result['duplicates'],2)
            self.assertEqual(set(result['rows'][0]['providers']),{'codex','gemini-cli','gemini'})
            self.assertIn('quota',result['errors'][0])

    def test_cli_only_does_not_call_api(self):
        answer={'table':ANSWER.split('SOURCES')[0], 'text':ANSWER,'sources':[], 'suggestions':''}
        with tempfile.TemporaryDirectory() as d, patch.object(gemini,'search') as g, patch.object(openai_search,'search') as o, patch.object(cli_search,'search',return_value=answer):
            host.dispatch({'action':'searchJobs','folder':d,'providers':['codex']})
            g.assert_not_called(); o.assert_not_called()
