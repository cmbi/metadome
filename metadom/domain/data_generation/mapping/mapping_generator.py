import logging
import time
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
from metadom.domain.wrappers.hmmer import align_sequences_according_to_PFAM_HMM,\
    FoundNoPfamHMMException, FoundMoreThanOnePfamHMMException,\
    convert_pfam_fasta_alignment_to_original_aligned_sequence,\
    map_sequence_to_aligned_sequence,\
    convert_pfam_fasta_alignment_to_strict_fasta
from metadom.domain.data_generation.mapping.Protein2ProteinMapping import createAlignedSequenceMapping
from metadom.domain.data_generation.mapping.Gene2ProteinMapping import createMappingOfGeneTranscriptionToTranslationToProtein
from metadom.database import db
from metadom.domain.models.gene import Gene
from metadom.domain.models.protein import Protein
from metadom.domain.models.interpro import Interpro
from metadom.domain.models.mapping import Mapping
from metadom.domain.models.pfam_domain_alignment import PfamDomainAlignment

_log = logging.getLogger(__name__)

def generate_pfam_alignment_mappings(pfam_id):
    # retrieve any entries already present in the database with this pfam_id
    domain_alignment_entries = PfamDomainAlignment.query.join(Interpro).filter(Interpro.ext_db_id == pfam_id).all()
    if len(domain_alignment_entries) > 0:
        _log.info("Pfam domain "+pfam_id+" is already aligned and mapped. Skipping Pfam annotation...")
    else:
        _log.info("Started creating an alignment of all '"+pfam_id+"' Pfam domains in the human genome")
        start_time = time.clock()
        
        # retrieve all domain occurrences for the domain_id
        domain_of_interest_occurrences = Interpro.query.filter_by(ext_db_id = pfam_id).all()
    
        # Retrieve all the sequences of the domain of interest
        domain_of_interest_sequences = [domain_occurrence.get_aa_sequence() for domain_occurrence in domain_of_interest_occurrences]
        
        _log.debug("Starting HMM based alignment on for domain '"+pfam_id+"' for '"+str(len(domain_of_interest_occurrences))+"' occurrences across HG19")
        # Run the HMMERAlign algorithm based on the Pfam HMM
        try:
            hmmeralign_output = align_sequences_according_to_PFAM_HMM(domain_of_interest_sequences, pfam_id)
        except (FoundNoPfamHMMException, FoundMoreThanOnePfamHMMException) as e:
            _log.error(e)
            time_step = time.clock()
            _log.error("Prematurely stopped creating the '"+pfam_id+"' 'meta'-domain in "+str(time_step-start_time)+" seconds")
            return None
        _log.debug("Finished HMM based alignment on for domain '"+pfam_id+"'")
        
        # Create the strict versions of the consensus alignment
        _log.debug("Creating the mappings for '"+str(len(domain_of_interest_occurrences)) +"' '"+pfam_id+"' domain occurrences based on the HMM alignment to consensus and original domain sequence")
        
        # ensure we can map consensus residues back to consensus positions
        hmmeralign_output['consensus']['aligned_sequence'] = convert_pfam_fasta_alignment_to_original_aligned_sequence(hmmeralign_output['consensus']['alignment'])
        hmmeralign_output['consensus']['mapping_consensus_alignment_to_positions'] = map_sequence_to_aligned_sequence(hmmeralign_output['consensus']['sequence'], hmmeralign_output['consensus']['aligned_sequence'])
        
        # create mappings between domain occurrences and the domain consensus sequence
        for index in range(len(hmmeralign_output['alignments'])):
            with db.session.no_autoflush as _session:
                # retrieve current aligned domain
                domain_occurrence = domain_of_interest_occurrences[index]
                
                # Create a mapping from the aligned domain sequence to the domain sequence
                aligned_sequence = convert_pfam_fasta_alignment_to_original_aligned_sequence(hmmeralign_output['alignments'][index]['alignment'])
                mapping_domain_alignment_to_sequence_positions = map_sequence_to_aligned_sequence(domain_occurrence.get_aa_sequence(), aligned_sequence)
                
                # Generate the strict sequence for this domain; leaving only residues that were aligned to the domain consensus
                strict_aligned_sequence = convert_pfam_fasta_alignment_to_strict_fasta(hmmeralign_output['alignments'][index]['alignment'])
                
                # create the mapping between the strict alignments and the original consensus sequence
                mapping_aligned_domain_to_domain_consensus = createAlignedSequenceMapping(strict_aligned_sequence, hmmeralign_output['consensus']['aligned_sequence'], False)
                
                # go over each mapping seperatly
                for mapping_pos in sorted(mapping_aligned_domain_to_domain_consensus.keys()):
                    # retrieve the position in the domain consensus
                    domain_consensus_pos = hmmeralign_output['consensus']['mapping_consensus_alignment_to_positions'][mapping_pos]
                    # retrieve the residue at the consensus position and the residue at the domain position
                    consensus_domain_residue = hmmeralign_output['consensus']['aligned_sequence'][mapping_pos]
                    # retrieve the aligned residue
                    aligned_residue = aligned_sequence[mapping_pos]
                    
                    # retrieve the position in the domain sequence
                    ref_pos = mapping_domain_alignment_to_sequence_positions[mapping_pos]
                    # convert the position in the domain sequence to the uniprot position and genomic position
                    uniprot_pos = domain_occurrence.uniprot_start + ref_pos -1
                    
                    # Retrieve the mapping for the corresponding uniprot_position
                    mapping = Mapping.query.filter((Mapping.uniprot_position == uniprot_pos) & (Mapping.protein_id == domain_occurrence.protein_id)).first()
                    
                    # Double check for any possible errors at this point
                    if mapping is None:
                        raise Exception("For domain '"+str(pfam_id)+
                                                               "' for occurrence '"+str(domain_occurrence.id)+
                                                               "' at aligned position '"+str(mapping_pos)+
                                                               "' for uniprot position '"+str(uniprot_pos)+
                                                               "' there was no mapping present in the database")
                        continue
            
                    if aligned_residue != mapping.uniprot_residue:
                        raise Exception("For domain '"+str(pfam_id)+
                                                               "' for occurrence '"+str(domain_occurrence.id)+
                                                               "' at aligned position '"+str(mapping_pos)+
                                                               "' aligned sequence residue '"+aligned_residue+
                                                               "' did not match uniprot residue '"+mapping.uniprot_residue+"'")
                        continue
                     
                    if mapping.amino_acid_residue != mapping.uniprot_residue:
                        raise Exception("For domain '"+str(pfam_id)+
                                                               "' for occurrence '"+str(domain_occurrence.id)+
                                                               "' at aligned position '"+str(mapping_pos)+
                                                               "' translation residue '"+mapping.amino_acid_residue+
                                                               "' did not match uniprot residue '"+mapping.uniprot_residue+"'")
                        continue
                    
                    # create new domain_ alignment object
                    domain_alignment = PfamDomainAlignment(domain_consensus_residue=consensus_domain_residue, domain_consensus_position=domain_consensus_pos)
                    
                    # Add the foreign keys
                    domain_occurrence.pfam_domain_alignments.append(domain_alignment)
                    mapping.pfam_domain_alignment.append(domain_alignment)
        
                    # add the alignment to the database
                    _session.add(domain_alignment)
                
                # commit the alignments to the database
                _session.commit()
        
        time_step = time.clock()
        _log.info("Finished the mappings for '"+str(len(domain_of_interest_occurrences)) +"' '"+pfam_id+"' domain occurrences in "+str(time_step-start_time)+" seconds")

