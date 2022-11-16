#!/usr/bin/env python

"""
Query Debian's Bug Tracking System (BTS).

This module provides a layer between Python and Debian's BTS. It provides
methods to query the BTS using the BTS' SOAP interface, and the Bugreport class
which represents a bugreport from the BTS.
"""


from __future__ import annotations

import base64
import email.feedparser
import email.policy
from datetime import datetime
import os
import logging
from typing import Any, Iterable

from pysimplesoap.client import SoapClient
from pysimplesoap.simplexml import SimpleXMLElement


logger = logging.getLogger(__name__)


# Support running from Debian infrastructure
ca_path = "/etc/ssl/ca-debian"
if os.path.isdir(ca_path):
    os.environ["SSL_CERT_DIR"] = ca_path


# Setup the soap server
# Default values
URL = "https://bugs.debian.org/cgi-bin/soap.cgi"
NS = "Debbugs/SOAP/V1"
BTS_URL = "https://bugs.debian.org/"
# Max number of bugs to send in a single get_status request
BATCH_SIZE = 500

SEVERITIES = {
    "critical": 7,
    "grave": 6,
    "serious": 5,
    "important": 4,
    "normal": 3,
    "minor": 2,
    "wishlist": 1,
}


class Bugreport:
    """Represents a bugreport from Debian's Bug Tracking System.

    A bugreport object provides all attributes provided by the SOAP interface.
    Most of the attributes are strings, the others are marked.

    Attributes
    ----------
    bug_num : int
        The bugnumber
    severity : str
        Severity of the bugreport
    tags : list[str]
        Tags of the bugreport
    subject : str
        The subject/title of the bugreport
    originator : str
        Submitter of the bugreport
    mergedwith : list[int]
        List of bugnumbers this bug was merged with
    package : str
        Package of the bugreport
    source : str
        Source package of the bugreport
    date : datetime
        Date of bug creation
    log_modified : datetime
        Date of update of the bugreport
    done : boolean
        Is the bug fixed or not
    done_by : str | None
        Name and Email or None
    archived : bool
        Is the bug archived or not
    unarchived : bool
        Was the bug unarchived or not
    fixed_versions : list[str]
        List of versions, can be empty even if bug is fixed
    found_versions : list[str]
        List of version numbers where bug was found
    forwarded : str
        A URL or email address
    blocks: list[int]
        List of bugnumbers this bug blocks
    blockedby : list[int]
        List of bugnumbers which block this bug
    pending : str
        Either 'pending' or 'done'
    msgid : str
        Message ID of the bugreport
    owner : str
        Who took responsibility for fixing this bug
    location : str
        Either 'db-h' or 'archive'
    affects : list[str]
        List of Packagenames
    summary : str
        Arbitrary text
    """

    def __init__(self) -> None:
        self.originator: str
        self.date: datetime
        self.subject: str
        self.msgid: str
        self.package: str
        self.tags: list[str]
        self.done: bool
        self.done_by: str | None
        self.forwarded: str
        self.mergedwith: list[int]
        self.severity: str
        self.owner: str
        self.found_versions: list[str]
        self.fixed_versions: list[str]
        self.blocks: list[int]
        self.blockedby: list[int]
        self.unarchived: bool
        self.summary: str
        self.affects: list[str]
        self.log_modified: datetime
        self.location: str
        self.archived: bool
        self.bug_num: int
        self.source: str
        self.pending: str
        # The ones below are also there but not used
        # self.fixed = None
        # self.found = None
        # self.fixed_date = None
        # self.found_date = None
        # self.keywords = None
        # self.id = None

    def __str__(self) -> str:
        s = "\n".join(
            f"{key}: {value}" for key, value in self.__dict__.items()
        )
        return s + "\n"

    def __lt__(self, other: Bugreport) -> bool:
        """Compare a bugreport with another.

        The more open and urgent a bug is, the greater the bug is:

            outstanding > resolved > archived

            critical > grave > serious > important > normal > minor > wishlist.

        Openness always beats urgency, eg an archived bug is *always* smaller
        than an outstanding bug.

        This sorting is useful for displaying bugreports in a list and sorting
        them in a useful way.

        """
        return self._get_value() < other._get_value()

    def __le__(self, other: Bugreport) -> bool:
        return not self.__gt__(other)

    def __gt__(self, other: Bugreport) -> bool:
        return self._get_value() > other._get_value()

    def __ge__(self, other: Bugreport) -> bool:
        return not self.__lt__(other)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Bugreport):
            return NotImplemented
        return self._get_value() == other._get_value()

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Bugreport):
            return NotImplemented
        return not self.__eq__(other)

    def _get_value(self) -> int:
        if self.archived:
            # archived and done
            val = 0
        elif self.done:
            # not archived and done
            val = 10
        else:
            # not done
            val = 20
        val += SEVERITIES[self.severity]
        return val


