from mock import patch
from nose.tools import ok_

from metadome.domain.repositories import GeneRepository


@patch('metadome.database.db.create_scoped_session')
def test_session_always_removed(mock_create_session):

    class FailSession:
        def __init__(self):
            self.removed = False

        def query(self, id_):
            raise Exception("test fail")

        def remove(self):
            self.removed = True

    class Allable:
        def all(self):
            return []

    class Filterable:
        def filter(self, id_):
            return Allable()

    class SuccessSession:
        def __init__(self):
            self.removed = False

        def query(self, id_):
            return Filterable()

        def remove(self):
            self.removed = True

    # Test that it removes upon failure:
    session = FailSession()
    mock_create_session.return_value = session

    try:
        l = GeneRepository.retrieve_all_transcript_ids_with_mappings()
    except:
        ok_(session.removed)


    # Test that it removes upon success:
    session = SuccessSession()
    mock_create_session.return_value = session

    l = GeneRepository.retrieve_all_transcript_ids_with_mappings()
    ok_(session.removed)


@patch('metadome.database.db.create_scoped_session')
@patch('metadome.domain.repositories._log.error')
def test_logs_error(mock_log_error, mock_create_session):

    class FailSession:
        def query(self, id_):
            raise Exception("test fail")

    try:
        l = GeneRepository.retrieve_all_transcript_ids_with_mappings()
    except:
        pass

    ok_(mock_log_error.assert_called)
