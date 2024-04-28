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
import logging
import os
import urllib.request
import xml.etree.ElementTree as ET
from collections.abc import Iterable, Mapping
from datetime import datetime
from typing import Any

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
        """Prepare string representation."""
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
        """Check if object <= other."""
        return not self.__gt__(other)

    def __gt__(self, other: Bugreport) -> bool:
        """Check if object > other."""
        return self._get_value() > other._get_value()

    def __ge__(self, other: Bugreport) -> bool:
        """Check if object >= other."""
        return not self.__lt__(other)

    def __eq__(self, other: object) -> bool:
        """Check if object == other."""
        if not isinstance(other, Bugreport):
            return NotImplemented
        return self._get_value() == other._get_value()

    def __ne__(self, other: object) -> bool:
        """Check if object != other."""
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
    """Return a list of Bugreport objects.

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
    bugs = []
    for i in range(0, len(numbers), BATCH_SIZE):
        slice_ = numbers[i : i + BATCH_SIZE]
        result_dict = _soap_client_call(f"{{{NS}}}get_status", slice_)
        for bug in result_dict.values():
            bugs.append(_parse_status(bug))
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

    result = _soap_client_call(f"{{{NS}}}get_usertag", email, *tags)
    return {k: list(map(int, v)) for k, v in result.items()}


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
    items = _soap_client_call(f"{{{NS}}}get_bug_log", nr)
    buglogs = []
    for item in items:
        header = item["header"]
        body = item["body"]
        msg_num = int(item["msg_num"])
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
    """Return the newest bugs.

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
    result = _soap_client_call(f"{{{NS}}}newest_bugs", amount)
    return list(map(int, result))


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
    result = _soap_client_call(f"{{{NS}}}get_bugs", kwargs)
    return list(map(int, result))


