#!/usr/bin/env python

# debianbts.py - Methods to query Debian's BTS.
# Copyright (C) 2007-2010  Bastian Venthur <venthur@debian.org>
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


from datetime import datetime

import SOAPpy


# Setup the soap server
# TODO: recognize HTTP proxy environment variable    # Default values
URL = 'http://bugs.debian.org/cgi-bin/soap.cgi'
NS = 'Debbugs/SOAP/V1'
server = SOAPpy.SOAPProxy(URL, NS)
BTS_URL = 'http://bugs.debian.org/'

class Bugreport(object):
    """Represents a bugreport from Debian's Bug Tracking System."""
    
    def __init__(self):
        self.originator = None
        self.date = None
        self.subject = None
        self.msgid = None
        self.package = None
        self.tags = None
        self.done = None
        self.forwarded = None
        self.mergedwith = None
        self.severity = None
        self.owner = None
        self.found_versions = None
        self.found_date = None
        self.fixed_versions = None
        self.fixed_date = None
        self.blocks = None
        self.blockedby = None
        self.unarchived = None
        self.summary = None
        self.affects = None
        self.log_modified = None
        self.location = None
        self.archived = None
        self.bug_num = None
        self.source = None
        # Buggy implemented in debbugs, ignoring it
        self.fixed = None
        # Buggy implemented in debbugs, ignoring it
        self.found = None
        self.keywords = None
        # Will vanish in debbugs, use bug_num
        self.id = None
        self.pending = None

    
    def __str__(self):
        s = ""
        for key, value in self.__dict__.iteritems():
            s += "%s: %s\n" % (key, str(value))
        return s
    
    def __cmp__(self, other):
        """Compare a bugreport with another.
        
        The more open and and urgent a bug is, the greater the bug is:
            outstanding > resolved > archived
            critical > grave > serious > important > normal > minor > wishlist.
        Openness always beats urgency, eg an archived bug is *always* smaller
        than an outstanding bug.
        
        This sorting is useful for displaying bugreports in a list and sorting
        them in a useful way.
        """ 
        
        myval = self._get_value()
        otherval = other._get_value()
        if myval < otherval: 
            return -1
        elif myval == otherval: 
            return 0
        else: 
            return 1 
        

    def _get_value(self):
        if self.archived:
            # archived and done
            val = 0
        elif self.done:
            # not archived and done
            val = 10
        else:
            # not done
            val = 20
        val += {u"critical" : 7, 
                u"grave" : 6,
                u"serious" : 5,
                u"important" : 4,
                u"normal" : 3,
                u"minor" : 2,
                u"wishlist" : 1}[self.severity]
        return val

    
def get_status(*nr):
    """Returns a list of Bugreports."""
    reply = server.get_status(*nr)
    # If we called get_status with one single bug, we get a single bug,
    # if we called it with a list of bugs, we get a list,
    # No available bugreports returns an enmpy list
    bugs = []
    if not reply:
        pass
    elif type(reply[0]) == type([]):
        for elem in reply[0]:
            bugs.append(_parse_status(elem))
    else:
        bugs.append(_parse_status(reply[0]))
    return bugs


def get_usertag(email, *tags):
    """Return a dictionary of (usertag, buglist) mappings.
    
    If tags are given the dictionary is limited to the matching tags, if no tags
    are given all available tags are returned.
    """
    reply = server.get_usertag(email, *tags)
    # reply is an empty string if no bugs match the query
    return dict() if reply == "" else reply._asdict()


def get_bug_log(nr):
    """Return a list of Buglogs.
    
    A buglog is a dictionary with the following mappings:
        "header" => string
        "body" => string
        "attachments" => list
        "msg_num" => int
    """
    reply = server.get_bug_log(nr)
    buglog = [i._asdict() for i in reply._aslist()]
    for b in buglog:
        b["header"] = unicode(b["header"], 'utf-8')
        b["body"] = unicode(b["body"], 'utf-8')
        b["msg_num"] = int(b["msg_num"])
        b["attachments"] = b["attachments"]._aslist()
    return buglog