def get_status(
    nrs: int | list[int] | tuple[int, ...],
) -> list[Bugreport]:
    """Returns a list of Bugreport objects.

    Given a list of bug numbers this method returns a list of Bugreport
    objects.

    Parameters
    ----------
    nrs
        The bugnumbers

    Returns
    -------
    list[Bugreport]
        list of Bugreport objects

    """
    numbers: list[int]
    if not isinstance(nrs, (list, tuple)):
        numbers = [nrs]
    else:
        numbers = list(nrs)

    # Process the input in batches to avoid hitting resource limits on
    # the BTS
    soap_client = _build_soap_client()
    bugs = []
    for i in range(0, len(numbers), BATCH_SIZE):
        slice_ = numbers[i:i + BATCH_SIZE]
        # I build body by hand, pysimplesoap doesn't generate soap Arrays
        # without using wsdl
        method_el = SimpleXMLElement("<get_status></get_status>")
        _build_int_array_el("arg0", method_el, slice_)
        reply = soap_client.call("get_status", method_el)
        for bug_item_el in reply("s-gensym3").children() or []:
            bug_el = bug_item_el.children()[1]
            bugs.append(_parse_status(bug_el))
    return bugs


def get_usertag(
    email: str,
    tags: None | list[str] | tuple[str, ...] = None,
) -> dict[str, list[int]]:
    """Get buglists by usertags.

    Parameters
    ----------
    email
    tags
        If tags are given the dictionary is limited to the matching tags, if no
        tags are given all available tags are returned.

    Returns
    -------
    dict[str, list[int]]
        a mapping of usertag -> buglist

    """
    if tags is None:
        tags = []

    reply = _soap_client_call("get_usertag", email, *tags)
    map_el = reply("s-gensym3")
    mapping = {}
    # element <s-gensys3> in response can have standard type
    # xsi:type=apachens:Map (example, for email debian-python@lists.debian.org)
    # OR no type, in this case keys are the names of child elements and
    # the array is contained in the child elements
    type_attr = map_el.attributes().get("xsi:type")
    if type_attr and type_attr.value == "apachens:Map":
        for usertag_el in map_el.children() or []:
            tag = str(usertag_el("key"))
            buglist_el = usertag_el("value")
            mapping[tag] = [int(bug) for bug in buglist_el.children() or []]
    else:
        for usertag_el in map_el.children() or []:
            tag = usertag_el.get_name()
            mapping[tag] = [int(bug) for bug in usertag_el.children() or []]
    return mapping


def get_bug_log(
    nr: int,
) -> list[dict[str, str | list[Any] | int | email.message.Message]]:
    """Get Buglogs.

    A buglog is a dictionary with the following mappings:
        * "header" => string
        * "body" => string
        * "attachments" => list
        * "msg_num" => int
        * "message" => email.message.Message

    Parameters
    ----------
    nr
        the bugnumber

    Returns
    -------
    list[dict[str, str | list[Any] | int | email.message.Message]]
        list of buglogs

    """
    reply = _soap_client_call("get_bug_log", nr)
    items_el = reply("soapenc:Array")
    buglogs = []
    for buglog_el in items_el.children():
        buglog: dict[str, str | list[Any] | int | email.message.Message] = {}
        header = _parse_string_el(buglog_el("header"))
        body = _parse_string_el(buglog_el("body"))
        msg_num = int(buglog_el("msg_num"))
        # server always returns an empty attachments array ?
        attachments: list[Any] = []

        mail_parser = email.feedparser.BytesFeedParser(
            policy=email.policy.SMTP
        )
        mail_parser.feed(header.encode())
        mail_parser.feed(b"\n\n")
        mail_parser.feed(body.encode())
        message = mail_parser.close()

        buglog = {
            "header": header,
            "body": body,
            "msg_num": msg_num,
            "attachments": attachments,
            "message": message,
        }

        buglogs.append(buglog)
    return buglogs