def _parse_status(bug_el: dict[str, Any]) -> Bugreport:
    """Return a bugreport object from a given status xml element.

    Parameters
    ----------
    bug_el
        a dict containing a debbugs bug description

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
        "found_versions",
        "fixed_versions",
    ):
        setattr(bug, field, bug_el[field])

    bug.date = datetime.utcfromtimestamp(float(bug_el["date"]))
    bug.log_modified = datetime.utcfromtimestamp(float(bug_el["log_modified"]))
    bug.tags = str(bug_el["tags"]).split()
    bug.done = _parse_bool(bug_el["done"])
    bug.done_by = bug_el["done"] if bug.done else None
    bug.archived = _parse_bool(bug_el["archived"])
    bug.unarchived = _parse_bool(bug_el["unarchived"])
    bug.bug_num = int(bug_el["bug_num"])
    bug.mergedwith = [int(i) for i in str(bug_el["mergedwith"]).split()]
    bug.blockedby = [int(i) for i in str(bug_el["blockedby"]).split()]
    bug.blocks = [int(i) for i in str(bug_el["blocks"]).split()]

    affects = [_f for _f in str(bug_el["affects"]).split(",") if _f]
    bug.affects = [a.strip() for a in affects]

    # Also available, but unused or broken:
    # 'keywords', 'found', 'found_date', 'fixed', 'fixed_data'

    return bug


def _parse_bool(x: str) -> bool:
    """Parse a boolean value, according to Perl's rules.

    Parameters
    ----------
    x
        the string to parse

    Returns
    -------
    bool
        the parsed value

    """
    return x not in ("", "0")


_soap_client_kwargs = {
    "location": URL,
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
    """Set location URL for SOAP client.

    You may use this method after import to override the default URL.

    Parameters
    ----------
    url
        default URL

    """
    _soap_client_kwargs["location"] = url


def get_soap_client_kwargs() -> dict[str, str]:
    """Return SOAP client kwargs.

    Returns
    -------
    dict[str, str]
        the SOAP client kwargs

    """
    return _soap_client_kwargs


def _soap_client_call(method_name: str, *args: Any) -> Any:
    """Perform a SOAP request.

    Parameters
    ----------
    method_name
        the method name
    *args

    Returns
    -------
    Any

    """
    handlers = []
    if "proxy" in _soap_client_kwargs:
        handlers.append(
            urllib.request.ProxyHandler(
                proxies={
                    "http": _soap_client_kwargs["proxy"],
                    "https": _soap_client_kwargs["proxy"],
                }
            )
        )
    opener = urllib.request.build_opener(*handlers)

    encoded_request = _encode_soap_request(method_name, args)
    logger.debug("Request: %s", encoded_request)

    try:
        with opener.open(
            urllib.request.Request(
                url=_soap_client_kwargs["location"],
                method="POST",
                headers={
                    "Content-Type": 'text/xml; charset="utf-8"',
                    "SOAPAction": "",
                },
                data=encoded_request,
            )
        ) as f:
            encoded_response = f.read()
    except urllib.error.HTTPError as e:
        if e.headers.get("Content-Type", "").startswith("text/xml"):
            # It's probably a SOAP Fault response
            encoded_response = e.fp.read()
        else:
            raise

    logger.debug("Response: %s", encoded_response)
    return _decode_soap_response(encoded_response)


# XML namespaces
SOAPENV = "http://schemas.xmlsoap.org/soap/envelope/"
SOAPENC = "http://schemas.xmlsoap.org/soap/encoding/"
XSD = "http://www.w3.org/2001/XMLSchema"
XSI = "http://www.w3.org/2001/XMLSchema-instance"


def _encode_soap_request(method_name: str, args: Iterable[Any]) -> bytes:
    """Build a SOAP request.

    Parameters
    ----------
    method_name
        the function to call (including namespace)
    args
        the function arguments

    Returns
    -------
    bytes

    """
    root = ET.Element(f"{{{SOAPENV}}}Envelope")
    root.set(f"{{{SOAPENV}}}encodingStyle", SOAPENC)
    body = ET.SubElement(root, f"{{{SOAPENV}}}Body")
    msg = ET.SubElement(body, method_name)
    for arg in args:
        _encode_value(msg, "arg", arg)
    return ET.tostring(root)


def _decode_soap_response(response: bytes) -> Any:
    """Extract the returned value from a SOAP response.

    Parameters
    ----------
    response
        the response from the SOAP service

    Returns
    -------
    Any
        the returned value

    """
    root = ET.fromstring(response)

    fault = root.find(f"{{{SOAPENV}}}Body/{{{SOAPENV}}}Fault")
    if fault is not None:
        message_el = fault.find("faultstring")
        message = message_el.text if message_el is not None else "Unknown"
        raise RuntimeError(f"SOAP fault: {message}")

    answer = root.find(f"{{{SOAPENV}}}Body/*[1]/*[1]")
    if answer is None:
        return None
    return _decode_value(answer)


def _encode_value(parent: ET.Element, name: str, value: Any) -> None:
    """Append the encoded representation of a value to the parent element.

    Parameters
    ----------
    parent
        the parent element
    name
        the tag of the new element
    value
        the value to be encoded

    """
    if isinstance(value, str):
        el = ET.SubElement(parent, name)
        el.set(f"{{{XSI}}}type", ET.QName(XSD, "string"))
        el.text = str(value)
    elif isinstance(value, int):
        # This includes booleans, as bool is a subtype of int
        el = ET.SubElement(parent, name)
        el.set(f"{{{XSI}}}type", ET.QName(XSD, "int"))
        el.text = str(int(value))
    elif isinstance(value, Iterable):
        if isinstance(value, Mapping):
            # Flatten the dictionary
            value = [x for pair in value.items() for x in pair]
        el = ET.SubElement(parent, name)
        el.set(f"{{{XSI}}}type", ET.QName(SOAPENC, "Array"))
        el.set(
            f"{{{SOAPENC}}}arrayType",
            ET.QName(XSD, "anyType[%d]" % len(value)),
        )
        for x in value:
            _encode_value(el, "item", x)
    else:
        raise ValueError(f"Can't encode {value!r}")


def _decode_value(element: ET.Element) -> Any:
    """Decode an XML encoded representation.

    Note: Perl does not have separate types for strings and numbers.
    The server assigns a type based on heuristics. To get consistent
    behavior, this function returns all numeric values as strings.

    Parameters
    ----------
    element
        the XML element to decode

    Returns
    -------
    Any
        the decoded value

    """
    typ = element.get(f"{{{XSI}}}type")
    if typ:
        # ElementTree discards the original namespace prefixes, so we
        # can't decode QName values properly. Luckily this doesn't
        # cause ambiguities with the debbugs API.
        typ = typ[typ.find(":") + 1 :]

    text = element.text or ""
    if typ in ("string", "int", "float"):
        return text
    elif typ == "base64Binary":
        return base64.b64decode(text).decode("utf-8", errors="replace")
    elif typ == "Array":
        return [_decode_value(el) for el in element]
    elif typ == "Map":
        assert all(len(item) == 2 for item in element)
        return {
            _decode_value(item[0]): _decode_value(item[1]) for item in element
        }
    elif typ is None:
        return {
            _remove_namespace(item.tag): _decode_value(item)
            for item in element
        }
    else:
        raise ValueError(f"Can't decode {ET.tostring(element).decode()}")


def _remove_namespace(tag: str) -> str:
    """Remove the namespace from an ElementTree tag."""
    return tag[tag.find("}") + 1 :]
