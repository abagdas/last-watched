"""``python -m last_watched`` komutunun giriş noktası."""

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
        description="Bir klasör ağacındaki en son erişilen video dosyalarını gösterir.",
    )
    parser.add_argument("klasor", help="Taranacak kök klasör yolu")
    return parser


def _write_warning(path: Path, error: OSError) -> None:
    print(f"Uyarı: Erişilemeyen öğe atlandı: {path} ({error})", file=sys.stderr)


def _format_access_time(video: VideoFile) -> str:
    local_time = datetime.fromtimestamp(video.access_time_ns / 1_000_000_000).astimezone()
    return local_time.isoformat(timespec="seconds")


def _write_results(root: Path, videos: list[VideoFile]) -> None:
    """Sonuçları uzun dosya yolları için okunaklı, çok satırlı yazdırır."""

    multiple_videos = len(videos) > 1
    if multiple_videos:
        print(f"Son erişim zamanı eşit olan {len(videos)} video bulundu.")
        print(
            "Not: Windows bu dosyaların LastAccessTime değerlerini aynı anda "
            "kaydettiği için kesin son bölüm belirlenemiyor."
        )
    else:
        print("Son erişilen video")

    print(f"Erişim zamanı: {_format_access_time(videos[0])}")
    print(f"Taranan klasör: {root}")

    for number, video in enumerate(videos, start=1):
        if multiple_videos:
            print(f"\n[{number}]")
        print(f"Dosya: {video.path.name}")
        print(f"Yol:   {video.path}")


def _validated_root(raw_path: str) -> Path:
    root = Path(raw_path).expanduser()
    try:
        if not root.exists():
            raise ValueError("Klasör bulunamadı")
        if not root.is_dir():
            raise ValueError("Verilen yol bir klasör değil")

        root = root.resolve()
        # Kök yolunun gerçekten listelenebildiğini kontrol eder; dosya içeriği
        # okunmadığından erişim zamanları değişmez.
        with os.scandir(root):
            pass
    except PermissionError as error:
        raise ValueError("Klasöre erişilemiyor") from error
    except OSError as error:
        raise ValueError(f"Klasöre erişilemiyor: {error}") from error
    return root


def main(argv: Sequence[str] | None = None) -> int:
    """Komut satırı programını çalıştırır ve çıkış kodunu döndürür."""

    args = _parser().parse_args(argv)
    try:
        root = _validated_root(args.klasor)
    except ValueError as error:
        print(f"Hata: {error}: {args.klasor}", file=sys.stderr)
        return 2

    try:
        videos = find_most_recent_videos(root, warn=_write_warning)
    except OSError as error:
        print(f"Hata: Klasör taranamadı: {root} ({error})", file=sys.stderr)
        return 2

    if not videos:
        print(f"Hata: Bu klasör ağacında video dosyası bulunamadı: {root}", file=sys.stderr)
        return 1

    _write_results(root, videos)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
