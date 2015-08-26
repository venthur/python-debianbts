#!/usr/bin/env python

# debianbts.py - Methods to query Debian's BTS.
# Copyright (C) 2007-2015  Bastian Venthur <venthur@debian.org>
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


"""Query Debian's Bug Tracking System (BTS).

This module provides a layer between Python and Debian's BTS. It
provides methods to query the BTS using the BTS' SOAP interface, and the
Bugreport class which represents a bugreport from the BTS.
"""


from datetime import datetime
import os

from pysimplesoap.client import SoapClient
from pysimplesoap.simplexml import SimpleXMLElement

# Support running from Debian infrastructure
ca_path = '/etc/ssl/ca-debian'
if os.path.isdir(ca_path):
    os.environ['SSL_CERT_DIR'] = ca_path

# Setup the soap server
# Default values
URL = 'https://bugs.debian.org/cgi-bin/soap.cgi'
NS = 'Debbugs/SOAP/V1'
BTS_URL = 'https://bugs.debian.org/'
# Max number of bugs to send in a single get_status request
BATCH_SIZE = 500

soap_client = SoapClient(location=URL, namespace=NS, soap_ns='soap')


class Bugreport(object):
    """Represents a bugreport from Debian's Bug Tracking System.

    A bugreport object provides all attributes provided by the SOAP
    interface. Most of the attributs are strings, the others are marked.

    * bug_num: The bugnumber (int)
    * severity: Severity of the bugreport
    * tags: List of tags of the bugreport (list of strings)
    * subject:  The subject/title of the bugreport
    * originator: Submitter of the bugreport
    * mergedwith: List of bugnumbers this bug was merged with (list of
      ints)
    * package: Package of the bugreport
    * source: Source package of the bugreport
    * date: Date of bug creation (datetime)
    * log_modified: Date of update of the bugreport (datetime)
    * done: Is the bug fixed or not (bool)
    * archived: Is the bug archived or not (bool)
    * unarchived: Was the bug unarchived or not (bool)
    * fixed_versions: List of versions, can be empty even if bug is
      fixed (list of strings)
    * found_versions: List of version numbers where bug was found (list
      of strings)
    * forwarded: A URL or email address
    * blocks: List of bugnumbers this bug blocks (list of ints)
    * blockedby: List of bugnumbers which block this bug (list of ints)
    * pending: Either 'pending' or 'done'
    * msgid: Message ID of the bugreport
    * owner: Who took responsibility for fixing this bug
    * location: Either 'db-h' or 'archive'
    * affects: List of Packagenames (list of strings)
    * summary: Arbitrary text
    """

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
        self.fixed_versions = None
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
        self.pending = None
        # The ones below are also there but not used
        # self.fixed = None
        # self.found = None
        # self.fixed_date = None
        # self.found_date = None
        # self.keywords = None
        # self.id = None

    def __str__(self):
        s = ""
        for key, value in self.__dict__.iteritems():
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            s += "%s: %s\n" % (key, str(value))
        return s

    def __cmp__(self, other):
        """Compare a bugreport with another.

        The more open and and urgent a bug is, the greater the bug is:

            outstanding > resolved > archived

            critical > grave > serious > important > normal > minor > wishlist.

        Openness always beats urgency, eg an archived bug is *always*
        smaller than an outstanding bug.

        This sorting is useful for displaying bugreports in a list and
        sorting them in a useful way.

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
        val += {u"critical": 7,
                u"grave": 6,
                u"serious": 5,
                u"important": 4,
                u"normal": 3,
                u"minor": 2,
                u"wishlist": 1}[self.severity]
        return val


def get_status(*nrs):
    """Returns a list of Bugreport objects."""
    # If we called get_status with one single bug, we get a single bug,
    # if we called it with a list of bugs, we get a list,
    # No available bugreports returns an empty list
    bugs = []
    list_ = []
    for nr in nrs:
        if isinstance(nr, list):
            list_.extend(nr)
        else:
            list_.append(nr)
    # Process the input in batches to avoid hitting resource limits on the BTS
    for i in range(0, len(list_), BATCH_SIZE):
        slice_ = list_[i:i + BATCH_SIZE]
        # I build body by hand, pysimplesoap doesn't generate soap Arrays
        # without using wsdl
        method_el = SimpleXMLElement('<get_status></get_status>')
        _build_int_array_el('arg0', method_el, slice_)
        reply = soap_client.call('get_status', method_el)
        for bug_item_el in reply('s-gensym3').children() or []:
            bug_el = bug_item_el.children()[1]
            bugs.append(_parse_status(bug_el))
    return bugs


def get_usertag(email, *tags):
    """Return a dictionary of "usertag" => buglist mappings.

    If tags are given the dictionary is limited to the matching tags, if
    no tags are given all available tags are returned.
    """
    reply = _soap_client_call('get_usertag', email, *tags)
    map_el = reply('s-gensym3')
    mapping = {}
    # element <s-gensys3> in response can have standard type
    # xsi:type=apachens:Map (example, for email debian-python@lists.debian.org)
    # OR no type, in this case keys are the names of child elements and
    # the array is contained in the child elements
    type_attr = map_el.attributes().get('xsi:type')
    if type_attr and type_attr.value == 'apachens:Map':
        for usertag_el in map_el.children() or []:
            tag = str(usertag_el('key'))
            buglist_el = usertag_el('value')
            mapping[tag] = [int(bug) for bug in buglist_el.children() or []]
    else:
        for usertag_el in map_el.children() or []:
            tag = usertag_el.get_name()
            mapping[tag] = [int(bug) for bug in usertag_el.children() or []]
    return mapping


def get_bug_log(nr):
    """Return a list of Buglogs.

    A buglog is a dictionary with the following mappings:
        "header" => string
        "body" => string
        "attachments" => list
        "msg_num" => int
    """
    reply = _soap_client_call('get_bug_log', nr)
    items_el = reply('soapenc:Array')
    buglogs = []
    for buglog_el in items_el.children():
        buglog = {}
        buglog["header"] = _uc(str(buglog_el("header")))
        buglog["body"] = _uc(str(buglog_el("body")))
        buglog["msg_num"] = int(buglog_el("msg_num"))
        buglog["attachments"] = []
        # server always returns an empty attachments array ?
        buglogs.append(buglog)
    return buglogs


def newest_bugs(amount):
    """Returns a list of bugnumbers of the `amount` newest bugs."""
    reply = _soap_client_call('newest_bugs', amount)
    items_el = reply('soapenc:Array')
    return [int(item_el) for item_el in items_el.children() or []]


def get_bugs(*key_value):
    """Returns a list of bugnumbers, that match the conditions given by
    the key-value pair(s).

    Possible keys are:
        "package": bugs for the given package
        "submitter": bugs from the submitter
        "maint": bugs belonging to a maintainer
        "src": bugs belonging to a source package
        "severity": bugs with a certain severity
        "status": can be either "done", "forwarded", or "open"
        "tag": see http://www.debian.org/Bugs/Developer#tags for
            available tags
        "owner": bugs which are assigned to `owner`
        "bugs": takes list of bugnumbers, filters the list according to
            given criteria
        "correspondent": bugs where `correspondent` has sent a mail to

    Example: get_bugs('package', 'gtk-qt-engine', 'severity', 'normal')
    """
    reply = _soap_client_call('get_bugs', *key_value)

    items_el = reply('soapenc:Array')
    return [int(item_el) for item_el in items_el.children() or []]


def _parse_status(bug_el):
    """Return a bugreport object from a given status xml element"""
    bug = Bugreport()

    # plain fields
    for field in ('originator', 'subject', 'msgid', 'package', 'severity',
                  'owner', 'summary', 'location', 'source', 'pending',
                  'forwarded'):
        setattr(bug, field, _uc(str(bug_el(field))))

    bug.date = datetime.utcfromtimestamp(float(bug_el('date')))
    bug.log_modified = datetime.utcfromtimestamp(float(bug_el('log_modified')))
    bug.tags = [_uc(tag) for tag in str(bug_el('tags')).split()]
    bug.done = _parse_bool(bug_el('done'))
    bug.archived = _parse_bool(bug_el('archived'))
    bug.unarchived = _parse_bool(bug_el('unarchived'))
    bug.bug_num = int(bug_el('bug_num'))
    bug.mergedwith = [int(i) for i in str(bug_el('mergedwith')).split()]
    bug.blockedby = [int(i) for i in str(bug_el('blockedby')).split()]
    bug.blocks = [int(i) for i in str(bug_el('blocks')).split()]

    bug.found_versions = [_uc(str(el)) for el in
                          bug_el('found_versions').children() or []]
    bug.fixed_versions = [_uc(str(el)) for el in
                          bug_el('fixed_versions').children() or []]
    affects = filter(None, str(bug_el('affects')).split(','))
    bug.affects = [_uc(a).strip() for a in affects]
    # Also available, but unused or broken
    # bug.keywords = [_uc(keyword) for keyword in
    #                 str(bug_el('keywords')).split()]
    # bug.fixed = _parse_crappy_soap(tmp, "fixed")
    # bug.found = _parse_crappy_soap(tmp, "found")
    # bug.found_date = [datetime.utcfromtimestamp(i) for i in tmp["found_date"]]
    # bug.fixed_date = [datetime.utcfromtimestamp(i) for i in tmp["fixed_date"]]
    return bug


def _soap_client_call(method_name, *args):
    # wrapper to work around pysimplesoap bug
    # https://github.com/pysimplesoap/pysimplesoap/issues/31
    soap_args = []
    for arg_n, arg in enumerate(args):
        soap_args.append(('arg' + str(arg_n), arg))
    return getattr(soap_client, method_name)(soap_client, *soap_args)


def _build_int_array_el(el_name, parent, list_):
    """build a soapenc:Array made of ints called `el_name` as a child
    of `parent`"""
    el = parent.add_child(el_name)
    el.add_attribute('xmlns:soapenc',
                     'http://schemas.xmlsoap.org/soap/encoding/')
    el.add_attribute('xsi:type', 'soapenc:Array')
    el.add_attribute('soapenc:arrayType', 'xsd:int[{:d}]'.format(len(list_)))
    for item in list_:
        item_el = el.add_child('item', str(item))
        item_el.add_attribute('xsi:type', 'xsd:int')
    return el


def _parse_bool(el):
    "parse a boolean value from a xml element"""
    value = str(el)
    return not value.strip() in ('', '0')


def _uc(string):
    """Convert string to unicode.

    This method only exists to unify the unicode conversion in this module.
    """
    return unicode(string, 'utf-8', 'replace')
