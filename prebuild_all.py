import traceback

from metadome.application import app, celery
from metadome.tasks import create_prebuild_visualization
from metadome.domain.repositories import GeneRepository

with app.app_context():
    transcripts = GeneRepository.retrieve_all_transcript_ids_with_mappings()

    results = [create_prebuild_visualization.delay(transcript.gencode_transcription_id)
               for transcript in transcripts]

    for result in results:
        try:
            print(result.get())
        except:
            traceback.print_exc()
