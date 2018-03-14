from metadom.default_settings import UNIPROT_SPROT_SPECIES_FILTER
from metadom.domain.wrappers.gencode import retrieveGeneTranslations_gencode,\
    retrieveNucleotideSequence_gencode, retrieveCodingGenomicLocations_gencode,\
    retrieveStrandDirection_gencode, retrieveMRNAValidatedTranslations_gencode,\
    NoGeneTranslationsFoundException, TranscriptionNotContainingCDS,\
    TranscriptionNotEncodingForTranslation, TranscriptionStrandMismatchException,\
    MissMatchTranscriptIDToMatchingTranscript
from metadom.domain.wrappers.uniprot import retrieveIdenticalUniprotMatch,\
    NoUniProtACFoundException
from metadom.domain.wrappers.interpro import retrieve_interpro_entries
from metadom.domain.data_generation.mapping.Gene2ProteinMapping import createMappingOfGeneTranscriptionToTranslationToProtein
from metadom.database import db
from metadom.domain.models.gene import Gene
from metadom.domain.models.protein import Protein
from metadom.domain.models.interpro import Interpro
from metadom.domain.repositories import MappingRepository, SequenceRepository

import logging

_log = logging.getLogger(__name__)

def annotate_interpro_domains_to_proteins(protein):
    interpro_entries = Interpro.query.join(Protein).filter(Interpro.protein_id == protein.id).all()
    if len(interpro_entries) > 0:
        _log.info("Protein "+str(protein.uniprot_ac)+" already annotated by Interpro. Skipping interpro annotation...")
    else:
        _log.info("Protein "+str(protein.uniprot_ac)+" has not yet been annotated by Interpro. Annotating...")
        # Annotate the interpro ids
        mappings = MappingRepository.get_mappings_for_protein(protein)
        aa_sequence = SequenceRepository.get_aa_sequence(mappings, skip_asterix_at_end=True)
        
        # Query the sequence to interpro
        interpro_results = retrieve_interpro_entries(protein.uniprot_ac, aa_sequence)
        
        # save the results to the database
        with db.session.no_autoflush:
            for interpro_result in interpro_results:
                if interpro_result['interpro_id'] is None and interpro_result['region_name'] == '':
                    # skip non-informative results
                    continue
                                
                # create a new interpro domain
                interpro_domain = Interpro(_interpro_id=interpro_result['interpro_id'],\
                                      _ext_db_id=interpro_result['ext_db_id'],\
                                      _region_name=interpro_result['region_name'],\
                                      _start_pos=interpro_result['start_pos'],\
                                      _end_pos=interpro_result['end_pos'])
                 
                # Solve the required foreign key
                protein.interpro_domains.append(interpro_domain)
                
                # Add the interpro_domain to the database
                db.session.add(interpro_domain)
                
        # Commit this session
        db.session.commit()
        
        _log.info("Protein "+str(protein.uniprot_ac)+" was annotated with '"+str(len(interpro_results))+"' interpro domains.")
        
