# Har2Document-Django

![Build](https://github.com/8percent/python-library/actions/workflows/ci.yml/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/8percent/python-library/master.svg)](https://results.pre-commit.ci/latest/github/8percent/python-library/master)

Har2Document-Django is a plugin for the [`har2document`](https://github.com/8percent/har2document) package, providing enhanced functionality when combined with Django.

Support for Python 3.10 and later, Django 3.2 and later versions.

---

## Features

- **Django Integration**: Seamlessly integrates with Django to provide detailed API documentation.
- **Enhanced URL Analysis**: Extracts and displays Django View functions or class names from URLs.
- **Path Parameter Insights**: Offers detailed information about path parameters in your Django application.
- **Masking Feature**: Offers the ability to mask sensitive information in the documentation, such as passwords and phone numbers.
- **Export to CSV and Markdown**: Allows exporting the generated documentation to both CSV and Markdown formats, enabling flexible documentation management.

---

## Usage

```python
from har2document_django import run

har_file_path = "/your/har/file/path.har"
masking_mapping = {
    "mypassword": "1q2w3e4r",  # password
    "01012345678": "010********",  # phone number
}

run(
    har_file_path,
    masking_mapping,
    csv=True,  # Save the result as a CSV file
    markdown=True,  # Save the result as a Markdown file
)
```

When you execute this code, it will process the specified HAR file and generate documentation. If csv or markdown is set to True, the respective CSV and Markdown files will be created. These files will be saved in the same directory as the provided HAR file.

---

## Installation

To install Har2Document-Django, you can use pip to install directly from the GitHub repository. Run the following command in your terminal:

```shell
pip install git+https://github.com/8percent/har2document-django.git
```

---

## Contributing
Pull requests are always welcome.

Check CONTRIBUTING.md for more details.

---

## License
Distributed under the terms of the MIT license.