def annotate_interpro_domains_to_proteins(protein):
    interpro_entries = Interpro.query.join(Protein).filter(Interpro.protein_id == protein.id).all()
    if len(interpro_entries) > 0:
        _log.info("Protein "+str(protein.uniprot_ac)+" already annotated by Interpro. Skipping interpro annotation...")
    else:
        _log.info("Protein "+str(protein.uniprot_ac)+" has not yet been annotated by Interpro. Annotating...")
        # Annotate the interpro ids
        aa_sequence = protein.get_aa_sequence(skip_asterix_at_end=True)
        
        # Query the sequence to interpro
        interpro_results = retrieve_interpro_entries(protein.uniprot_ac, aa_sequence)
        
        # save the results to the database
        with db.session.no_autoflush as _session:
            for interpro_result in interpro_results:
                # create a new interpro domain
                interpro_domain = Interpro(_interpro_id=interpro_result['interpro_id'],\
                                      _ext_db_id=interpro_result['ext_db_id'],\
                                      _region_name=interpro_result['region_name'],\
                                      _start_pos=interpro_result['start_pos'],\
                                      _end_pos=interpro_result['end_pos'])
                 
                # Solve the required foreign key
                protein.interpro_domains.append(interpro_domain)
                
                # Add the interpro_domain to the database
                _session.add(interpro_domain)
            
            # Commit this session
            _session.commit()
            
        _log.info("Protein "+str(protein.uniprot_ac)+" was annotated with '"+str(len(interpro_result))+"' interpro domains.")
        