def generate_gene_to_swissprot_mapping(gene_name):
    """
    Given a gene_name, this method generates a mapping between swissprot and 
    every GENCODE Basic protein-coding translation for that gene
    """
    _log.info("Starting swissprot mapping for gene '"+gene_name+"'")
    
    # The result of this method; a dictionary containing all items that will be added to the database
    to_be_added_db_entries = {"genes":dict(), "proteins":dict(), "chromosome_positions":dict(), "mappings":dict()}    
    
    # retrieve all translations for the gene
    matching_translations = retrieveGeneTranslations_gencode(gene_name)
    
    # filter out translations that are not validated on the mRNA level
    mrna_translations =  [a['transcription_id'] for a in retrieveMRNAValidatedTranslations_gencode(gene_name)]
    mrna_filtered_translations = [translation for translation in matching_translations if translation['transcription-id'] in mrna_translations]
    n_translations = len(matching_translations)
    n_translations_after_mrna_filter  = len(mrna_filtered_translations)
    if n_translations > n_translations_after_mrna_filter:
        _log.debug("Filtered out '"+str(n_translations - n_translations_after_mrna_filter)+"' from the original '"+str(n_translations)+"' matching translation(s) for gene "+gene_name+", by focussing on mRNA level validation")
    
    # filter out any non-coding genes, by excluding any sequences that do not start with a methionine ('M')
    matching_coding_translations = [translation for translation in mrna_filtered_translations if translation['sequence'].startswith('M')]
    n_translations_after_coding_filter  = len(matching_coding_translations)
    if n_translations_after_mrna_filter > n_translations_after_coding_filter:
        _log.debug("Filtered out '"+str(n_translations - n_translations_after_coding_filter)+"' from the original '"+str(n_translations)+"' matching translation(s) for gene "+gene_name+", by checking if the sequence starts with a Methionine")
    
    # retrieve the lengths for the sequences
    sequences_lengths = [len(s['sequence']) for s in matching_coding_translations]
    _log.info("Found '"+str(len(matching_coding_translations))+"' matching protein coding translation(s) for gene "+gene_name+", with lengths: "+str(sequences_lengths))

    # start creation of the mapping between the gene and swissprot
    for matching_coding_translation in matching_coding_translations:
        # retrieve the nucleotide and coding sequence information
        try:
            gene_transcription = retrieveNucleotideSequence_gencode(matching_coding_translation)
            gene_transcription['CDS_annotation'] = retrieveCodingGenomicLocations_gencode(matching_coding_translation)
            matching_coding_translation['strand'] = retrieveStrandDirection_gencode(gene_transcription['CDS_annotation'])            
        except (NoGeneTranslationsFoundException, MissMatchTranscriptIDToMatchingTranscript,
                TranscriptionNotContainingCDS, TranscriptionStrandMismatchException,
                TranscriptionNotEncodingForTranslation) as e:
            _log.error(e)
            continue
        
        # Create the gene transcription entry
        to_be_added_db_entries["genes"][matching_coding_translation['transcription-id']] =  Gene(_strand=matching_coding_translation['strand'],
            _gene_name = matching_coding_translation['gene-name'],
            _gencode_transcription_id = matching_coding_translation['transcription-id'],
            _gencode_translation_name = matching_coding_translation['translation-name'],
            _gencode_gene_id = matching_coding_translation['gene_name-id'],
            _havana_gene_id = matching_coding_translation['Havana-gene_name-id'],
            _havana_translation_id = matching_coding_translation['Havana-translation-id'],
            _sequence_length = matching_coding_translation['sequence-length'])
        
        # retrieve uniprot match
        try:
            uniprot = retrieveIdenticalUniprotMatch(matching_coding_translation, species_filter=UNIPROT_SPROT_SPECIES_FILTER)
        except (NoUniProtACFoundException) as e:
            _log.error("For gene '"+str(gene_name)+
                                    "' with translation '"+str(matching_coding_translation['translation-name'])+
                                    "', no match could be made with uniprot due to: "+str(e))
            continue
        
        # Create the uniprot_result database entry
        to_be_added_db_entries["proteins"][matching_coding_translation['transcription-id']] = Protein(_uniprot_ac = uniprot['uniprot_ac'],
                _uniprot_name = uniprot['uniprot_name'],
                _source = uniprot['database'])
        
        # create the mapping between both sequences
        mappings = createMappingOfGeneTranscriptionToTranslationToProtein(gene_transcription, matching_coding_translation, uniprot)
        to_be_added_db_entries["mappings"][matching_coding_translation['transcription-id']] = mappings
        
        _log.info("For gene '"+str(gene_name)+
                                    "' the translation '"+str(matching_coding_translation['translation-name'])+
                                    "' is matched and mapped with '"+str(uniprot['uniprot_ac'])+"'")
    
    return to_be_added_db_entries