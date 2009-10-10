#!/usr/bin/env python

import unittest
import debianbts as bts

class DebianBtsTestCase(unittest.TestCase):
    
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
            


suite = unittest.TestLoader().loadTestsFromTestCase(DebianBtsTestCase)

def main():
    unittest.main()

if __name__ == "__main__":
    main()