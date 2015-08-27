#!/usr/bin/env python

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


import datetime
import math
import random
import unittest
try:
    import unittest.mock as mock
except ImportError:
    import mock

from pysimplesoap.simplexml import SimpleXMLElement

import debianbts as bts


class DebianBtsTestCase(unittest.TestCase):

    def setUp(self):
        self.b1 = bts.Bugreport()
        self.b1.severity = 'normal'
        self.b2 = bts.Bugreport()
        self.b2.severity = 'normal'

    def testGetUsertagEmpty(self):
        """get_usertag should return empty dict if no bugs are found."""
        d = bts.get_usertag("thisisatest@debian.org")
        self.assertEqual(d, dict())

    def testGetUsertag(self):
        """get_usertag should return dict with tag(s) and buglist(s)."""
        d = bts.get_usertag("debian-python@lists.debian.org")
        self.assertEqual(type(d), type(dict()))
        for k, v in d.iteritems():
            self.assertEqual(type(""), type(k))
            self.assertEqual(type([]), type([]))
            for bug in v:
                self.assertEquals(type(bug), int)

    def testGetUsertagFilters(self):
        """get_usertag should return only requested tags"""
        tags = bts.get_usertag("debian-python@lists.debian.org")
        self.assertTrue(isinstance(tags, dict))
        randomKey0 = random.choice(tags.keys())
        randomKey1 = random.choice(tags.keys())

        filtered_tags = bts.get_usertag(
            "debian-python@lists.debian.org", randomKey0, randomKey1)

        self.assertEquals(len(filtered_tags), 2)
        self.assertEquals(set(filtered_tags[randomKey0]),
                          set(tags[randomKey0]))
        self.assertEquals(set(filtered_tags[randomKey1]),
                          set(tags[randomKey1]))

    def testGetBugsEmpty(self):
        """get_bugs should return empty list if no matching bugs where found."""
        l = bts.get_bugs("package", "thisisatest")
        self.assertEqual(l, [])

    def testGetBugs(self):
        """get_bugs should return list of bugnumbers."""
        l = bts.get_bugs("owner", "venthur@debian.org")
        self.assertEqual(type(l), type([]))
        for i in l:
            self.assertEqual(type(i), type(int()))

    def testGetBugsList(self):
        """previous versions of python-debianbts accepted malformed key-value lists."""
        l = bts.get_bugs('owner', 'venthur@debian.org', 'severity', 'normal')
        l2 = bts.get_bugs(['owner', 'venthur@debian.org', 'severity', 'normal'])
        self.assertEqual(l, l2)

    def testNewestBugs(self):
        """newest_bugs should return list of bugnumbers."""
        l = bts.newest_bugs(10)
        self.assertEqual(type(l), type([]))
        for i in l:
            self.assertEqual(type(i), type(int()))

    def testNewestBugsAmount(self):
        """newest_bugs(amount) should return a list of len 'amount'. """
        for i in 0, 1, 10:
            l = bts.newest_bugs(i)
            self.assertEqual(len(l), i)

    def testGetBugLog(self):
        """get_bug_log should return the correct data types."""
        bl = bts.get_bug_log(223344)
        self.assertEqual(type(bl), type([]))
        for i in bl:
            self.assertEqual(type(i), type(dict()))
            self.assertTrue("attachments" in i)
            self.assertEqual(type(i["attachments"]), type(list()))
            self.assertTrue("body" in i)
            self.assertEqual(type(i["body"]), type(unicode()))
            self.assertTrue("header" in i)
            self.assertEqual(type(i["header"]), type(unicode()))
            self.assertTrue("msg_num" in i)
            self.assertEqual(type(i["msg_num"]), type(int()))

    def testGetBugLogWithAttachments(self):
        """get_bug_log should include attachments"""
        buglogs = bts.get_bug_log(400000)
        for bl in buglogs:
            self.assertTrue("attachments" in bl)

    def testEmptyGetStatus(self):
        """get_status should return empty list if bug doesn't exits"""
        bugs = bts.get_status(0)
        self.assertEquals(type(bugs), list)
        self.assertEquals(len(bugs), 0)

    def testSampleGetStatus(self):
        """test retrieving of a "known" bug status"""
        bugs = bts.get_status(486212)
        self.assertEquals(len(bugs), 1)
        bug = bugs[0]
        self.assertEquals(bug.bug_num, 486212)
        self.assertEquals(bug.date, datetime.datetime(2008, 6, 14, 10, 30, 02))
        self.assertTrue(bug.subject.startswith('[reportbug-ng] segm'))
        self.assertEquals(bug.package, 'reportbug-ng')
        self.assertEquals(bug.severity, 'normal')
        self.assertEquals(bug.tags, ['help'])
        self.assertEquals(bug.blockedby, [])
        self.assertEquals(bug.blocks, [])
        self.assertEquals(bug.summary, '')
        self.assertEquals(bug.location, 'archive')
        self.assertEquals(bug.source, 'reportbug-ng')
        self.assertEquals(bug.log_modified,
                          datetime.datetime(2008, 8, 17, 7, 26, 22))
        self.assertEquals(bug.pending, 'done')
        self.assertEquals(bug.done, True)
        self.assertEquals(bug.archived, True)
        self.assertEquals(bug.found_versions, ['reportbug-ng/0.2008.06.04'])
        self.assertEquals(bug.fixed_versions, ['reportbug-ng/1.0'])
        self.assertEquals(bug.affects, [])

    def testGetStatusAffects(self):
        """test a bug with "affects" field"""
        bugs = bts.get_status(290501, 770490)
        self.assertEquals(len(bugs), 2)
        self.assertEquals(bugs[0].affects, [])
        self.assertEquals(bugs[1].affects, ['conkeror'])

    def testStatusBatchesLargeBugCounts(self):
        """get_status should perform requests in batches to reduce server load."""
        with mock.patch.object(bts.soap_client, 'call') as MockStatus:
            MockStatus.return_value = SimpleXMLElement('<a><s-gensym3/></a>')
            nr = bts.BATCH_SIZE + 10.0
            calls = int(math.ceil(nr / bts.BATCH_SIZE))
            bts.get_status([722226] * int(nr))
            self.assertEqual(MockStatus.call_count, calls)

    def testStatusBatchesMultipleArguments(self):
        """get_status should batch multiple arguments into one request."""
        with mock.patch.object(bts.soap_client, 'call') as MockStatus:
            MockStatus.return_value = SimpleXMLElement('<a><s-gensym3/></a>')
            batch_size = bts.BATCH_SIZE

            calls = 1
            bts.get_status(*range(batch_size))
            self.assertEqual(MockStatus.call_count, calls)

            calls += 2
            bts.get_status(*range(batch_size + 1))
            self.assertEqual(MockStatus.call_count, calls)

    def testComparison(self):
        self.b1.archived = True
        self.b2.done = True
        self.assertTrue(self.b2 > self.b1)

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
            bug.affects, [u'epiphany-browser-dev', u'libwebkit-dev'])


if __name__ == "__main__":
    unittest.main()