def newest_bugs(amount):
    """Returns a list of bugnumbers of the newest bugs."""
    reply = server.newest_bugs(amount)
    return reply._aslist()


def get_bugs(*key_value):
    """
    Returns a list of bugnumbers, that match the conditions given by the
    key-value pair(s).
    
    Possible keys are: package, submitter, maint, src, severity, status, tag, 
    owner, bugs, correspondent.
    
    Example: get_bugs('package', 'gtk-qt-engine', 'severity', 'normal')
    """
    reply = server.get_bugs(*key_value)
    return reply._aslist()


def _parse_status(status):
    """Return a bugreport object from a given status."""
    status = status._asdict()
    bug = Bugreport()
    tmp = status['value']
    
    bug.originator = unicode(tmp['originator'], 'utf-8')
    bug.date = datetime.utcfromtimestamp(tmp['date'])
    bug.subject = unicode(tmp['subject'], 'utf-8')
    bug.msgid = unicode(tmp['msgid'], 'utf-8')
    bug.package = unicode(tmp['package'], 'utf-8')
    bug.tags = unicode(tmp['tags'], 'utf-8').split()
    bug.done = bool(tmp['done'])
    bug.forwarded = unicode(tmp['forwarded'], 'utf-8')
    # Should be a list but does not appear to be one
    bug.mergedwith = tmp['mergedwith']
    bug.severity = unicode(tmp['severity'], 'utf-8')
    bug.owner = unicode(tmp['owner'], 'utf-8')
    # sometimes it is a float, sometimes it is "$packagename/$version"
    bug.found_versions = [unicode(str(i), 'utf-8') for i in tmp['found_versions']]
    bug.found_date = [datetime.utcfromtimestamp(i) for i in tmp["found_date"]]
    bug.fixed_versions = [unicode(str(i), 'utf-8') for i in tmp['fixed_versions']]
    bug.fixed_date = [datetime.utcfromtimestamp(i) for i in tmp["fixed_date"]]
    bug.blocks = unicode(tmp['blocks'], 'utf-8')
    # here too: sometimes float sometimes string
    bug.blockedby = unicode(str(tmp['blockedby']), 'utf-8')
    bug.unarchived = bool(tmp["unarchived"])
    bug.summary = unicode(tmp['summary'], 'utf-8')
    bug.affects = unicode(tmp['affects'], 'utf-8')
    bug.log_modified = datetime.utcfromtimestamp(tmp['log_modified'])
    bug.location = unicode(tmp['location'], 'utf-8')
    bug.archived = bool(tmp["archived"])
    bug.bug_num = int(tmp['bug_num'])
    bug.source = unicode(tmp['source'], 'utf-8')
    # Not fully implemented in debbugs, use fixed_versions and found_versions
    #bug.fixed = _parse_crappy_soap(tmp, "fixed")
    #bug.found = _parse_crappy_soap(tmp, "found")
    # Space separated list
    bug.keywords = unicode(tmp['keywords'], 'utf-8').split()
    # Will vanish in future versions of debbugs, use bug_num
    #bug.id = int(tmp['id'])
    bug.pending = unicode(tmp['pending'], 'utf-8')
    return bug


def _parse_crappy_soap(crap, key):
    """Parses 'interesting' SOAP structure.
    
    Crap should be a list, but can be an empty string or a nested dict where 
    the actual list is hidden behind various keys.
    """ 
    tmp = [] if crap[key] == '' else crap[key]._asdict()['item']
    if type(tmp) != type(list()):
        tmp = [tmp]
    l = list()
    for i in tmp:
        l.append(unicode(str(i._asdict()['key']), "utf-8"))
    return l
    

if __name__ == '__main__':
    pass
    #buglist = [11111, 22222, 496544, 393837, 547498]
    buglist = get_bugs("package", "reportbug")
    bugs = get_status(buglist)
    bugs.sort()
    print bugs
    for i in bugs:
        print str(i)
