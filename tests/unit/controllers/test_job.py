from shutil import rmtree
from threading import Thread
from tempfile import mkdtemp
from time import sleep
import json
import logging
import os
import traceback

from nose.tools import with_setup, ok_
from mock import patch

from metadome.factory import create_app
from metadome.controllers.job import (create_visualization_job_if_needed,
                                      get_visualization_status,
                                      retrieve_visualization, retrieve_error,
                                      get_visualization_path,
                                      store_visualization, store_error)


_log = logging.getLogger(__name__)


@patch("metadome.database.db.create_all")
def setup(mock_create_all):
    global temp_dir
    temp_dir = mkdtemp()

    global app
    mock_create_all.return_value = None
    app = create_app()


def teardown():
    global temp_dir
    if os.path.isdir(temp_dir):
        rmtree(temp_dir)


@with_setup(setup, teardown)
@patch("metadome.tasks.create_prebuild_visualization.delay")
@patch("celery.result.AsyncResult")
@patch("metadome.controllers.job._get_visualization_dir_path")
def test_run(mock_dir_path, mock_result, mock_delay):
    global temp_dir
    mock_dir_path.return_value = temp_dir

    class ThreadResult(Thread):
        def __init__(self, transcript_id):
            Thread.__init__(self)
            self.name = "resutl_test"
            self.transcript_id = transcript_id
            self.status = "PENDING"

        def run(self):
            self.status = "STARTED"
            try:
                sleep(5.0)
                global app
                with app.app_context():
                    store_visualization(self.transcript_id, {'id': 'test'})
                self.status = "SUCCESS"
            except:
                with app.app_context():
                    store_error(self.transcript_id, traceback.format_exc())
                self.status = "FAILURE"

    transcript_id = "test_transcript"

    result_thread = ThreadResult(transcript_id)
    mock_result.return_value = result_thread
    mock_delay.return_value = result_thread

    global app
    with app.app_context():
        create_visualization_job_if_needed(transcript_id)
        result_thread.start()

        while True:
            status = get_visualization_status(transcript_id)
            ok_(status != 'FAILURE')

            if status == 'SUCCESS':
                break
            else:
                sleep(1.0)

        result = retrieve_visualization(transcript_id)

        ok_(len(result) > 0)
        ok_(os.path.isfile(get_visualization_path(transcript_id)))
