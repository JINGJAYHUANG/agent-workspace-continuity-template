from __future__ import annotations


def parse_note(value: str) -> dict[str, object]:
    """Parse a synthetic note with ``title: body`` syntax."""
    title, separator, body = value.partition(":")
    if not separator or not title.strip() or not body.strip():
        raise ValueError("note must use non-empty 'title: body' syntax")
    words = body.strip().split()
    return {"title": title.strip(), "body": body.strip(), "word_count": len(words)}
