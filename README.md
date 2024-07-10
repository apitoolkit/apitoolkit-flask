<div align="center">

![APItoolkit's Logo](https://github.com/apitoolkit/.github/blob/main/images/logo-white.svg?raw=true#gh-dark-mode-only)
![APItoolkit's Logo](https://github.com/apitoolkit/.github/blob/main/images/logo-black.svg?raw=true#gh-light-mode-only)

## Flask SDK

[![APItoolkit SDK](https://img.shields.io/badge/APItoolkit-SDK-0068ff?logo=flask)](https://github.com/topics/apitoolkit-sdk) [![PyPI - Version](https://img.shields.io/pypi/v/apitoolkit-flask)](https://pypi.org/project/apitoolkit-flask) [![PyPI - Downloads](https://img.shields.io/pypi/dw/apitoolkit-flask)](https://pypi.org/project/apitoolkit-flask) [![Join Discord Server](https://img.shields.io/badge/Chat-Discord-7289da)](https://apitoolkit.io/discord?utm_campaign=devrel&utm_medium=github&utm_source=sdks_readme) [![APItoolkit Docs](https://img.shields.io/badge/Read-Docs-0068ff)](https://apitoolkit.io/docs/sdks/python/flask?utm_campaign=devrel&utm_medium=github&utm_source=sdks_readme) 

APItoolkit is an end-to-end API and web services management toolkit for engineers and customer support teams. To integrate your Flask (Python) application with APItoolkit, you need to use this SDK to monitor incoming traffic, aggregate the requests, and then deliver them to the APItoolkit's servers.

</div>

---

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Contributing and Help](#contributing-and-help)
- [License](#license)

---

## Installation

Kindly run the command below to install the SDK:

```sh
pip install apitoolkit-flask
```

## Configuration

Next, initialize APItoolkit in your application's entry point (e.g., `main.py`), like so:

```python
from flask import Flask
from apitoolkit_flask import APIToolkit

app = Flask(__name__)

# Initialize APItoolkit
apitoolkit = APIToolkit(
    api_key = "{ENTER_YOUR_API_KEY_HERE}",
    debug = False,
    tags = ["environment: production", "region: us-east-1"],
    service_version = "v2.0"
)

@app.before_request
def before_request():
    apitoolkit.beforeRequest()

@app.after_request
def after_request(response):
    apitoolkit.afterRequest(response)
    return response
# END Initialize APItoolkit

@app.route('/hello', methods=['GET', 'POST'])
def sample_route():
    return {"Hello": "World"}

app.run(debug=True)
```

> [!NOTE]
> 
> The `{ENTER_YOUR_API_KEY_HERE}` demo string should be replaced with the [API key](https://apitoolkit.io/docs/dashboard/settings-pages/api-keys?utm_campaign=devrel&utm_medium=github&utm_source=sdks_readme) generated from the APItoolkit dashboard.

<br />

> [!IMPORTANT]
> 
> To learn more configuration options (redacting fields, error reporting, outgoing requests, etc.), please read this [SDK documentation](https://apitoolkit.io/docs/sdks/python/flask?utm_campaign=devrel&utm_medium=github&utm_source=sdks_readme).

## Contributing and Help

To contribute to the development of this SDK or request help from the community and our team, kindly do any of the following:
- Read our [Contributors Guide](https://github.com/apitoolkit/.github/blob/main/CONTRIBUTING.md).
- Join our community [Discord Server](https://apitoolkit.io/discord?utm_campaign=devrel&utm_medium=github&utm_source=sdks_readme).
- Create a [new issue](https://github.com/apitoolkit/apitoolkit-flask/issues/new/choose) in this repository.

## License

This repository is published under the [MIT](LICENSE) license.

---

<div align="center">
    
<a href="https://apitoolkit.io?utm_campaign=devrel&utm_medium=github&utm_source=sdks_readme" target="_blank" rel="noopener noreferrer"><img src="https://github.com/apitoolkit/.github/blob/main/images/icon.png?raw=true" width="40" /></a>

</div>
