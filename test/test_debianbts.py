#!/usr/bin/env python
# -*- coding: utf-8 -*-

# debianbts_test.py - Unittests for debianbts.py.
# Copyright (C) 2009  Bastian Venthur <venthur@debian.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


from __future__ import division, unicode_literals, absolute_import, print_function

import datetime
import email.message
import math
import random
import unittest
import logging
import threading
try:
    import unittest.mock as mock
except ImportError:
    import mock

from pysimplesoap.simplexml import SimpleXMLElement

import debianbts as bts


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.NOTSET)


class DebianBtsTestCase(unittest.TestCase):

    def setUp(self):
        self.b1 = bts.Bugreport()
        self.b1.severity = 'normal'
        self.b2 = bts.Bugreport()
        self.b2.severity = 'normal'

    def test_get_usertag_empty(self):
        """get_usertag should return empty dict if no bugs are found."""
        d = bts.get_usertag("thisisatest@debian.org")
        self.assertEqual(d, dict())

    def test_get_usertag(self):
        """get_usertag should return dict with tag(s) and buglist(s)."""
        d = bts.get_usertag("debian-python@lists.debian.org")
        self.assertEqual(type(d), type(dict()))
        for k, v in d.items():
            self.assertEqual(type(""), type(k))
            self.assertEqual(type([]), type([]))
            for bug in v:
                self.assertEqual(type(bug), int)

    def test_get_usertag_filters(self):
        """get_usertag should return only requested tags"""
        tags = bts.get_usertag("debian-python@lists.debian.org")
        self.assertTrue(isinstance(tags, dict))
        randomKey0 = random.choice(list(tags.keys()))
        randomKey1 = random.choice(list(tags.keys()))

        filtered_tags = bts.get_usertag(
            "debian-python@lists.debian.org", randomKey0, randomKey1)

        self.assertEqual(len(filtered_tags), 2)
        self.assertEqual(set(filtered_tags[randomKey0]),
                          set(tags[randomKey0]))
        self.assertEqual(set(filtered_tags[randomKey1]),
                          set(tags[randomKey1]))

    def test_get_bugs_empty(self):
        """get_bugs should return empty list if no matching bugs where found."""
        l = bts.get_bugs("package", "thisisatest")
        self.assertEqual(l, [])

    def test_get_bugs(self):
        """get_bugs should return list of bugnumbers."""
        l = bts.get_bugs("submitter", "venthur@debian.org")
        self.assertFalse(len(l) == 0)
        self.assertEqual(type(l), type([]))
        for i in l:
            self.assertEqual(type(i), type(int()))

    def test_get_bugs_list(self):
        """previous versions of python-debianbts accepted malformed key-value lists."""
        l = bts.get_bugs('submitter', 'venthur@debian.org', 'severity', 'normal')
        l2 = bts.get_bugs(['submitter', 'venthur@debian.org', 'severity', 'normal'])
        self.assertFalse(len(l) == 0)
        l.sort()
        l2.sort()
        self.assertEqual(l, l2)

    def test_newest_bugs(self):
        """newest_bugs should return list of bugnumbers."""
        l = bts.newest_bugs(10)
        self.assertEqual(type(l), type([]))
        for i in l:
            self.assertEqual(type(i), type(int()))

    def test_newest_bugs_amount(self):
        """newest_bugs(amount) should return a list of len 'amount'. """
        for i in 0, 1, 10:
            l = bts.newest_bugs(i)
            self.assertEqual(len(l), i)

    def test_get_bug_log(self):
        """get_bug_log should return the correct data types."""
        bl = bts.get_bug_log(223344)
        self.assertEqual(type(bl), type([]))
        for i in bl:
            self.assertEqual(type(i), type(dict()))
            self.assertTrue("attachments" in i)
            self.assertEqual(type(i["attachments"]), type(list()))
            self.assertTrue("body" in i)
            self.assertTrue(isinstance(i["body"], type('')))
            self.assertTrue("header" in i)
            self.assertTrue(isinstance(i["header"], type('')))
            self.assertTrue("msg_num" in i)
            self.assertEqual(type(i["msg_num"]), type(int()))

    def test_get_bug_log_with_attachments(self):
        """get_bug_log should include attachments"""
        buglogs = bts.get_bug_log(400000)
        for bl in buglogs:
            self.assertTrue("attachments" in bl)

    def test_bug_log_message(self):
        """dict returned by get_bug_log has a email.Message field"""
        buglogs = bts.get_bug_log(400012)
        for buglog in buglogs:
            self.assertTrue('message' in buglog)
            msg = buglog['message']
            self.assertIsInstance(msg, email.message.Message)
            self.assertTrue('Subject' in msg)
            if not msg.is_multipart():
                self._assert_unicode(msg.get_payload())

    def test_bug_log_message_unicode(self):
        """test parsing of bug_log mail with non ascii characters"""
        buglogs = bts.get_bug_log(773321)
        buglog = buglogs[2]
        msg_payload = buglog['message'].get_payload()
        self._assert_unicode(msg_payload)
        self.assertTrue('é' in msg_payload)

    def test_empty_get_status(self):
        """get_status should return empty list if bug doesn't exits"""
        bugs = bts.get_status(0)
        self.assertEqual(type(bugs), list)
        self.assertEqual(len(bugs), 0)

    def test_sample_get_status(self):
        """test retrieving of a "known" bug status"""
        bugs = bts.get_status(486212)
        self.assertEqual(len(bugs), 1)
        bug = bugs[0]
        self.assertEqual(bug.bug_num, 486212)
        self.assertEqual(bug.date, datetime.datetime(2008, 6, 14, 10, 30, 2))
        self.assertTrue(bug.subject.startswith('[reportbug-ng] segm'))
        self.assertEqual(bug.package, 'reportbug-ng')
        self.assertEqual(bug.severity, 'normal')
        self.assertEqual(bug.tags, ['help'])
        self.assertEqual(bug.blockedby, [])
        self.assertEqual(bug.blocks, [])
        self.assertEqual(bug.summary, '')
        self.assertEqual(bug.location, 'archive')
        self.assertEqual(bug.source, 'reportbug-ng')
        self.assertEqual(bug.log_modified,
                          datetime.datetime(2008, 8, 17, 7, 26, 22))
        self.assertEqual(bug.pending, 'done')
        self.assertEqual(bug.done, True)
        self.assertEqual(bug.archived, True)
        self.assertEqual(bug.found_versions, ['reportbug-ng/0.2008.06.04'])
        self.assertEqual(bug.fixed_versions, ['reportbug-ng/1.0'])
        self.assertEqual(bug.affects, [])

    def test_bug_str(self):
        """test string conversion of a Bugreport"""
        self.b2.package = 'foo-pkg'
        self.b2.bug_num = 12222
        s = str(self.b2)
        self.assertTrue(isinstance(s, str)) # byte string in py2, unicode in py3
        self.assertTrue('bug_num: 12222\n' in s)
        self.assertTrue('package: foo-pkg\n' in s)

    def test_get_status_affects(self):
        """test a bug with "affects" field"""
        bugs = bts.get_status(290501, 770490)
        self.assertEqual(len(bugs), 2)
        self.assertEqual(bugs[0].affects, [])
        self.assertEqual(bugs[1].affects, ['conkeror'])

    def test_status_batches_large_bug_counts(self):
        """get_status should perform requests in batches to reduce server load."""
        with mock.patch.object(bts, '_build_soap_client') as mock_build_client:
            mock_build_client.return_value = mock_client = mock.Mock()
            mock_client.call.return_value = SimpleXMLElement(
                '<a><s-gensym3/></a>')
            nr = bts.BATCH_SIZE + 10.0
            calls = int(math.ceil(nr / bts.BATCH_SIZE))
            bts.get_status([722226] * int(nr))
            self.assertEqual(mock_client.call.call_count, calls)

    def test_status_batches_multiple_arguments(self):
        """get_status should batch multiple arguments into one request."""
        with mock.patch.object(bts, '_build_soap_client') as mock_build_client:
            mock_build_client.return_value = mock_client = mock.Mock()
            mock_client.call.return_value = SimpleXMLElement(
                '<a><s-gensym3/></a>')
            batch_size = bts.BATCH_SIZE

            calls = 1
            bts.get_status(*list(range(batch_size)))
            self.assertEqual(mock_client.call.call_count, calls)

            calls += 2
            bts.get_status(*list(range(batch_size + 1)))
            self.assertEqual(mock_client.call.call_count, calls)

    def test_comparison(self):
        """comparison of two bugs"""
        self.b1.archived = True
        self.b2.done = True
        self.assertTrue(self.b2 > self.b1)
        self.assertTrue(self.b2 >= self.b1)
        self.assertFalse(self.b2 == self.b1)
        self.assertFalse(self.b2 < self.b1)
        self.assertFalse(self.b2 <= self.b1)

    def test_comparison_equal(self):
        """comparison of two bug which are equal regarding their
        relative order"""
        self.b1.done = True
        self.b2.done = True
        self.assertFalse(self.b2 > self.b1)
        self.assertTrue(self.b2 >= self.b1)
        self.assertTrue(self.b2 == self.b1)
        self.assertFalse(self.b2 < self.b1)
        self.assertTrue(self.b2 <= self.b1)

    def test_get_bugs_int_bugs(self):
        """It is possible to pass a list of bug number to get_bugs"""
        bugs = bts.get_bugs('bugs', [400010, 400012], 'archive', True)
        self.assertEquals(set(bugs), set((400010, 400012)))

    def test_get_bugs_single_int_bug(self):
        """bugs parameter in get_bugs can be a list of int or a int"""
        bugs1 = bts.get_bugs('bugs', 400040, 'archive', True)
        bugs2 = bts.get_bugs('bugs', [400040], 'archive', True)
        self.assertEquals(bugs1, bugs2)

    def test_mergedwith(self):
        """Mergedwith is always a list of int."""
        # this one is merged with two other bugs
        m = bts.get_status(486212)[0].mergedwith
        self.assertTrue(len(m) == 2)
        for i in m:
            self.assertEqual(type(i), type(int()))
        # this one was merged with one bug
        m = bts.get_status(433550)[0].mergedwith
        self.assertTrue(len(m) == 1)
        self.assertEqual(type(m[0]), type(int()))
        # this one was not merged
        m = bts.get_status(474955)[0].mergedwith
        self.assertEqual(m, list())

    def test_base64_status_fields(self):
        """fields in bug status are sometimes base64-encoded"""
        bug = bts.get_status(711111)[0]
        self._assert_unicode(bug.originator)
        self.assertTrue(bug.originator.endswith('gmail.com>'))
        self.assertTrue('ł' in bug.originator)

    def test_base64_buglog_body(self):
        """buglog body is sometimes base64 encoded"""
        buglog = bts.get_bug_log(773321)
        body = buglog[2]['body']
        self._assert_unicode(buglog[1]['body'])
        self.assertTrue('é' in body)

    def test_string_status_originator(self):
        """test reading of bug status originator that is not base64-encoded"""
        bug = bts.get_status(711112)[0]
        self._assert_unicode(bug.originator)
        self.assertTrue(bug.originator.endswith('debian.org>'))

    def test_unicode_conversion_in_str(self):
        """string representation must deal with unicode correctly."""
        [bug] = bts.get_status(773321)
        try:
            bug.__str__()
        except UnicodeEncodeError:
            self.fail()

    def test_regression_588954(self):
        """Get_bug_log must convert the body correctly to unicode."""
        try:
            bts.get_bug_log(582010)
        except UnicodeDecodeError:
            self.fail()

    def test_regression_590073(self):
        """bug.blocks is sometimes a str sometimes an int."""
        try:
            # test the int case
            # TODO: test the string case
            bts.get_status(568657)
        except TypeError:
            self.fail()

    def test_regression_590725(self):
        """bug.body utf sometimes contains invalid continuation bytes."""
        try:
            bts.get_bug_log(578363)
            bts.get_bug_log(570825)
        except UnicodeDecodeError:
            self.fail()

    def test_regression_670446(self):
        """affects should be split by ','"""
        bug = bts.get_status(657408)[0]
        self.assertEqual(
            bug.affects, ['epiphany-browser-dev', 'libwebkit-dev'])

    def test_regression_799528(self):
        """fields of buglog are sometimes base64 encoded."""
        # bug with base64 encoding originator
        [bug] = bts.get_status(711111)
        self.assertTrue('ł' in bug.originator)
        # bug with base64 encoding subject
        [bug] = bts.get_status(779005)
        self.assertTrue('‘' in bug.subject)

    def _assert_unicode(self, string):
        """asserts for type of a unicode string, depending on python version"""
        if bts.PY2:
            self.assertIsInstance(string, unicode)
        else:
            self.assertIsInstance(string, str)


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



if __name__ == "__main__":
    unittest.main()
