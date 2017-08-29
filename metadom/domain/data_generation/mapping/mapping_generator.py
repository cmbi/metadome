import logging
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

_log = logging.getLogger(__name__)

def annotate_protein_domains_to_mappings():
    pass

def generate_gene_to_swissprot_mapping(gene_name):
    """
    Given a gene_name, this method generates a mapping between swissprot and 
    every GENCODE Basic protein-coding translation for that gene
    """

    _log.info("Starting analysis for gene '"+gene_name+"'")
    
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
    
    for matching_coding_translation in matching_coding_translations:
        # First try if this matching coding translation matches with a swissprot sequence     
        try:
            # retrieve the nucleotide sequence
            gene_transcription = retrieveNucleotideSequence_gencode(matching_coding_translation)
            gene_transcription['CDS_annotation'] = retrieveCodingGenomicLocations_gencode(matching_coding_translation)
            gene_transcription['strand'] = retrieveStrandDirection_gencode(gene_transcription['CDS_annotation'])
            
            # annotate the swissprot ID
            uniprot = retrieveIdenticalUniprotMatch(matching_coding_translation, species_filter=UNIPROT_SPROT_SPECIES_FILTER)
        except (NoGeneTranslationsFoundException, MissMatchTranscriptIDToMatchingTranscript,
                TranscriptionNotContainingCDS, TranscriptionStrandMismatchException,
                TranscriptionNotEncodingForTranslation, NoUniProtACFoundException) as e:
            _log.error(e)
            continue
        
        # Annotate the interpro ids
#         gene_report['interpro'] = retrieve_interpro_entries(gene_report['uniprot'])
        
        _log.info("For gene '"+str(gene_name)+
                                            "' used translation '"+str(matching_coding_translation['translation-name'])+
                                            "', with translation length "+str(matching_coding_translation['sequence-length'])+
    #                                         " to find corresponding PDB file '"+str(gene_report["pdb_seqres_used"]['sseqid'])+
    #                                         "', with seqres of length '"+str(gene_report["pdb_seqres_used"]['length'])+
    #                                         "' and structure length '"+str(len(gene_report["measured_structure_sequence"]))+
    #                                         " found corresponding uniprot ID '"+str(gene_report["uniprot"]['uniprot_ac'])+
                                            "'")
        # translation position: {Amino Acid, Nucleotides, chromosomal position range, Linked PDB seqres position, Linked PDB atom position}
        createMappingOfGeneTranscriptionToTranslationToProtein(gene_transcription, matching_coding_translation, uniprot)
