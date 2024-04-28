"""Tests for SOAP calls."""


import xml.etree.ElementTree as ET

import pytest

from debianbts.debianbts import (
    _decode_soap_response,
    _decode_value,
    _encode_soap_request,
    _encode_value,
)


def test_encode_value() -> None:
    """Test that Python data is correctly encoded to XML."""
    value = {
        "String": "hello world",
        "Integer": 123,
        "Boolean": True,
        "List": ["a", "b"],
    }

    expected = """
        <root
            xmlns:ns1="http://schemas.xmlsoap.org/soap/encoding/"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:xs="http://www.w3.org/2001/XMLSchema"
        >
            <value xsi:type="ns1:Array" ns1:arrayType="xs:anyType[8]">
                <item xsi:type="xs:string">String</item>
                <item xsi:type="xs:string">hello world</item>
                <item xsi:type="xs:string">Integer</item>
                <item xsi:type="xs:int">123</item>
                <item xsi:type="xs:string">Boolean</item>
                <item xsi:type="xs:int">1</item>
                <item xsi:type="xs:string">List</item>
                <item xsi:type="ns1:Array" ns1:arrayType="xs:anyType[2]">
                    <item xsi:type="xs:string">a</item>
                    <item xsi:type="xs:string">b</item>
                </item>
            </value>
        </root>
    """
    expected = ET.canonicalize(expected, strip_text=True)

    root = ET.Element("root")
    _encode_value(root, "value", value)
    actual = ET.canonicalize(ET.tostring(root))

    assert actual == expected


def test_decode_value() -> None:
    """Test that XML data is correctly decoded."""
    xml = ET.fromstring(
        """
        <root
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:xs="http://www.w3.org/2001/XMLSchema"
            xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/"
            xmlns:apachens="http://xml.apache.org/xml-soap"
        >
            <value xsi:type="soapenc:Array" soapenc:arrayType="xs:anyType[6]">
                <item xsi:type="xs:string">hello world</item>
                <item xsi:type="xs:base64Binary">YmluYXJ5IGRhdGE=</item>
                <item xsi:type="xs:int">123</item>
                <gensym xsi:type="apachens:Map">
                    <item>
                        <key xsi:type="xs:string">a</key>
                        <value xsi:type="xs:int">1</value>
                    </item>
                    <item>
                        <key xsi:type="xs:string">b</key>
                        <value xsi:type="xs:int">2</value>
                    </item>
                </gensym>
                <gensym>
                    <c xsi:type="xs:int">3</c>
                    <d xsi:type="xs:int">4</d>
                </gensym>
            </value>
        </root>
        """
    )

    expected = [
        "hello world",
        "binary data",
        "123",
        {"a": "1", "b": "2"},
        {"c": "3", "d": "4"},
    ]

    actual = _decode_value(xml[0])
    assert actual == expected


def test_encode_soap_request() -> None:
    """Test that SOAP requests can be encoded."""
    expected = """
        <ns0:Envelope
            xmlns:ns0="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:ns1="Debbugs/SOAP/V1"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:xs="http://www.w3.org/2001/XMLSchema"
            ns0:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
        >
            <ns0:Body>
                <ns1:newest_bugs>
                    <arg xsi:type="xs:int">123</arg>
                </ns1:newest_bugs>
            </ns0:Body>
        </ns0:Envelope>
    """
    expected = ET.canonicalize(expected, strip_text=True)
    actual = ET.canonicalize(
        _encode_soap_request("{Debbugs/SOAP/V1}newest_bugs", [123])
    )
    assert actual == expected


def test_decode_soap_response() -> None:
    """Test that SOAP responses can be decoded."""
    xml = b"""
         <soap:Envelope
            xmlns:ns1="Debbugs/SOAP"
            xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:xs="http://www.w3.org/2001/XMLSchema"
         >
             <soap:Body>
                 <ns1:someResponse>
                    <return xsi:type="xs:string">abc</return>
                 </ns1:someResponse>
             </soap:Body>
         </soap:Envelope>
    """
    assert _decode_soap_response(xml) == "abc"


def test_decode_soap_fault_response() -> None:
    """Test that SOAP fault responses raise an exception."""
    xml = b"""
         <soap:Envelope
            xmlns:ns1="Debbugs/SOAP/V1"
            xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:xs="http://www.w3.org/2001/XMLSchema"
         >
             <soap:Body>
                 <soap:Fault>
                     <faultcode>123</faultcode>
                     <faultstring>Some error message</faultstring>
                 </soap:Fault>
             </soap:Body>
         </soap:Envelope>
    """
    with pytest.raises(RuntimeError) as excinfo:
        _decode_soap_response(xml)
    assert "Some error message" in str(excinfo.value)
