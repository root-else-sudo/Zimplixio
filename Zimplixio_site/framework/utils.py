import json


def parse_claude_json(raw_text: str) -> dict:
    """Parse JSON from a Claude response, stripping any accidental markdown fences."""
    clean = raw_text.strip()
    if clean.startswith('```'):
        clean = clean.split('\n', 1)[1] if '\n' in clean else clean[3:]
    if clean.endswith('```'):
        clean = clean[:-3]
    return json.loads(clean.strip())