def newest_bugs(amount: int) -> list[int]:
    """Returns the newest bugs.

    This method can be used to query the BTS for the n newest bugs.

    Parameters
    ----------
    amount
        the number of desired bugs. E.g. if `amount` is 10 the method will
        return the 10 latest bugs.

    Returns
    -------
    list[int]
        the bugnumbers

    """
    reply = _soap_client_call("newest_bugs", amount)
    items_el = reply("soapenc:Array")
    return [int(item_el) for item_el in items_el.children() or []]


def get_bugs(
    **kwargs: str | int | list[int],
) -> list[int]:
    """Get list of bugs matching certain criteria.

    The conditions are defined by the keyword arguments.

    Arguments
    ---------
    kwargs
        Possible keywords are:
            * "package": bugs for the given package
            * "submitter": bugs from the submitter
            * "maint": bugs belonging to a maintainer
            * "src": bugs belonging to a source package
            * "severity": bugs with a certain severity
            * "status": can be either "done", "forwarded", or "open"
            * "tag": see http://www.debian.org/Bugs/Developer#tags for
              available tags
            * "owner": bugs which are assigned to `owner`
            * "bugs": takes single int or list of bugnumbers, filters the list
              according to given criteria
            * "correspondent": bugs where `correspondent` has sent a mail to
            * "archive": takes a string: "0" (unarchived), "1" (archived) or
              "both" (un- and archived). if omitted, only returns un-archived
              bugs.

    Returns
    -------
    list[int]
        the bugnumbers

    Examples
    --------
        >>> get_bugs(package='gtk-qt-engine', severity='normal')
        [12345, 23456]

    """
    # flatten kwargs to list:
    # {'foo': 'bar', 'baz': 1} -> ['foo', 'bar','baz', 1]
    args = []
    for k, v in kwargs.items():
        args.extend([k, v])

    # pysimplesoap doesn't generate soap Arrays without using wsdl
    # I build body by hand, converting list to array and using standard
    # pysimplesoap marshalling for other types
    method_el = SimpleXMLElement("<get_bugs></get_bugs>")
    for arg_n, kv in enumerate(args):
        arg_name = "arg" + str(arg_n)
        if isinstance(kv, (list, tuple)):
            _build_int_array_el(arg_name, method_el, kv)
        else:
            method_el.marshall(arg_name, kv)

    soap_client = _build_soap_client()
    reply = soap_client.call("get_bugs", method_el)
    items_el = reply("soapenc:Array")
    return [int(item_el) for item_el in items_el.children() or []]


def _parse_status(bug_el: SimpleXMLElement) -> Bugreport:
    """Return a bugreport object from a given status xml element

    Parameters
    ----------
    bug_el
        a status XML element

    Returns
    -------
    Bugreport
        a Bugreport object

    """
    bug = Bugreport()

    # plain fields
    for field in (
        "originator",
        "subject",
        "msgid",
        "package",
        "severity",
        "owner",
        "summary",
        "location",
        "source",
        "pending",
        "forwarded",
    ):
        setattr(bug, field, _parse_string_el(bug_el(field)))

    bug.date = datetime.utcfromtimestamp(float(bug_el("date")))
    bug.log_modified = datetime.utcfromtimestamp(float(bug_el("log_modified")))
    bug.tags = [tag for tag in str(bug_el("tags")).split()]
    bug.done = _parse_bool(bug_el("done"))
    bug.done_by = _parse_string_el(bug_el("done")) if bug.done else None
    bug.archived = _parse_bool(bug_el("archived"))
    bug.unarchived = _parse_bool(bug_el("unarchived"))
    bug.bug_num = int(bug_el("bug_num"))
    bug.mergedwith = [int(i) for i in str(bug_el("mergedwith")).split()]
    bug.blockedby = [int(i) for i in str(bug_el("blockedby")).split()]
    bug.blocks = [int(i) for i in str(bug_el("blocks")).split()]

    bug.found_versions = [
        str(el) for el in bug_el("found_versions").children() or []
    ]
    bug.fixed_versions = [
        str(el) for el in bug_el("fixed_versions").children() or []
    ]
    affects = [_f for _f in str(bug_el("affects")).split(",") if _f]
    bug.affects = [a.strip() for a in affects]
    # Also available, but unused or broken
    # bug.keywords = [keyword for keyword in
    #                 str(bug_el('keywords')).split()]
    # bug.fixed = _parse_crappy_soap(tmp, "fixed")
    # bug.found = _parse_crappy_soap(tmp, "found")
    # bug.found_date = \
    #     [datetime.utcfromtimestamp(i) for i in tmp["found_date"]]
    # bug.fixed_date = \
    #     [datetime.utcfromtimestamp(i) for i in tmp["fixed_date"]]
    return bug


