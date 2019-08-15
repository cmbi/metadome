import os
import shutil
from time import sleep
import tempfile

from nose.tools import with_setup, eq_
from mock import patch

from metadome.factory import create_app, make_celery


def setup_lazy():
    flask_app = create_app({'TESTING': True,
                            'CELERYD_CONCURRENCY': 0})  # do nothing
    make_celery(flask_app)


prebuild_dir = None

def setup_normal():
    global prebuild_dir
    prebuild_dir = tempfile.mkdtemp()

    flask_app = create_app({'TESTING': True,
                            'PRE_BUILD_VISUALIZATION_DIR': prebuild_dir})
    make_celery(flask_app)


def cleanup():
    if os.path.isfile(prebuild_dir):
        shutil.rmtree(prebuild_dir)


@with_setup(setup_lazy, cleanup)
@patch("metadome.tasks.analyse_transcript")
def test_update_sent_state(mock_analyse):
    mock_analyse.return_value = {'test': "ok"}

    from metadome.tasks import retrieve_prebuild_visualization
    result = retrieve_prebuild_visualization.delay('test_id')

    eq_(result.status, 'SENT')


@with_setup(setup_normal, cleanup)
def test_create_visualization():
    transcript_id = "ENST00000311502.7"

    from metadome.tasks import create_prebuild_visualization

    result = create_prebuild_visualization.delay(transcript_id)

    status = result.status
    while status in ['SENT', 'PENDING', 'STARTED']:
        sleep(1)
        status = result.status

    eq_(status, 'SUCCESS')
