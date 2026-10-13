"""OpenAI Responses API web search; no conversation or document upload."""
import json
import re
import urllib.request
import urllib.error
import credentials
from gemini import search_prompt, result_table


def api(path, payload=None):
    key = credentials.read('openai')
    if not key:
        raise ValueError('OpenAI API-Schlüssel fehlt / OpenAI API key missing')
    request = urllib.request.Request('https://api.openai.com/v1/' + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        try:
            code = json.loads(error.read(65536)).get('error', {}).get('code')
        except (ValueError, AttributeError):
            code = None
        if code == 'insufficient_quota':
            raise ValueError('OpenAI HTTP 429: API-Guthaben oder Ausgabenlimit erschöpft / API credits or spending limit exhausted') from None
        if code == 'rate_limit_exceeded':
            raise ValueError('OpenAI HTTP 429: Anfragelimit erreicht; später versuchen / Request rate limit reached; try later') from None
        messages = {400: 'Anfrage/Modell nicht unterstützt / Request or model unsupported',
                    401: 'API-Schlüssel ungültig / Invalid API key', 403: 'Zugriff verweigert / Access denied',
                    404: 'Modell nicht verfügbar / Model unavailable', 429: 'Kontingent/Ratenlimit / Quota or rate limit'}
        raise ValueError(f'OpenAI HTTP {error.code}: ' + messages.get(error.code, 'Dienstfehler / Service error')) from None
    except (urllib.error.URLError, TimeoutError):
        raise ValueError('OpenAI nicht erreichbar / OpenAI connection failed') from None


def check():
    return {'available': True, 'models': [m['id'] for m in api('models').get('data', [])]}


def search(req):
    model = str(req.get('openaiModel', 'gpt-5-mini')).strip().lower().replace(' ', '-')
    if not re.fullmatch(r'gpt-[a-z0-9.\-]{1,80}', model):
        raise ValueError('Ungültiges OpenAI-Modell / Invalid OpenAI model')
    response = api('responses', {'model': model, 'input': search_prompt(req), 'store': False,
        'tools': [{'type': 'web_search'}], 'tool_choice': 'required'})
    if response.get('status') != 'completed':
        raise ValueError('OpenAI-Suche unvollständig / OpenAI search incomplete')
    text, sources = [], []
    for item in response.get('output', []):
        for part in item.get('content', []):
            if part.get('type') != 'output_text': continue
            text.append(part.get('text', ''))
            for annotation in part.get('annotations', []):
                if annotation.get('type') == 'url_citation' and annotation.get('url', '').startswith('https://'):
                    sources.append({'uri': annotation['url'], 'title': annotation.get('title', annotation['url'])})
    if not sources:
        raise ValueError('OpenAI: Keine Webquellen / No web sources')
    answer = '\n'.join(text)
    return {'table': result_table(answer), 'text': answer, 'sources': sources, 'suggestions': ''}
