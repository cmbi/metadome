from nose.tools import ok_

from metadome.domain.transcript import is_transcript_id


def test_is_transcript_id():
    ok_(is_transcript_id('ENST00000273580.7'))
    ok_(not is_transcript_id('foo'))
