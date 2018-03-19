from metadom.domain.wrappers.hmmer import align_sequences_according_to_PFAM_HMM,\
    FoundNoPfamHMMException, FoundMoreThanOnePfamHMMException,\
    convert_pfam_fasta_alignment_to_original_aligned_sequence,\
    map_sequence_to_aligned_sequence,\
    convert_pfam_fasta_alignment_to_strict_fasta
from metadom.domain.data_generation.mapping.Protein2ProteinMapping import createAlignedSequenceMapping    
import numpy as np
import time
import logging
from metadom.domain.repositories import MappingRepository, SequenceRepository

_log = logging.getLogger(__name__)

def generate_pfam_alignment_mappings(pfam_id, domain_of_interest_occurrences):
    _log.info("Started creating an alignment of all '"+pfam_id+"' Pfam domains in the human genome")
    start_time = time.clock()
      
    # the meta_domain that is to be returned
    mappings_per_consensus_pos = {}
    # the mapping of the protein {protein_id: {protein_posistion: consensus_position}}
    consensus_pos_per_protein = {}
    
    # First: retrieve all protein ids for this domain
    protein_ids = [int(y) for y  in np.unique([x.protein_id for x in domain_of_interest_occurrences])]
    
    # Second, get all mappings for these proteins
    protein_mappings = MappingRepository.get_mappings_for_multiple_protein_ids(protein_ids)

    # Third: cut out the sequences from these mappings to Retrieve all the sequences of the domain of interest
    domain_of_interest_sequences = [SequenceRepository.get_aa_region(
        sequence=SequenceRepository.get_aa_sequence(mappings=protein_mappings[domain_occurrence.protein_id], skip_asterix_at_end=True), 
        region_start=domain_occurrence.uniprot_start, 
        region_stop=domain_occurrence.uniprot_stop) for domain_occurrence in domain_of_interest_occurrences]
      
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
        # retrieve current aligned domain
        domain_occurrence = domain_of_interest_occurrences[index]
           
        # Create a mapping from the aligned domain sequence to the domain sequence
        aligned_sequence = convert_pfam_fasta_alignment_to_original_aligned_sequence(hmmeralign_output['alignments'][index]['alignment'])
        mapping_domain_alignment_to_sequence_positions = map_sequence_to_aligned_sequence(domain_of_interest_sequences[index], aligned_sequence)
           
        # Generate the strict sequence for this domain; leaving only residues that were aligned to the domain consensus
        strict_aligned_sequence = convert_pfam_fasta_alignment_to_strict_fasta(hmmeralign_output['alignments'][index]['alignment'])
           
        # create the mapping between the strict alignments and the original consensus sequence
        mapping_aligned_domain_to_domain_consensus = createAlignedSequenceMapping(strict_aligned_sequence, hmmeralign_output['consensus']['aligned_sequence'], False)
           
        # create a list of mapping positions that includes insertions
        mapping_positions = list(mapping_domain_alignment_to_sequence_positions.keys()) + list(set(mapping_aligned_domain_to_domain_consensus.keys()) - set(mapping_domain_alignment_to_sequence_positions.keys()))
           
        # Second add each aligned residue mapping
        for mapping_pos in sorted(mapping_positions):
            # retrieve the residue at the consensus position and the residue at the domain position
            consensus_domain_residue = hmmeralign_output['consensus']['aligned_sequence'][mapping_pos]
               
            if consensus_domain_residue == '-':
                # Set the default values for the insertion
                continue
            else:
                # retrieve the position in the domain consensus
                domain_consensus_pos = hmmeralign_output['consensus']['mapping_consensus_alignment_to_positions'][mapping_pos]
               
            # retrieve the aligned residue
            aligned_residue = aligned_sequence[mapping_pos]
               
            # retrieve the position in the domain sequence
            ref_pos = mapping_domain_alignment_to_sequence_positions[mapping_pos]
            # convert the position in the domain sequence to the uniprot position and genomic position
            uniprot_pos = domain_occurrence.uniprot_start + ref_pos -1
            
            # Add the consensus pos to the protein
            if not domain_occurrence.protein_id in consensus_pos_per_protein.keys():
                consensus_pos_per_protein[domain_occurrence.protein_id] = {}
            if uniprot_pos in consensus_pos_per_protein[domain_occurrence.protein_id].keys():
                # found a duplicate... this should not happen
                raise Exception("duplicate uniprot position in metadomain for protein_id ='"+str(domain_occurrence.protein_id)+"' at position '"+str(uniprot_pos)+"'") 
            else:
                consensus_pos_per_protein[domain_occurrence.protein_id][uniprot_pos] = domain_consensus_pos
            
            # Retrieve the mapping for the corresponding uniprot_position
            mappings = [x for x in protein_mappings[domain_occurrence.protein_id] if x.uniprot_position == uniprot_pos]
               
            for mapping in mappings:
                # Double check for any possible errors at this point
                if mapping is None:
                    raise Exception("For domain '"+str(pfam_id)+
                                                           "' for occurrence '"+str(domain_occurrence.id)+
                                                           "' at aligned position '"+str(mapping_pos)+
                                                           "' for uniprot position '"+str(uniprot_pos)+
                                                           "' there was no mapping present in the database")
#                     continue
           
                if aligned_residue != mapping.uniprot_residue:
                    raise Exception("For domain '"+str(pfam_id)+
                                                           "' for occurrence '"+str(domain_occurrence.id)+
                                                           "' at aligned position '"+str(mapping_pos)+
                                                           "' aligned sequence residue '"+aligned_residue+
                                                           "' did not match uniprot residue '"+mapping.uniprot_residue+"'")
#                     continue
                    
                if mapping.amino_acid_residue != mapping.uniprot_residue:
                    raise Exception("For domain '"+str(pfam_id)+
                                                           "' for occurrence '"+str(domain_occurrence.id)+
                                                           "' at aligned position '"+str(mapping_pos)+
                                                           "' translation residue '"+mapping.amino_acid_residue+
                                                           "' did not match uniprot residue '"+mapping.uniprot_residue+"'")
#                     continue
                   
                # Add the domain alignment
                if not domain_consensus_pos in mappings_per_consensus_pos.keys():
                    mappings_per_consensus_pos[domain_consensus_pos] = []
                mappings_per_consensus_pos[domain_consensus_pos].append(mapping)
  
    time_step = time.clock()
    _log.info("Finished the mappings for '"+str(len(domain_of_interest_occurrences)) +"' '"+pfam_id+"' domain occurrences in "+str(time_step-start_time)+" seconds")
    return mappings_per_consensus_pos, consensus_pos_per_protein
