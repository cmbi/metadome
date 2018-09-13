from nose.tools import with_setup, eq_
from mock import patch

from metadome.factory import create_app, make_celery


def setup_lazy():
    flask_app = create_app({'TESTING': True,
                            'CELERYD_CONCURRENCY': 0})  # do nothing
    make_celery(flask_app)


def do_nothing():
    pass


@with_setup(setup_lazy, do_nothing)
@patch("metadome.tasks.analyse_transcript")
def test_update_sent_state(mock_analyse):
    mock_analyse.return_value = {'test': "ok"}

    from metadome.tasks import retrieve_prebuild_visualization
    result = retrieve_prebuild_visualization.delay('test_id')

    eq_(result.status, 'SENT')