def generate_gene_to_swissprot_mapping(gene_name):
    """
    Given a gene_name, this method generates a mapping between swissprot and 
    every GENCODE Basic protein-coding translation for that gene
    """

    _log.info("Starting swissprot mapping for gene '"+gene_name+"'")
    
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
        # test if this translation does not already exists
        gene_translation = Gene.query.filter_by(
            gencode_transcription_id = matching_coding_translation['transcription-id']).first()
        if not gene_translation is None:
            _log.info("gene transcription: "+matching_coding_translation['transcription-id']+" is already present in the database. Skipping mapping")
            continue
        
        # retrieve the nucleotide sequence and coding sequence information
        try:
            gene_transcription = retrieveNucleotideSequence_gencode(matching_coding_translation)
            gene_transcription['CDS_annotation'] = retrieveCodingGenomicLocations_gencode(matching_coding_translation)
            matching_coding_translation['strand'] = retrieveStrandDirection_gencode(gene_transcription['CDS_annotation'])            
        except (NoGeneTranslationsFoundException, MissMatchTranscriptIDToMatchingTranscript,
                TranscriptionNotContainingCDS, TranscriptionStrandMismatchException,
                TranscriptionNotEncodingForTranslation) as e:
            _log.error(e)
            continue
        
        # Add the gene transcription to the database
        db.session.add(Gene(_strand=matching_coding_translation['strand'],
            _gene_name = matching_coding_translation['gene-name'],
            _gencode_transcription_id = matching_coding_translation['transcription-id'],
            _gencode_translation_name = matching_coding_translation['translation-name'],
            _gencode_gene_id = matching_coding_translation['gene_name-id'],
            _havana_gene_id = matching_coding_translation['Havana-gene_name-id'],
            _havana_translation_id = matching_coding_translation['Havana-translation-id'],
            _sequence_length = matching_coding_translation['sequence-length']))
        db.session.commit()
        
        # retrieve uniprot match
        try:
            uniprot = retrieveIdenticalUniprotMatch(matching_coding_translation, species_filter=UNIPROT_SPROT_SPECIES_FILTER)
        except (NoUniProtACFoundException) as e:
            _log.error(e)
            continue
        
        # test if this protein already exists in the database
        matching_protein = Protein.query.filter_by(uniprot_ac = uniprot['uniprot_ac']).first()
        if matching_protein is None:
            # Add the uniprot_result to the database
            db.session.add(Protein(_uniprot_ac = uniprot['uniprot_ac'],
                    _uniprot_name = uniprot['uniprot_name'],
                    _source = uniprot['database']))
            db.session.commit()
        
        # create the mapping between both sequences
        createMappingOfGeneTranscriptionToTranslationToProtein(gene_transcription, matching_coding_translation, uniprot)
        
        _log.info("For gene '"+str(gene_name)+
                                            "' used translation '"+str(matching_coding_translation['translation-name'])+
                                            "', with translation length "+str(matching_coding_translation['sequence-length'])+"'")