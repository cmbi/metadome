'''
Created on Dec 22, 2015

Writes an automated report for a gene analysis

@author: laurensvdwiel
'''
from metadom_api.default_settings import UNIPROT_SPROT_SPECIES_FILTER
from metadom_api.controller.wrappers.gencode import retrieveGeneTranslations_gencode,\
    retrieveLongestTranslation, retrieveNucleotideSequence_gencode,\
    retrieveCodingGenomicLocations_gencode,\
    retrieveStrandDirection_gencode,\
    retrieveMRNAValidatedTranslations_gencode, NoGeneTranslationsFoundException,\
    TranscriptionNotContainingCDS, TranscriptionNotEncodingForTranslation,\
    TranscriptionStrandMismatchException,\
    MissMatchTranscriptIDToMatchingTranscript
from metadom_api.controller.wrappers.uniprot import retrieveTopUniprotMatch,\
    retrieveSwissprotFromGencode, NoUniProtACFoundException
from metadom_api.controller.wrappers.interpro import retrieve_interpro_entries
from metadom_api.controller.mapping.Gene2ProteinMapping import createMappingOfGeneTranscriptionToTranslationToProtein
import logging

_log = logging.getLogger(__name__)

# from metadom_api.controller.wrappers.pdb import retrieveMatchingSeqresSequences,\
#     retrieveBestMatchingSeqresSequence, retrieveAtomicStructureSequence,\
#     getRefseqForPDBfile, cleanBlastResults, appendStructureDataToBlastResults


def generateAnnotatedGeneTable(gene_name):
    """INPUT:gene_name - Gene Name
    OUTPUT:
        annotated_table:
        DESCR: matched GENE_TRANSCRIPT with length xxx to PDB_CODE, chain CHAIN_ID, with length xxx having E_VALUE, RESOLUTION, R_FREE, _R_WORK
        HG19_pos            | PDB_pos   | Exac SNP | HGMD mut | Interprot domain | .... additional space c.xxx[nucleotide]   | p.AAxxx"""

    _log.info("Starting analysis for gene '"+gene_name+"'")
    
    # create a report
    gene_report = {}
    
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
    try:
        # retrieve best translation for the gene
        longest_translation = retrieveLongestTranslation(matching_coding_translations)
        
        # retrieve the nucleotide sequence
        transcription = retrieveNucleotideSequence_gencode(longest_translation)
        transcription['CDS_annotation'] = retrieveCodingGenomicLocations_gencode(longest_translation)
        transcription['strand'] = retrieveStrandDirection_gencode(transcription['CDS_annotation'])
        
        # annotate the swissprot ID
        gene_report['uniprot'] = retrieveTopUniprotMatch(longest_translation, species_filter=UNIPROT_SPROT_SPECIES_FILTER)
    except (NoGeneTranslationsFoundException, MissMatchTranscriptIDToMatchingTranscript,
            TranscriptionNotContainingCDS, TranscriptionStrandMismatchException,
            TranscriptionNotEncodingForTranslation, NoUniProtACFoundException) as e:
        _log.error(e)
        return gene_report
    
    # construct the first part of the report
    gene_report["gene_name"] = gene_name
    gene_report["matching_translations"] = matching_translations
    gene_report["gene_transcription"] = transcription
    gene_report["matching_coding_translations"] = matching_coding_translations
    gene_report["translation_used"] = longest_translation
    
    # Annotate the interpro ids
    gene_report['interpro'] = retrieve_interpro_entries(gene_report['uniprot'])

    # Annotateswissprot ac's from gencode
    gene_report['gencode_swissprot'] = retrieveSwissprotFromGencode(gene_report)
    
    
    _log.info("For gene '"+str(gene_report["gene_name"])+
                                        "' used translation '"+str(gene_report["translation_used"]['translation-name'])+
                                        "', with translation length "+str(gene_report["translation_used"]['sequence-length'])+
                                        " to find corresponding PDB file '"+str(gene_report["pdb_seqres_used"]['sseqid'])+
                                        "', with seqres of length '"+str(gene_report["pdb_seqres_used"]['length'])+
                                        "' and structure length '"+str(len(gene_report["measured_structure_sequence"]))+
                                        " found corresponding uniprot ID '"+str(gene_report["uniprot"]['uniprot_ac'])+
                                        "'")
    
    return gene_report
    
def createGene2ProteinMapping(gene_report):
    # translation position: {Amino Acid, Nucleotides, chromosomal position range, Linked PDB seqres position, Linked PDB atom position}
    GenomeMapping = createMappingOfGeneTranscriptionToTranslationToProtein(gene_report)
    
    # add to report    
    gene_report["GenomeMapping"] = GenomeMapping         
    


