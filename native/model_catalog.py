"""User-editable model catalog; no execution or network access."""
import json
from pathlib import Path
import re

PATH = Path(__file__).resolve().parents[1] / 'models.json'


def read():
    try:
        data = json.loads(PATH.read_text(encoding='utf-8-sig'))
        result = {}
        for provider in ('codex', 'antigravity', 'gemini', 'openai'):
            values = data[provider]
            if not isinstance(values, list) or not 1 <= len(values) <= 100:
                raise ValueError()
            if any(not isinstance(v, str) or not (v == '' and provider == 'codex' or
                    re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9._:-]{0,100}', v)) for v in values):
                raise ValueError()
            result[provider] = list(dict.fromkeys(values))
        return {'models': result}
    except (OSError, ValueError, KeyError, TypeError):
        raise ValueError('models.json prüfen: vier nichtleere Modelllisten erforderlich / Check models.json: four nonempty model lists required') from None
