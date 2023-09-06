# API Toolkit Python Flask SDK

The API Toolkit Flask client is an sdk used to integrate flask web services with APIToolkit.
It monitors incoming traffic, gathers the requests and sends the request to the apitoolkit servers.

## Design decisions:

- Use the gcp SDK to send real time traffic from REST APIs to the gcp topic

## How to Integrate:

First install the apitoolkit Go sdk:
`pip install apitoolkit-flask`

Then add apitoolkit to your app like so (flask example):

```python
from flask import Flask
from apitoolkit import APIToolkit

app = Flask(__name__)

apitoolkit = APIToolkit(api_key="<API_KEY>", debug=True)


@app.before_request
def before_request():
    apitoolkit.beforeRequest()

@app.after_request
def after_request(response):
    apitoolkit.afterRequest(response)
    return response


@app.route('/hello', methods=['GET', 'POST'])
def sample_route(subject):
    return {"Hello": "World"}

app.run(debug=True)

```

This will monitor all requests and send metadata to the API Toolkit dashboard.
