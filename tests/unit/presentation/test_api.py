import json
import logging

from nose.tools import with_setup, eq_
from mock import patch
from flask import url_for

from metadome.factory import create_app


_log = logging.getLogger(__name__)


@patch("metadome.database.db")
def setup(mock_db):
    global server
    global client

    class FakeDB:
        def init_app(self, app):
            pass

        def create_all(self):
            pass
    mock_db.return_value = FakeDB()

    server = create_app({'SERVER_NAME': "test-server",
                         'TESTING': True,
                         'SECRET_KEY': 'testing'})
    client = server.test_client()


def teardown():
    pass


@with_setup(setup, teardown)
@patch("metadome.tasks.retrieve_metadomain_annotation")
def test_get_metadomain_annotation(mock_retrieve):
    global server
    global client

    mock_retrieve.return_value = {}

    input_ = {
        'transcript_id': 'test',
        'protein_position': 1,
        'requested_domains': {}
    }

    with server.app_context():
        r = client.post(url_for('api.get_metadomain_annotation'),
                        data=json.dumps(input_),
                        content_type="application/json")

    eq_(r.status_code, 200)
