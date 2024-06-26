# SPDX-FileCopyrightText: 2024 Nicco Kunzmann and Open Web Calendar Contributors <https://open-web-calendar.quelltext.eu/>
#
# SPDX-License-Identifier: GPL-2.0-only

import os
import sys
import pytest
from unittest.mock import Mock
import requests

# constants
HERE = os.path.dirname(__file__) or "."
CALENDAR_DIRECTORY = os.path.join(HERE, "..", "features", "calendars")

# relative imports
sys.path.append(os.path.join(os.path.abspath(HERE), ".."))
sys.path.append(os.path.abspath(HERE))
from app import cache_url


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    """Prevent requests from sending out requests

    See https://docs.pytest.org/en/latest/monkeypatch.html#example-preventing-requests-from-remote-operations
    """
    def test_cannot_call_outside(*args, **kw):
        raise RuntimeError("Tests are not allowed to make requests to the"
                           " Internet. You can use cache_url() to mock that.")
    monkeypatch.setattr(requests.sessions.Session, "request", test_cannot_call_outside)


@pytest.fixture()
def mock():
    return Mock()


@pytest.fixture()
def app():
    """Create the app.

    See https://flask.palletsprojects.com/en/2.2.x/testing/
    """
    from app import app
    app.config.update({
        "TESTING": True,
    })

    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


calendar_files = {}
for file in os.listdir(CALENDAR_DIRECTORY):
    with open(os.path.join(CALENDAR_DIRECTORY, file)) as f:
        calendar_files[file] = f.read()


@pytest.fixture()
def calendar_urls():
    """Mapping the calendar name without .ics to the cached url.

    The files are located in the CALENDAR_FOLDER.
    """
    mapping = {}
    for file, content in calendar_files.items():
        url = "http://test.examples.local/" + file
        cache_url(url, content)
        mapping[file] = url
        if file.lower().endswith(".ics"):
            mapping[file[:-4]] = url
    return mapping


@pytest.fixture()
def calendar_content():
    """Mapping the calendar name without .ics to the calendar content.

    The files are located in the CALENDAR_FOLDER.
    """
    mapping = {}
    for file, content in calendar_files.items():
        if file.lower().endswith(".ics"):
            mapping[file[:-4]] = content
    return mapping
