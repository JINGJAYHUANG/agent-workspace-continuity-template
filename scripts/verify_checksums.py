#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import sys
from pathlib import Path


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main() -> int:
    manifest = Path(sys.argv[1] if len(sys.argv) > 1 else "SHA256SUMS.txt").resolve()
    failed = False
    for row in manifest.read_text(encoding="utf-8").splitlines():
        if not row.strip():
            continue
        expected, name = row.split(None, 1)
        target = manifest.parent / name.strip()
        actual = digest(target)
        ok = actual == expected
        print(f"{'OK' if ok else 'FAIL'} {target.name}")
        failed |= not ok
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
