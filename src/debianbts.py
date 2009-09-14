#!/usr/bin/env python

# debianbts.py - Methods to query Debian's BTS.
# Copyright (C) 2007-2008  Bastian Venthur <venthur@debian.org>
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


import SOAPpy
import os
import time
from HTMLParser import HTMLParser
import urllib
from datetime import datetime

# Setup the soap server
# TODO: recognize HTTP proxy environment variable    # Default values
URL = 'http://bugs.debian.org/cgi-bin/soap.cgi'
NS = 'Debbugs/SOAP/V1'
server = SOAPpy.SOAPProxy(URL, NS)

# for ordinary html
BTS_URL = "http://bugs.debian.org/"

# helpers to calculate the 'value' of a bug
STATUS_VALUE = {u'outstanding' : 90,
                u'resolved' : 50,
                u'archived' : 10}
SEVERITY_VALUE = {u"critical" : 7,
                  u"grave" : 6,
                  u"serious" : 5,
                  u"important" : 4,
                  u"normal" : 3,
                  u"minor" : 2,
                  u"wishlist" : 1}


class Bugreport(object):
    """Represents a bugreport from Debian's Bug Tracking System."""
    
    def __init__(self, nr):
        self.nr = unicode(nr)
        self.summary = None
        self.submitter = None
        self.status = None
        self.severity = None
        self.fulltext = None
        self.package = None
        self.firstaction = None
        self.lastaction = None
        self.tags = None
    
    def __str__(self):
        s  = "Bug: %s\n" % self.nr
        s += "Package: %s\n" % self.package
        s += "Summary: %s\n" % self.summary
        s += "Submitter: %s\n" % self.submitter
        s += "Status: %s\n" % self.status
        s += "Severity: %s\n" % self.severity
        s += "Tags: %s\n" % self.tags
        s += "Firstaction: %s\n" % self.firstaction
        s += "Lastaction: %s\n" % self.lastaction
        s += "Fulltext: %s\n" % self.fulltext
        return s

    def value(self):
        """Returns an 'urgency value', the higher the number, the more urgent
        the bug is. Open bugs generally have higher urgencies than closed ones.
        """
        return STATUS_VALUE.get(self.status.lower(), 200) + SEVERITY_VALUE.get(self.severity.lower(), 20)

    
class Buglog(object):
    """Represents a single message of a bugreport."""
    
    def __init__(self, header, body):
        self.header = unicode(header)
        self.body = unicode(body)
        
    def __str__(self):
        s  = "Header: \n%s\n" % self.header
        s += "Body: \n%s\n" % self.body
        return s


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

def get_usertag(email, *tag):
    pass


def get_bug_log(nr):
    """Returns a list of Buglogs."""
    reply = _make_list(server.get_bug_log(nr))
    l = []
    for i in reply:
        l.append(_make_dict(i))
    bl = []
    for i in l:
        log = Buglog(i['header'], i['body'])
        bl.append(log)
    return bl


def newest_bugs(amount):
    """Returns a list of bugnumbers of the newest bugs."""
    return _make_list(server.newest_bugs(amount))


def get_bugs(*key_value):
    """
    Returns a list of bugnumbers, that match the conditions given bey the
    key-value pair(s).
    
    Possible keys are: package, submitter, maint, src, severity, status, tag, 
    owner, bugs, correspondent.
    
    Example: get_bugs('package', 'gtk-qt-engine','severity', 'normal')
    """
    return _make_list(server.get_bugs(*key_value))


def _parse_status(status):
    """Return a bugreport from a given status."""
    bug = Bugreport(status['key'])
    tmp = status['value']
    bug.summary = unicode(tmp['subject'], 'utf-8')
    bug.package =  unicode(tmp['package'], 'utf-8')
    bug.submitter = unicode(tmp['originator'], 'utf-8')
    bug.firstaction = datetime.utcfromtimestamp(tmp['date'])
    bug.lastaction = datetime.utcfromtimestamp(tmp['log_modified'])
    bug.severity = unicode(tmp['severity'], 'utf-8')
    if tmp['done']:
        bug.status = u"Resolved"
    else:
        bug.status = u"Outstanding"
    if tmp['tags']:
        bug.tags = unicode(tmp['tags'])
    return bug


def _make_list(listlike):
    """Converts a convert a SOAPpy array to a python list."""
    l = []
    for i in listlike:
        l.append(i)
    return l

def _make_dict(dictlike):
    """Converts a SOAPpy record into a python dict."""
    d = dict()
    for i in dictlike._keys():
        d[i] = dictlike[i]
    return d

def get_html_fulltext(bugnr):
    """Returns the full bugreport"""
    report = urllib.urlopen(str(BTS_URL) + str(bugnr))

    parser = HTMLStripper()
    parser.feed(unicode(report.read(), "utf-8", 'replace'))
    parser.close()
    return parser.result

class HTMLStripper(HTMLParser):
    """Strips all unwanted tags from given HTML/XML String"""
    
    invalid_tags = ('img')
   
    def __init__(self):
        HTMLParser.__init__(self)
        self.result = ""
  
    def handle_data(self, data):
        self.result += data

    def handle_entityref(self, name):
        self.result += "&"+name+";"

    def handle_charref(self, name):
        self.result += "&#"+name+";"
    
    def handle_starttag(self, tag, attrs):
        if not tag in self.invalid_tags:       
            self.result += '<' + tag
            for k, v in attrs:
                self.result += ' %s="%s"' % (k, v)
            self.result += '>'
        else:
            self.result += "<p>[ %s-tag removed by reportbug-ng ]</p>" % tag
            
    def handle_endtag(self, tag):
        if not tag in self.invalid_tags:
            self.result = "%s</%s>" % (self.result, tag)

if __name__ == '__main__':
    pass
    buglist = [11111, 22222, 496544, 393837]
    bugs = get_status(buglist)
    for i in bugs:
        print i


#    # an array of bugnumbers
#    print get_bugs('package', 'gtk-qt-engine','severity', 'normal')
    
    # something strange
    #bugs = server.get_usertag("debian-qa@lists.debian.org")
    
#    # an array of bugnumbers
#    print newest_bugs(20)

#    #l = get_bug_log('11111')
#    l = get_bug_log('66666')
#    print l
#    for i in l:
#        print i
    
#    for b in bugs:
#        print b