_soap_client_kwargs = {
    "location": URL,
    "action": "",
    "namespace": NS,
    "soap_ns": "soap",
}


def set_soap_proxy(proxy_arg: str) -> None:
    """Set proxy for SOAP client.

    You must use this method after import to set the proxy.

    Parameters
    ----------
    proxy_arg

    """
    _soap_client_kwargs["proxy"] = proxy_arg


def set_soap_location(url: str) -> None:
    """Set location URL for SOAP client

    You may use this method after import to override the default URL.

    Parameters
    ----------
    url
        default URL

    """
    _soap_client_kwargs["location"] = url


def get_soap_client_kwargs() -> dict[str, str]:
    """Returns SOAP client kwargs.

    Returns
    -------
    dict[str, str]
        the SOAP client kwargs

    """
    return _soap_client_kwargs


def _build_soap_client() -> SoapClient:
    """Factory method that creates a SoapClient.

    For thread-safety we create SoapClients on demand instead of using a
    module-level one.

    Returns
    -------
    SoapClient
        a SoapClient instance

    """
    return SoapClient(**_soap_client_kwargs)


def _convert_soap_method_args(*args: Iterable[Any]) -> list[tuple[str, Any]]:
    """Convert arguments to be consumed by a SoapClient method

    Parameters
    ----------
    *args
        any argument

    Returns
    -------
    list[tuple[str, Any]]
        the converted arguments

    Examples
    --------
    Soap client required a list of named arguments:

        >>> _convert_soap_method_args('a', 1)
        [('arg0', 'a'), ('arg1', 1)]

    """
    soap_args = []
    for arg_n, arg in enumerate(args):
        soap_args.append(("arg" + str(arg_n), arg))
    return soap_args


def _soap_client_call(method_name: str, *args: Any) -> Any:
    """Wrapper to call SoapClient method

    Parameters
    ----------
    method_name
        the method name
    *args

    Returns
    -------
    Any

    """
    # a new client instance is built for threading issues
    soap_client = _build_soap_client()
    soap_args = _convert_soap_method_args(*args)
    return getattr(soap_client, method_name)(*soap_args)


def _build_int_array_el(
    el_name: str,
    parent: SimpleXMLElement,
    list_: list[Any],
) -> SimpleXMLElement:
    """Build Array as child of parent.

    More specifically: Build a soapenc:Array made of ints called `el_name` as a
    child of `parent`.

    Parameters
    ----------
    el_name
    parent
    list

    Returns
    -------
    SimpleXMLElement

    """
    el = parent.add_child(el_name)
    el.add_attribute(
        "xmlns:soapenc", "http://schemas.xmlsoap.org/soap/encoding/"
    )
    el.add_attribute("xsi:type", "soapenc:Array")
    el.add_attribute("soapenc:arrayType", f"xsd:int[{len(list_):d}]")
    for item in list_:
        item_el = el.add_child("item", str(item))
        item_el.add_attribute("xsi:type", "xsd:int")
    return el


def _parse_bool(el: SimpleXMLElement) -> bool:
    """Parse a boolean value from a XML element.

    Parameters
    ----------
    el
        the element to parse

    Returns
    -------
    bool
        the parsed value

    """
    value = str(el)
    return not value.strip() in ("", "0")


def _parse_string_el(el: SimpleXMLElement) -> str:
    """Read a string element, maybe encoded in base64.

    Parameters
    ----------
    el
        the element to parse

    Returns
    -------
    str
        the parsed value

    """
    value = str(el)
    el_type = el.attributes().get("xsi:type")
    if el_type and el_type.value == "xsd:base64Binary":
        tmp = base64.b64decode(value)
        value = tmp.decode("utf-8", errors="replace")
    return value
