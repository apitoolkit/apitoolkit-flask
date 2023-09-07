from flask import request, g
import requests  # type: ignore
from google.cloud import pubsub_v1
from google.oauth2 import service_account  # type: ignore
import json
import base64
import time


class APIToolkit:
    def __init__(self, api_key,  debug, redact_headers=["Authorization", "Cookie"]):
        self.debug = debug
        self.publisher = None
        self.topic_name = None
        self.meta = None
        self.redact_headers = redact_headers

        try:
            response = requests.get(
                url="https://app.apitoolkit.io/api/client_metadata", headers={"Authorization": f"Bearer {api_key}"})
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
        except Exception as e:
            print(f"Error fetching meta data: {str(e)}")

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

    def beforeRequest(self):
        request_method = request.method
        raw_url = request.full_path
        url_path = request.url_rule.rule
        request_body = None
        query_params = request.args.copy().to_dict()
        path_params = request.view_args.copy()
        request_headers = self.redact_headers_func(dict(request.headers))

        if request.content_type == 'application/json':
            request_body = request.get_json()

        if request.content_type == 'application/x-www-form-urlencoded':
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

    def afterRequest(self, response):
        end_time = time.perf_counter_ns()
        apitoolkit_request_data = g.get("apitoolkit_request_data", {})
        duration = (end_time - apitoolkit_request_data.get("start_time", 0))
        status_code = response.status_code
        request_body = json.dumps(
            apitoolkit_request_data.get("request_body", {}))
        headers = self.redact_headers_func(dict(response.headers))
        content = response.data
        payload = {
            "query_params": apitoolkit_request_data["query_params"],
            "path_params": apitoolkit_request_data["path_params"],
            "request_headers": apitoolkit_request_data.get("request_headers", {}),
            "response_headers": dict(headers),
            "proto_minor": 1,
            "proto_major": 1,
            "method": apitoolkit_request_data.get("method", ""),
            "url_path": apitoolkit_request_data.get("url_path", ""),
            "raw_url": apitoolkit_request_data.get("raw_url", ""),
            "request_body": base64.b64encode(request_body.encode('utf-8')).decode("utf-8"),
            "response_body": base64.b64encode(content.decode('utf-8').encode('utf-8')).decode("utf-8"),
            "host": apitoolkit_request_data.get("host", ""),
            "referer": apitoolkit_request_data.get("referer", ""),
            "sdk_type": "PythonFlask",
            "project_id": self.meta["project_id"],
            "status_code": status_code,
            "duration": duration,
        }
        self.publish_message(payload)
