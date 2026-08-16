from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from last_watched.__main__ import main
from last_watched.scanner import find_most_recent_videos


class LastWatchedTests(unittest.TestCase):
    def setUp(self) -> None:
        # Test ortamı sistem geçici klasörüne yazmayı kısıtlayabilir; çalışma
        # alanı ise test süresince temizlenebilen güvenilir bir konumdur.
        self.temporary_directory = tempfile.TemporaryDirectory(
            dir=Path(__file__).resolve().parents[1]
        )
        self.root = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _video(self, relative_path: str, access_time_ns: int) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"video")
        os.utime(path, ns=(access_time_ns, access_time_ns))
        return path

    def _run_main(self, *arguments: str) -> tuple[int, str, str]:
        stdout = StringIO()
        stderr = StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = main(arguments)
        return exit_code, stdout.getvalue(), stderr.getvalue()

    def test_selects_the_video_with_the_newest_access_time(self) -> None:
        old_video = self._video("Movies/old.mkv", 1_700_000_000_000_000_000)
        newest_video = self._video("Shows/new.mp4", 1_700_000_100_000_000_000)

        videos = find_most_recent_videos(self.root)

        self.assertEqual([newest_video], [video.path for video in videos])
        self.assertNotIn(old_video, [video.path for video in videos])

    def test_lists_all_videos_with_the_same_newest_access_time(self) -> None:
        timestamp = 1_700_000_100_000_000_000
        first_video = self._video("Shows/episode-1.mkv", timestamp)
        second_video = self._video("Shows/episode-2.webm", timestamp)
        self._video("Shows/older.avi", timestamp - 1)

        exit_code, stdout, stderr = self._run_main(str(self.root))

        self.assertEqual(0, exit_code)
        self.assertEqual("", stderr)
        self.assertIn(first_video.name, stdout)
        self.assertIn(second_video.name, stdout)
        self.assertIn(str(first_video), stdout)
        self.assertIn(str(second_video), stdout)
        self.assertIn("Son erişim zamanı eşit olan 2 video bulundu.", stdout)
        self.assertIn("kesin son bölüm belirlenemiyor", stdout)
        self.assertRegex(stdout, r"Erişim zamanı: \d{4}-\d{2}-\d{2}T")
        self.assertEqual(2, stdout.count("Dosya: "))

    def test_recurses_and_ignores_non_video_files(self) -> None:
        nested_video = self._video("Shows/Season 1/episode.m4v", 1_700_000_100_000_000_000)
        ignored_subtitle = self.root / "Shows/Season 1/episode.srt"
        ignored_poster = self.root / "Shows/poster.jpg"
        ignored_subtitle.write_text("subtitle", encoding="utf-8")
        ignored_poster.write_bytes(b"image")

        videos = find_most_recent_videos(self.root)

        self.assertEqual([nested_video], [video.path for video in videos])

    def test_invalid_and_video_less_directories_return_errors(self) -> None:
        missing = self.root / "does-not-exist"
        invalid_code, invalid_stdout, invalid_stderr = self._run_main(str(missing))
        self.assertEqual(2, invalid_code)
        self.assertEqual("", invalid_stdout)
        self.assertIn("Klasör bulunamadı", invalid_stderr)

        (self.root / "notes.txt").write_text("not a video", encoding="utf-8")
        empty_code, empty_stdout, empty_stderr = self._run_main(str(self.root))
        self.assertEqual(1, empty_code)
        self.assertEqual("", empty_stdout)
        self.assertIn("video dosyası bulunamadı", empty_stderr)

    def test_module_help_and_example_root_and_shows_paths_work(self) -> None:
        media_root = self.root / "P_S_M"
        shows = media_root / "Shows"
        movie = self._video("P_S_M/Movies/movie.wmv", 1_700_000_000_000_000_000)
        episode = self._video("P_S_M/Shows/Show/episode.mov", 1_700_000_100_000_000_000)
        project_root = Path(__file__).resolve().parents[1]

        help_result = subprocess.run(
            [sys.executable, "-m", "last_watched", "--help"],
            cwd=project_root,
            text=True,
            capture_output=True,
            check=False,
        )
        root_result = subprocess.run(
            [sys.executable, "-m", "last_watched", str(media_root)],
            cwd=project_root,
            text=True,
            capture_output=True,
            check=False,
        )
        shows_result = subprocess.run(
            [sys.executable, "-m", "last_watched", str(shows)],
            cwd=project_root,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(0, help_result.returncode)
        self.assertIn("Taranacak kök klasör yolu", help_result.stdout)
        self.assertEqual(0, root_result.returncode)
        self.assertIn(str(episode), root_result.stdout)
        self.assertNotIn(str(movie), root_result.stdout)
        self.assertEqual(0, shows_result.returncode)
        self.assertIn(str(episode), shows_result.stdout)
        self.assertNotIn(str(movie), shows_result.stdout)


if __name__ == "__main__":
    unittest.main()
