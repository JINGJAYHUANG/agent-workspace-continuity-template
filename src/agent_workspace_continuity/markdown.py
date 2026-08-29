from __future__ import annotations

import re
from dataclasses import dataclass

HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
BULLET = re.compile(r"^\s*(?:[-*+] |\d+[.)]\s+)(.+?)\s*$")
CHECKBOX = re.compile(r"^\s*[-*+]\s+\[[ xX]\]\s+(.+?)\s*$")


@dataclass(frozen=True, slots=True)
class Section:
    level: int
    title: str
    body: str


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def sections(text: str) -> list[Section]:
    lines = text.splitlines()
    heads: list[tuple[int, int, str]] = []
    for i, line in enumerate(lines):
        match = HEADING.match(line)
        if match:
            heads.append((i, len(match.group(1)), match.group(2).strip()))
    out: list[Section] = []
    for pos, (start, level, title) in enumerate(heads):
        end = len(lines)
        for nxt, nxt_level, _ in heads[pos + 1 :]:
            if nxt_level <= level:
                end = nxt
                break
        out.append(Section(level, title, "\n".join(lines[start + 1 : end]).strip()))
    return out


def find_section(text: str, *titles: str) -> Section | None:
    wanted = {normalize(t) for t in titles}
    return next((s for s in sections(text) if normalize(s.title) in wanted), None)


def section_items(text: str, *titles: str) -> list[str]:
    section = find_section(text, *titles)
    if section is None:
        return []
    out: list[str] = []
    in_fence = False
    for line in section.body.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or not stripped or stripped.startswith("|"):
            continue
        match = CHECKBOX.match(line) or BULLET.match(line)
        out.append((match.group(1) if match else stripped).strip())
    return out


def first_item(text: str, *titles: str) -> str | None:
    items = section_items(text, *titles)
    return items[0] if items else None
