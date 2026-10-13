"""Deterministic duplicate matching. No API calls and no fuzzy name guesses."""
import re
import unicodedata
from copy import deepcopy


def normalized(value):
    value = unicodedata.normalize('NFKC', value).casefold().replace('&', 'und')
    return re.sub(r'[^\w]', '', value)


def same(a, b):
    an, bn = normalized(a['name']), normalized(b['name'])
    if an and an == bn: return True
    # Alternate legal suffixes only match when the street address also agrees.
    suffix = r'(?:gmbh|ag|se|ltd|limited|inc|llc)$'
    if re.sub(suffix, '', an) == re.sub(suffix, '', bn) and normalized(a['address']) and normalized(a['address']) == normalized(b['address']):
        return True
    # Shared mailboxes and buildings may serve several distinct companies.
    return False


def merge(rows):
    result = []
    for row in rows:
        item = deepcopy(row)
        matches = [r for r in result if same(r, item)]
        if not matches:
            result.append(item); continue
        keep = matches[0]
        for value in [item, *matches[1:]]:
            for field in ('emails', 'providers'):
                keep[field] = list(dict.fromkeys(keep.get(field, []) + value.get(field, [])))
            if not keep.get('address'): keep['address'] = value['address']
        for duplicate in matches[1:]: result.remove(duplicate)
    return result
