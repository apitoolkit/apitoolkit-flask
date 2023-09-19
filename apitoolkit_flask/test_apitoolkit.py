from flask import Flask, request, jsonify
from werkzeug.test import Client
import sys
from . import APIToolkit
import base64
import json

app = Flask(__name__)
app.config.update({
    "TESTING": True,
})

redact_req = ["$.credit-card.cvv", "$.credit-card.name", "$.password"]
redact_headers = ["authorization", "content-type", "connection"]
exampleDataRedaction = [
    "$.status", "$.data.account_data.account_type",
    "$.data.account_data.possible_account_types",
    "$.data.account_data.possible_account_types2[*]",
    "$.non_existent",
]

apitoolkit = APIToolkit(
    api_key="<API_KEY>",
    root_url="http://localhost:8080",
    redact_headers=redact_headers,
    redact_request_body=redact_req,
    redact_response_body=exampleDataRedaction,
    debug=True
)


def publish_message(payload):
    assert_response(payload['method'], "POST")
    assert_response(payload['response_headers']
                    ['Content-Type'], "[CLIENT_REDACTED]")
    assert_response(payload['request_headers']
                    ['Authorization'], "[CLIENT_REDACTED]")
    assert_response(payload['url_path'], '/hello/<name>')
    assert_response(payload['raw_url'], '/hello/john?foo=bar')
    assert_response(payload['status_code'], 200)
    assert_response(json.dumps(
        payload['query_params']), json.dumps({"foo": "bar"}))
    assert_response(json.dumps(
        payload['query_params']), json.dumps({"foo": "bar"}))
    assert_response(json.dumps(
        payload['path_params']), json.dumps({"name": "john"}))
    assert_response(base64_json_to_dict(
        payload['request_body']), exampleRequestData)
    assert_response(base64_json_to_dict(
        payload['response_body']), exampleDataRedacted)


apitoolkit.publish_message = publish_message


@app.before_request
def before_request():
    apitoolkit.beforeRequest()


@app.after_request
def after_request(response):
    apitoolkit.afterRequest(response)
    return response


@app.route("/hello/<name>", methods=["POST"])
def read_main(name):
    return jsonify(exampleResponseData)


client = Client(app)


def test_read_main():
    response = client.post("/hello/john?foo=bar", json=exampleRequestData,
                           headers={"Authorization": "Bearer abc123", "X-Val": "foo"})
    assert response.status_code == 200
    assert response.get_json() == exampleResponseData


def assert_response(expected, actual):
    if not expected == actual:
        sys.exit(f"Expected {expected} but got {actual}")


exampleResponseData = {
    "status": "success",
    "data": {
        "message": "hello world",
        "account_data": {
            "batch_number": 12345,
            "account_id": "123456789",
            "account_name": "test account",
            "account_type": "test",
            "account_status": "active",
            "account_balance": "100.00",
            "account_currency": "USD",
            "account_created_at": "2020-01-01T00:00:00Z",
            "account_updated_at": "2020-01-01T00:00:00Z",
            "account_deleted_at": "2020-01-01T00:00:00Z",
            "possible_account_types": ["test", "staging", "production"],
            "possible_account_types2": ["test", "staging", "production"],
        },
    },
}

exampleDataRedaction = [
    "$.status", "$.data.account_data.account_type",
    "$.data.account_data.possible_account_types",
    "$.data.account_data.possible_account_types2[*]",
    "$.non_existent",
]

exampleDataRedacted = {
    "status": "[CLIENT_REDACTED]",
    "data": {
        "message": "hello world",
        "account_data": {
            "batch_number": 12345,
            "account_id": "123456789",
            "account_name": "test account",
            "account_type": "[CLIENT_REDACTED]",
            "account_status": "active",
            "account_balance": "100.00",
            "account_currency": "USD",
            "account_created_at": "2020-01-01T00:00:00Z",
            "account_updated_at": "2020-01-01T00:00:00Z",
            "account_deleted_at": "2020-01-01T00:00:00Z",
            "possible_account_types": "[CLIENT_REDACTED]",
            "possible_account_types2": ["[CLIENT_REDACTED]", "[CLIENT_REDACTED]", "[CLIENT_REDACTED]"],
        },
    },
}

exampleRequestData = {
    "status": "request",
    "send": {
        "message": "hello world",
        "account_data": [{
            "batch_number": 12345,
            "account_id": "123456789",
            "account_name": "test account",
            "account_type": "test",
            "account_status": "active",
            "account_balance": "100.00",
            "account_currency": "USD",
            "account_created_at": "2020-01-01T00:00:00Z",
            "account_updated_at": "2020-01-01T00:00:00Z",
            "account_deleted_at": "2020-01-01T00:00:00Z",
            "possible_account_types": ["test", "staging", "production"],
        }],
    },
}


def base64_json_to_dict(base64_encoded_str):
    try:
        # Decode the base64 string
        decoded_bytes = base64.b64decode(base64_encoded_str)
        # Convert bytes to a JSON string
        json_str = decoded_bytes.decode('utf-8')
        # Parse JSON string to a dictionary
        data_dict = json.loads(json_str)
        return data_dict
    except (base64.binascii.Error, json.JSONDecodeError):
        # Handle decoding or parsing errors
        return {}
