"""Local key storage; public responses expose presence only."""
import os
from pathlib import Path
import re
import uuid
ROOT = Path(__file__).resolve().parents[1]
NAMES = {'gemini': 'GEMINI_API_KEY', 'openai': 'OPENAI_API_KEY'}


def read(provider):
    name = NAMES[provider]
    result = os.environ.get(name, '')
    path = ROOT / '.env.local'
    if path.exists():
        for line in path.read_text(encoding='utf-8-sig').splitlines():
            if line.strip().startswith(name + '='):
                result = line.split('=', 1)[1].strip().strip('\"\'')
    return result


def status():
    return {p: bool(read(p)) for p in NAMES}


def save(values):
    path = ROOT / '.env.local'
    if path.is_symlink():
        raise ValueError('Symlink als Schlüsseldatei nicht erlaubt / Key file must not be a symlink')
    import msvcrt
    with (ROOT / '.env.lock').open('a+b') as lock:
        lock.seek(0)
        if not lock.read(1): lock.write(b'0'); lock.flush()
        lock.seek(0)
        try:
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            raise ValueError('Schlüssel werden gerade gespeichert / Keys are being saved') from None
        try:
            return _save(values)
        finally:
            lock.seek(0); msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)


def _save(values):
    # Validate everything before changing either key. Empty fields preserve existing keys.
    updates = {}
    for provider, value in values.items():
        if provider not in NAMES or not isinstance(value, str):
            raise ValueError('Ungültige Schlüssel-Eingabe / Invalid key input')
        value = value.strip()
        if not value:
            continue
        if not re.fullmatch(r'[A-Za-z0-9._\-]{15,512}', value):
            raise ValueError('Schlüsselformat ungültig / Invalid key format')
        updates[NAMES[provider]] = value
    if not updates:
        return status()
    path = ROOT / '.env.local'
    lines = path.read_text(encoding='utf-8-sig').splitlines() if path.exists() else []
    lines = [line for line in lines if line.partition('=')[0].strip() not in updates]
    lines.extend(name + '=' + value for name, value in updates.items())
    temp = ROOT / ('.env.' + uuid.uuid4().hex + '.tmp')
    try:
        temp.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        os.replace(temp, path)
    finally:
        if temp.exists(): temp.unlink()
    return status()
