import requests
import os
from xml.sax.saxutils import escape
import xml.etree.ElementTree as ET

# Public Functions

def get_session_id(username, password, security_token):
    """
    Authenticates with Salesforce and retrieves a session ID.

    :param username: The Salesforce username.
    :param password: The Salesforce password.
    :param security_token: The Salesforce security token.
    :return: The Salesforce session ID.
    :rtype: str
    :raises Exception: If the authentication request fails or the session ID is not found.
    """
    response = requests.post(
        get_url(), 
        data=get_body(username, password, security_token), 
        headers=get_headers()
        )
    if response.status_code != 200:
        raise Exception(f"Authentication failed with status code {
                        response.status_code}: {response.text}")
    session_id = extract_session_id(response.text)
    return session_id

# Private Functions

def escape_chars(string):
    """
    Escapes special XML characters in a string to ensure valid XML formatting.

    :param string: The string to escape.
    :return: The escaped string.
    """
    extra_entities = {"'": "&apos;", '"': "&quot;"}
    escaped_string = escape(string, extra_entities)
    return escaped_string


def get_body(username, password, security_token):
    """
    Constructs the XML body for the Salesforce SOAP login request.

    :param username: The Salesforce username.
    :param password: The Salesforce password.
    :param security_token: The Salesforce security token.
    :return: The XML-formatted body for the login request.
    """
    formatted_password = escape_chars(password)
    formatted_secutiry_token = escape_chars(security_token)
    return f"""<?xml version=\"1.0\" encoding=\"utf-8\" ?>
    <env:Envelope xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\"
        xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"
        xmlns:env=\"http://schemas.xmlsoap.org/soap/envelope/\">
      <env:Body>
        <n1:login xmlns:n1=\"urn:partner.soap.sforce.com\">
          <n1:username>{username}</n1:username>
          <n1:password>{formatted_password}{formatted_secutiry_token}</n1:password>
        </n1:login>
      </env:Body>
    </env:Envelope>"""


def get_url():
    url = f"{os.environ["SALESFORCE_URL"]}/services/Soap/u/60.0"
    return url


def get_headers():
    headers = {
        'SOAPAction': 'login',
        'Content-Type': 'text/xml',
        'charset': 'UTF-8'
    }
    return headers


def extract_session_id(xml_str):
    """
    Parses the Salesforce SOAP response XML to extract the session ID.

    :param xml_str: The XML response as a string.
    :return: The extracted session ID, or None if not found.
    :raises ET.ParseError: If the XML parsing fails.
    """
    namespaces = {
        'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
        'ns': 'urn:partner.soap.sforce.com'
    }

    root = ET.fromstring(xml_str)
    session_id_elem = root.find(
        './/soapenv:Body/ns:loginResponse/ns:result/ns:sessionId', namespaces)

    if session_id_elem is not None:
        return session_id_elem.text
    else:
        print("sessionId not found in the response.")
        return None
