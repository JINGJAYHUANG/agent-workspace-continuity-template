#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import hashlib
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EPOCH = int(os.environ.get("SOURCE_DATE_EPOCH", "1767225600"))  # 2026-01-01T00:00:00Z


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean_build_state() -> None:
    shutil.rmtree(ROOT / "build", ignore_errors=True)
    for path in (ROOT / "src").glob("*.egg-info"):
        shutil.rmtree(path, ignore_errors=True)
    for path in ROOT.rglob("__pycache__"):
        if ".git" not in path.parts:
            shutil.rmtree(path, ignore_errors=True)
    for path in ROOT.rglob("*.pyc"):
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def command(args: list[str], env: dict[str, str]) -> None:
    result = subprocess.run(args, cwd=ROOT, env=env, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(args)}\n{result.stdout}\n{result.stderr}")


def normalize_wheel(path: Path) -> None:
    entries: list[tuple[str, bytes, int, bool]] = []
    with zipfile.ZipFile(path, "r") as source:
        for info in source.infolist():
            mode = (info.external_attr >> 16) & 0o7777
            entries.append((info.filename, source.read(info.filename), mode, info.is_dir()))
    timestamp = time.gmtime(EPOCH)[:6]
    temp = path.with_suffix(path.suffix + ".tmp")
    with zipfile.ZipFile(temp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as target:
        for name, data, original_mode, is_dir in sorted(entries):
            info = zipfile.ZipInfo(name, date_time=timestamp)
            info.create_system = 3
            mode = (0o755 if is_dir else (0o755 if original_mode & 0o111 else 0o644))
            info.external_attr = (mode & 0xFFFF) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            info.extra = b""
            info.comment = b""
            target.writestr(info, data)
    temp.replace(path)


def normalize_sdist(path: Path) -> None:
    entries: list[tuple[tarfile.TarInfo, bytes | None]] = []
    with tarfile.open(path, "r:gz") as source:
        for member in source.getmembers():
            data = None
            if member.isfile():
                extracted = source.extractfile(member)
                data = extracted.read() if extracted else b""
            entries.append((member, data))
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=EPOCH) as zipped:
            with tarfile.open(fileobj=zipped, mode="w", format=tarfile.GNU_FORMAT) as target:
                for original, data in sorted(entries, key=lambda item: item[0].name):
                    info = tarfile.TarInfo(original.name)
                    info.type = original.type
                    info.linkname = original.linkname
                    info.mtime = EPOCH
                    info.uid = 0
                    info.gid = 0
                    info.uname = ""
                    info.gname = ""
                    info.mode = 0o755 if original.isdir() or original.mode & 0o111 else 0o644
                    if data is not None:
                        info.size = len(data)
                        import io
                        target.addfile(info, io.BytesIO(data))
                    else:
                        info.size = 0
                        target.addfile(info)
    temp.replace(path)


def build_once(output: Path) -> dict[str, str]:
    output.mkdir(parents=True, exist_ok=True)
    clean_build_state()
    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = str(EPOCH)
    env["PYTHONHASHSEED"] = "0"
    command([sys.executable, "setup.py", "--quiet", "sdist", "--dist-dir", str(output)], env)
    command([sys.executable, "setup.py", "--quiet", "bdist_wheel", "--dist-dir", str(output)], env)
    wheel = next(output.glob("*.whl"))
    sdist = next(output.glob("*.tar.gz"))
    normalize_wheel(wheel)
    normalize_sdist(sdist)
    return {path.name: sha256(path) for path in sorted(output.iterdir()) if path.is_file()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="dist")
    parser.add_argument("--no-repro-check", action="store_true")
    args = parser.parse_args()
    final = Path(args.output)
    if not final.is_absolute():
        final = ROOT / final
    shutil.rmtree(final, ignore_errors=True)
    final.mkdir(parents=True)

    with tempfile.TemporaryDirectory(prefix="awc-build-a-") as first_raw:
        first = Path(first_raw)
        hashes_a = build_once(first)
        if not args.no_repro_check:
            with tempfile.TemporaryDirectory(prefix="awc-build-b-") as second_raw:
                second = Path(second_raw)
                hashes_b = build_once(second)
                if hashes_a != hashes_b:
                    raise RuntimeError(f"non-reproducible build\nfirst={hashes_a}\nsecond={hashes_b}")
        for artifact in first.iterdir():
            if artifact.is_file():
                shutil.copy2(artifact, final / artifact.name)

    clean_build_state()
    print("Reproducible artifacts:")
    for name, digest in sorted(hashes_a.items()):
        print(f"{digest}  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
