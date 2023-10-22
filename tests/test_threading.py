"""Test threading behaviour of debianbts."""


import logging
import threading

import debianbts as bts

logger = logging.getLogger(__name__)


class TestThreading:
    """Test the module's thread safety."""

    def test_multithreading(self) -> None:
        """Test multithreading."""
        self._thread_failed = False
        threads = [
            threading.Thread(target=self._get_bugs_thread, args=(pkg,))
            for pkg in ("python3-gst-1.0", "libsoxr0")
        ] + [
            threading.Thread(target=self._get_bug_log_thread, args=(bug_n,))
            for bug_n in (300000, 300001)
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        assert not self._thread_failed

    def _get_bugs_thread(self, pkg: str) -> None:
        try:
            bts.get_bugs(package=pkg)
        except Exception:
            self._thread_failed = True
            logger.exception("Threaded get_bugs() call failed.")

    def _get_bug_log_thread(self, bug_num: int) -> None:
        try:
            bts.get_bug_log(bug_num)
        except Exception:
            self._thread_failed = True
            logger.exception("Threaded get_bug_log() call failed.")
