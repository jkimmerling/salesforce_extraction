import requests
import json
import os

from salesforce_authentication import get_session_id
from helper_functions import get_credentials, get_nested_values

# Public Functions


def get_records_list(object_name, fields=None, limit=None):
    """
    Retrieves a list of records based on the specified object name, fields, and limit.

    :param object_name: The name of the object to query.
    :param fields: A list of fields to include in the results. If None, all fields are retrieved.
    :param limit: The maximum number of records to retrieve. If None, no limit is applied.
    :return: A list of dictionaries representing the filtered records.
    """
    if not fields and not limit:
        fields = get_field_names(object_name)
    query = get_query(object_name, fields, limit)
    raw_results = get_rest_query_results(query)

    return [
        {k: v for k, v in d.items() if k != "attributes"}
        for d in raw_results
    ]

# Private Functions


def get_query(object_name, fields=None, limit=None):
    """
    Constructs a SOQL query string based on the provided object name, fields, and limit.

    :param object_name: The name of the Salesforce object to query.
    :param fields: A list of fields to include in the SELECT clause. If None, a special FIELDS(ALL) clause is used.
    :param limit: The maximum number of records to retrieve. If None, no LIMIT clause is added.
    :return: A SOQL query string.
    :raises Exception: If neither fields nor limit is provided.
    """
    if not fields and not limit:
        raise Exception(
            "If limit is not provided, you MUST provide a list of fields")
    fields_string = ",".join(fields) if fields else "FIELDS(ALL)"
    limit_string = f"+LIMIT+{limit}" if limit else ""
    return f"queryAll/?q=SELECT+{fields_string}+FROM+{object_name}{limit_string}"


def get_rest_query_results(query, next_url=None):
    """
    Executes a REST API GET request to Salesforce with the given query.
    Handles pagination recursively by checking for 'nextRecordsUrl' in the response.

    :param query: The SOQL query string to execute.
    :param next_url: The nextRecordsUrl for pagination (used internally during recursion).
    :return: A list of all records retrieved from Salesforce.
    :raises Exception: If the REST query fails with a non-200 status code.
    """

    if next_url is None:
        url = f"{os.environ['SALESFORCE_URL']} \
                /services/data/v60.0/{query}"
    else:
        url = f"{os.environ['SALESFORCE_URL']}{next_url}"

    response = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {fetch_session_id()}",
            "Content-Type": "application/json"
        }
    )

    if response.status_code != 200:
        raise Exception(f"REST query failed with a status of \
                        {response.status_code}: {response.text}")

    data = response.json()

    records = data.get("records", [])

    # Recursively fetch more records if 'nextRecordsUrl' is present
    if "nextRecordsUrl" in data:
        next_records = get_rest_query_results(
            query, next_url=data['nextRecordsUrl'])
        records.extend(next_records)

    return records


def get_field_names(object_name):
    """
    Retrieves all field names for the specified Salesforce object.

    :param object_name: The name of the Salesforce object to describe.
    :return: A list of field names for the object.
    :raises Exception: If the field name query fails with a non-200 status code.
    """
    response = requests.get(
        f"{os.environ["SALESFORCE_URL"]
           }/services/data/v60.0/sobjects/{object_name}/describe/",
        headers={
            "Authorization": f"Bearer {fetch_session_id()}"
        }
    )
    if response.status_code != 200:
        raise Exception(f"Field name query failed with a status of {
                        response.status_code}: {response.text}")
    return get_nested_values("name", response.json()["fields"])


def fetch_session_id():
    """
    Fetches the current Salesforce session ID using stored credentials.

    :return: The Salesforce session ID as a string.
    """
    credentials = get_credentials("salesforce")
    return get_session_id(
        credentials["salesforce_username"],
        credentials["salesforce_password"],
        credentials["salesforce_security_token"]
    )
