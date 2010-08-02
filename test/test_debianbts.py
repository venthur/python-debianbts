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


import unittest

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
            
    def testNewestBugs(self):
        """newest_bugs shoudl return list of bugnumbers."""
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
            self.assertTrue(i.has_key("attachments"))
            self.assertEqual(type(i["attachments"]), type(list()))
            self.assertTrue(i.has_key("body"))
            self.assertEqual(type(i["body"]), type(unicode()))
            self.assertTrue(i.has_key("header"))
            self.assertEqual(type(i["header"]), type(unicode()))
            self.assertTrue(i.has_key("msg_num"))
            self.assertEqual(type(i["msg_num"]), type(int()))

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

    def test_affects(self):
        """affects is a list of str."""
        # this one affects one bug
        #a = bts.get_status(290501)[0].affects
        #self.assertTrue(len(a) == 1)
        #self.assertEqual(type(a[0]), type(str()))
        # this one affects no other bug
        a = bts.get_status(437154)[0].affects
        self.assertEqual(a, [])

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




if __name__ == "__main__":
    unittest.main()

