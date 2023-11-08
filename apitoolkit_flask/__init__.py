import uuid
from flask import request, g
import requests  # type: ignore
from google.cloud import pubsub_v1
from google.oauth2 import service_account  # type: ignore
from jsonpath_ng import parse  # type: ignore
import json
import base64
import time
from datetime import datetime
import pytz  # type: ignore
from apitoolkit_python import observe_request, report_error


class APIToolkit:
    def __init__(self, api_key, root_url="https://app.apitoolkit.io", redact_headers=["Authorization", "Cookie"], redact_request_body=[], redact_response_body=[], debug=False, service_version=None, tags=[]):
        self.debug = debug
        self.publisher = None
        self.topic_name = None
        self.meta = None
        self.redact_headers = redact_headers
        self.redact_request_body = redact_request_body
        self.redact_response_body = redact_response_body
        self.service_version = service_version
        self.tags = tags
        response = requests.get(
            url=root_url + "/api/client_metadata", headers={"Authorization": f"Bearer {api_key}"})
        response.raise_for_status()
        data = response.json()
        credentials = service_account.Credentials.from_service_account_info(
            data["pubsub_push_service_account"])
        self.publisher = pubsub_v1.PublisherClient(credentials=credentials)
        self.topic_name = 'projects/{project_id}/topics/{topic}'.format(
            project_id=data['pubsub_project_id'],
            topic=data['topic_id'],
        )
        self.meta = data

    def getInfo(self):
        return {"project_id": self.meta["project_id"], "service_version": self.service_version, "tags": self.tags}

    def publish_message(self, payload):
        data = json.dumps(payload).encode('utf-8')
        if self.debug:
            print("APIToolkit: publish message")
            json_formatted_str = json.dumps(payload, indent=2)
            print(json_formatted_str)
        future = self.publisher.publish(self.topic_name, data=data)
        return future.result()

    def redact_headers_func(self, headers):
        redacted_headers = {}
        for header_name, value in headers.items():
            if header_name.lower() in self.redact_headers or header_name in self.redact_headers:
                redacted_headers[header_name] = "[CLIENT_REDACTED]"
            else:
                redacted_headers[header_name] = value
        return redacted_headers

    def redact_fields(self, body, paths):
        try:
            data = json.loads(body)
            for path in paths:
                expr = parse(path)
                expr.update(data, "[CLIENT_REDACTED]")
            return json.dumps(data).encode("utf-8")
        except Exception as e:
            if isinstance(body, str):
                return body.encode('utf-8')
            return body

    def beforeRequest(self):
        if self.debug:
            print("APIToolkit: beforeRequest")
        request_method = request.method
        raw_url = request.full_path
        url_path = request.url_rule.rule
        request_body = None
        query_params = request.args.copy().to_dict()
        path_params = request.view_args.copy()
        request_headers = self.redact_headers_func(dict(request.headers))
        content_type = request.headers.get('Content-Type', '')

        if content_type == 'application/json':
            request_body = request.get_json()
        if content_type == 'text/plain':
            request_body = request.get_data().decode('utf-8')
        if content_type == 'application/x-www-form-urlencoded' or 'multipart/form-data' in content_type:
            request_body = request.form.copy().to_dict()

        g.apitoolkit_request_data = {
            "query_params": query_params,
            "path_params": path_params,
            "request_headers": request_headers,
            "method": request_method,
            "url_path": url_path,
            "raw_url": raw_url,
            "request_body": request_body,
            "start_time":  time.perf_counter_ns(),
            "host": request.host,
            "referer": request.headers.get('Referer', "")
        }
        request.apitoolkit_message_id = str(uuid.uuid4())
        request.apitoolkit_errors = []
        request.apitoolkit_client = self

    def afterRequest(self, response):
        if self.debug:
            print("APIToolkit: afterRequest")
        end_time = time.perf_counter_ns()
        apitoolkit_request_data = g.get("apitoolkit_request_data", {})
        duration = (end_time - apitoolkit_request_data.get("start_time", 0))
        status_code = response.status_code
        request_body = json.dumps(
            apitoolkit_request_data.get("request_body", {}))
        response_headers = self.redact_headers_func(dict(response.headers))
        request_body = self.redact_fields(
            request_body, self.redact_request_body)
        response_body = self.redact_fields(
            response.data, self.redact_response_body)
        timezone = pytz.timezone("UTC")
        timestamp = datetime.now(timezone).isoformat()
        message_id = request.apitoolkit_message_id
        try:
            payload = {
                "query_params": apitoolkit_request_data["query_params"],
                "path_params": apitoolkit_request_data["path_params"],
                "request_headers": apitoolkit_request_data.get("request_headers", {}),
                "response_headers": response_headers,
                "proto_minor": 1,
                "proto_major": 1,
                "method": apitoolkit_request_data.get("method", ""),
                "url_path": apitoolkit_request_data.get("url_path", ""),
                "raw_url": apitoolkit_request_data.get("raw_url", ""),
                "request_body": base64.b64encode(request_body).decode("utf-8"),
                "response_body": base64.b64encode(response_body).decode("utf-8"),
                "host": apitoolkit_request_data.get("host", ""),
                "referer": apitoolkit_request_data.get("referer", ""),
                "sdk_type": "PythonFlask",
                "project_id": self.meta["project_id"],
                "status_code": status_code,
                "msg_id": message_id,
                "errors": request.apitoolkit_errors or [],
                "duration": duration,
                "parent_id": None,
                "timestamp": timestamp
            }
            self.publish_message(payload)
        except Exception as e:
            return None
