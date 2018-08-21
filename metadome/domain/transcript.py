import re


transcript_id_pattern = re.compile(r"^ENST[0-9]{11}\.[0-9]+$")

def is_transcript_id(transcript_id):
    return transcript_id_pattern.match(transcript_id) is not None

