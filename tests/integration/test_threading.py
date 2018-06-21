import unittest
import threading

import debianbts as bts


class ThreadingTestCase(unittest.TestCase):
    """this class tests that the module is thread safe"""

    def setUp(self):
        self._thread_failed = False

    def test_multithreading(self):
        threads = [
            threading.Thread(target=self._get_bugs_thread, args=(pkg,))
            for pkg in ('python3-gst-1.0', 'libsoxr0')
        ] + [
            threading.Thread(target=self._get_bug_log_thread, args=(bug_n,))
            for bug_n in (300000, 300001)
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        if self._thread_failed:
            self.fail('multithreaded calls failed')

    def _get_bugs_thread(self, pkg):
        try:
            bugs = bts.get_bugs('package', pkg)
        except Exception as exc:
            self._thread_failed = True
            print('threaded get_bugs() call failed '
                  'with exception {} {}'.format(type(exc), exc))

    def _get_bug_log_thread(self, bug_num):
        try:
            bug_logs = bts.get_bug_log(bug_num)
        except Exception as exc:
            self._thread_failed = True
            print('threaded get_bug_log() call failed '
                  'with exception {} {}'.format(type(exc), exc))
