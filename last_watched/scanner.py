from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


VIDEO_EXTENSIONS = frozenset({".mkv", ".mp4", ".avi", ".mov", ".m4v", ".wmv", ".webm"})


@dataclass(frozen=True)
class VideoFile:

    path: Path
    access_time_ns: int


WarningHandler = Callable[[Path, OSError], None]


def find_most_recent_videos(
    root: Path, warn: WarningHandler | None = None
) -> list[VideoFile]:

    newest_access_time: int | None = None
    newest_videos: list[VideoFile] = []
    pending_directories = [root]

    while pending_directories:
        directory = pending_directories.pop()
        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            pending_directories.append(Path(entry.path))
                            continue

                        if not entry.is_file(follow_symlinks=False):
                            continue

                        path = Path(entry.path)
                        if path.suffix.casefold() not in VIDEO_EXTENSIONS:
                            continue

                        access_time = entry.stat(follow_symlinks=False).st_atime_ns
                    except OSError as error:
                        if warn is not None:
                            warn(Path(entry.path), error)
                        continue

                    video = VideoFile(path=path, access_time_ns=access_time)
                    if newest_access_time is None or access_time > newest_access_time:
                        newest_access_time = access_time
                        newest_videos = [video]
                    elif access_time == newest_access_time:
                        newest_videos.append(video)
        except OSError as error:
            if directory == root:
                raise
            if warn is not None:
                warn(directory, error)

    return sorted(newest_videos, key=lambda video: str(video.path).casefold())
