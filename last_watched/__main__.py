from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Sequence

from .scanner import VideoFile, find_most_recent_videos


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m last_watched",
        description="Bir klasor agacindaki en son erisilen video dosyalarini gösterir.",
    )
    parser.add_argument("klasor", help="Taranacak kok klasör yolu")
    return parser


def _write_warning(path: Path, error: OSError) -> None:
    print(f"Uyari: Erisilemeyen oge atlandi: {path} ({error})", file=sys.stderr)


def _format_access_time(video: VideoFile) -> str:
    local_time = datetime.fromtimestamp(video.access_time_ns / 1_000_000_000).astimezone()
    return local_time.isoformat(timespec="seconds")


def _write_results(root: Path, videos: list[VideoFile]) -> None:

    multiple_videos = len(videos) > 1
    if multiple_videos:
        print(f"Son erisim zamani esit olan {len(videos)} video bulundu.")
        print(
            "Not: Windows bu dosyalarin LastAccessTime degerlerini ayni anda "
            "kaydettigi için kesin son bolum belirlenemiyor."
        )
    else:
        print("Son erisilen video")

    print(f"Erisim zamani: {_format_access_time(videos[0])}")
    print(f"Taranan klasor: {root}")

    for number, video in enumerate(videos, start=1):
        if multiple_videos:
            print(f"\n[{number}]")
        print(f"Dosya: {video.path.name}")
        print(f"Yol:   {video.path}")


def _validated_root(raw_path: str) -> Path:
    root = Path(raw_path).expanduser()
    try:
        if not root.exists():
            raise ValueError("Klasor bulunamadi")
        if not root.is_dir():
            raise ValueError("Verilen yol bir klasor degil")

        root = root.resolve()

        with os.scandir(root):
            pass
    except PermissionError as error:
        raise ValueError("Klasore erisilemiyor") from error
    except OSError as error:
        raise ValueError(f"Klasore erisilemiyor: {error}") from error
    return root


def main(argv: Sequence[str] | None = None) -> int:

    args = _parser().parse_args(argv)
    try:
        root = _validated_root(args.klasor)
    except ValueError as error:
        print(f"Hata: {error}: {args.klasor}", file=sys.stderr)
        return 2

    try:
        videos = find_most_recent_videos(root, warn=_write_warning)
    except OSError as error:
        print(f"Hata: Klasor taranamadi: {root} ({error})", file=sys.stderr)
        return 2

    if not videos:
        print(f"Hata: Bu klasor agacinda video dosyasi bulunamadi: {root}", file=sys.stderr)
        return 1

    _write_results(root, videos)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
