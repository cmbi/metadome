import logging
from metadom.domain.wrappers.blast import run_blast, interpret_blast_as_uniprot
from metadom.domain.wrappers.gencode import retrieveSwissProtIDs,\
    NoSwissProtEntryFoundException
from metadom.default_settings import UNIPROT_SPROT_CANONICAL, UNIPROT_TREMBL,\
    UNIPROT_MAX_BLAST_RESULTS, UNIPROT_SPROT_CANONICAL_AND_ISOFORM,\
    UNIPROT_SPROT_ISOFORM

_log = logging.getLogger(__name__)


class NoUniProtACFoundException(Exception):
    pass

class NoneExistingUniprotDatabaseProvidedException(Exception):
    pass

class MissMatchingSwissProtEntriesFoundException(Exception):
    pass

def retrieveTopUniprotMatch(geneTranslation, uniprot_database="sp", species_filter=None):
    """Retrieves the top swiss-/Uniprot match for the provided sequence"""
    # Which database to blast to
    if uniprot_database=="sp":
        _log.debug('Querying the gene translation to Uniprot_Sprot database')
        blast_db=UNIPROT_SPROT_CANONICAL_AND_ISOFORM
    elif uniprot_database=="tr":
        _log.debug('Querying the gene translation to Uniprot_TREMBL database')
        blast_db=UNIPROT_TREMBL
    else:
        raise NoneExistingUniprotDatabaseProvidedException("Possible options are 'sp' for SwissProt and 'tr' for Uniprot_Trembl, provided was '"+str(uniprot_database)+"'")
    
    # retrieve the results
    sequence_results = retrieveMatchingUniprotSequences(geneTranslation, blast_db, species_filter)
    _log.debug("Retrieved '"+str(len(sequence_results))+"' results from blasting to Uniprot")
    
    # retrieve the top result
    top_result = sequence_results[0]
    
    # analyse the top result
    if top_result['length'] != len(geneTranslation['sequence']):
        _log.warning("Length of gene translation ('"+str(len(geneTranslation['sequence']))+"') does not match uniprot sequence ('"+str(top_result['length'])+"')")
    if top_result['pident'] < 100:
        _log.warning("Percentage identity of gene translation to uniprot sequence is not 100%, but is '"+str(top_result['pident'])+"%'")
    if top_result['evalue'] > 0.01:
        _log.warning("E-value of uniprot sequence is '"+str(top_result['evalue'])+"'")
    if top_result['send'] != top_result['qend']:
        _log.warning("End position of uniprot sequence ('"+str(top_result['send'])+"') does not match the end position of the gene translation ('"+str(top_result['qend'])+"')")
    if top_result['sstart'] != top_result['qstart']:
        _log.warning("Start position of uniprot sequence ('"+str(top_result['sstart'])+"') does not match the start position of the gene translation ('"+str(top_result['qstart'])+"')")
    
    # construct the result    
    uniprot_result = {
        "sequence": getUniprotSequence(top_result['accession_code'], blast_db),
        "database": "swissprot" if top_result['database_id']=='sp' else "uniprot_trembl",
        "uniprot_name": top_result['entry_name'],
        "uniprot_ac": top_result['accession_code'],
        "blast_result":top_result,
    }
    
    return uniprot_result
    

def getUniprotSequence(accession_code , blast_db=UNIPROT_SPROT_CANONICAL_AND_ISOFORM):
    if blast_db != UNIPROT_SPROT_CANONICAL_AND_ISOFORM and blast_db != UNIPROT_SPROT_CANONICAL and blast_db != UNIPROT_SPROT_ISOFORM:
        raise NotImplementedError('Only swissprot is supported for now, uniprot needs to be handled by a database structure')
    
    sequence = ""
    with open(blast_db) as fasta_file:
        fasta_lines = fasta_file.read().splitlines()
        n_total_lines = len(fasta_lines)
        for i in range(n_total_lines):
            if not(fasta_lines[i].startswith('>')):continue
            if accession_code in fasta_lines[i]:
                for j in range(i+1, n_total_lines):
                    if fasta_lines[j].startswith('>'):
                        return sequence
                    if j < n_total_lines:
                        sequence = sequence+fasta_lines[j]
                    else:
                        return sequence
                
    return sequence    

def retrieveMatchingUniprotSequences(geneTranslation, blast_db=UNIPROT_SPROT_CANONICAL_AND_ISOFORM, species_filter=None):
    """Blasts the translated gene sequence to the uniprot/swissprot fasta database and returns 
     the blast results as a list of dictionaries with keys: database_id, accession_code,
     entry_name, qseqid, sseqid, pident, length, mismatch, gapopen, qstart, qend, sstart,
     send, evalue, bitscore"""
    sequence_results = []
    blast_results = run_blast(sequence=geneTranslation['sequence'], blastdb=blast_db, max_target_seqs=UNIPROT_MAX_BLAST_RESULTS)
    
    if not len(blast_results) == 0 :
        sequence_results = [interpret_blast_as_uniprot(blast_result) for blast_result in blast_results]
    
    if not species_filter is None:
        if blast_db == UNIPROT_SPROT_CANONICAL or blast_db == UNIPROT_SPROT_ISOFORM or blast_db == UNIPROT_SPROT_CANONICAL_AND_ISOFORM:
            sequence_results = [entry for entry in sequence_results if entry['entry_name'].split("_")[1] == species_filter]
        else:
            raise NotImplementedError("There is no species filtering available at the moment for uniprot (non-swissprot) entries")
    
    if len(sequence_results) == 0 :
        raise NoUniProtACFoundException("No uniprot sequence found for "+geneTranslation['gene-name'])
    
    
    return sequence_results


def retrieveSwissprotFromGencode(gene_report):
    try:
        # retrieve translation ids
        translationIDs = [translation['transcription-id'] for translation in gene_report['matching_coding_translations']]
         
        # Retrieve any id that matches one of the translation ids for this gene
        swissprot_results = retrieveSwissProtIDs(translationIDs)
                 
        # check if there are more then one results, validate
        if len(swissprot_results) > 1:
            previous_swissprot_ac= None
            translation_ids_checked = []
            for translation_id in swissprot_results.keys():
                translation_ids_checked.append(translation_id)
                if previous_swissprot_ac is None:
                    previous_swissprot_ac = swissprot_results[translation_id]['ac']
                elif previous_swissprot_ac != swissprot_results[translation_id]['ac']:
                    raise MissMatchingSwissProtEntriesFoundException("Found non-matching swissprot ids / accession codes '"+str(previous_swissprot_ac)+"' vs '"+str(swissprot_results[translation_id]['swissprot_id'])+"/"+str(swissprot_results[translation_id]['ac'])+"' for the gene '"+gene_report['gene_name']+"'")
            
            # Check if the chosen translation_used, also was allocated to the swissprot ids/acs 
            if not(gene_report["translation_used"]['transcription-id'] in translation_ids_checked):
                _log.warning("Used an alternative SwissProt ID and AC, as the original translation_id '"+str(gene_report["translation_used"]['transcription-id'])+"' was not present in the translation ids found in the GenCode Swissprot allocation file '"+str(translation_ids_checked)+"'")
                
        return swissprot_results
    except (NoSwissProtEntryFoundException, MissMatchingSwissProtEntriesFoundException) as e:
        _log.error(e)

    
