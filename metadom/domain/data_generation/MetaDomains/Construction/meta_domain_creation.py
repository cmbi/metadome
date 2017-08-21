'''
Created on Aug 2, 2016

@author: laurens
'''
import pandas as pd
from BGVM.Mapping.Gene2ProteinMappingDatabase import retrieve_single_gene_entries
from BGVM.Mapping.Regions.region_annotation import analyse_dn_ds_over_protein_region
from BGVM.Mapping.Protein2ProteinMapping import createAlignedSequenceMapping
from BGVM.APIConnectors import HMMERApi
from BGVM.BGVMExceptions import RegioncDNALengthDoesNotEqualProteinLengthException,\
    FoundNoPfamHMMException, FoundMoreThanOnePfamHMMException,\
    RegionIsNotEncodedBycDNAException
from BGVM.MetaDomains.Construction.meta_domain_merging import merge_meta_domain
from dev_settings import LOGGER_NAME
import logging
import time
from BGVM.APIConnectors.HMMERApi import convert_pfam_fasta_alignment_to_original_aligned_sequence,\
    map_sequence_to_aligned_sequence,\
    convert_pfam_fasta_alignment_to_strict_fasta

def annotate_genic_information(information_name, information_key, reference_domain_consensus, domain_id, hmmeralign_output, domain_of_interest_occurrences, ignore_list_of_indices, additional_information_keys):
    annotated_domain_consensus = []
    for index in range(len(hmmeralign_output['alignments'])):
        if index not in ignore_list_of_indices:
            domain_occurrence = domain_of_interest_occurrences[index]
            for entry in domain_occurrence[information_key]:
                domain_identifier = domain_occurrence['identifier']
                reference_domain_consensus_entry = reference_domain_consensus[(reference_domain_consensus['domain_identifier'] == domain_identifier) & (reference_domain_consensus['swissprot_pos'] == entry['uniprot_pos'])]
                
                if len(reference_domain_consensus_entry) != 1:
                    logging.getLogger(LOGGER_NAME).warning("At "+information_name+" annotation: For domain '"+str(domain_id)+
                                                       "' for occurrence '"+str(domain_occurrence['identifier'])+
                                                       "' at aligned position '"+str(entry['uniprot_pos'])+
                                                       "' no reference was mapped")
                    continue
                
                # convert to dictionary for easy accessibility
                reference_domain_consensus_entry = reference_domain_consensus_entry.set_index('domain_identifier').to_dict()
                
                # annotate iformation from mapping
                annotated_domain_consensus_entry = {
                        'chr':reference_domain_consensus_entry['chr'][domain_identifier], 
                        'chr_start':reference_domain_consensus_entry['chr_start'][domain_identifier], 
                        'chr_stop':reference_domain_consensus_entry['chr_stop'][domain_identifier], 
                        'gencode_transcription_id':reference_domain_consensus_entry['gencode_transcription_id'][domain_identifier],
                        'gencode_translation_name':reference_domain_consensus_entry['gencode_translation_name'][domain_identifier],
                        'gencode_gene_id':reference_domain_consensus_entry['gencode_gene_id'][domain_identifier],
                        'uniprot_ac':reference_domain_consensus_entry['uniprot_ac'][domain_identifier],
                        'uniprot_name':reference_domain_consensus_entry['uniprot_name'][domain_identifier],
                        'domain_identifier':domain_identifier,
                        'gene_name':reference_domain_consensus_entry['gene_name'][domain_identifier],
                        'swissprot_pos':reference_domain_consensus_entry['swissprot_pos'][domain_identifier],
                        'domain_consensus_pos':reference_domain_consensus_entry['domain_consensus_pos'][domain_identifier],
                        'ref_codon':reference_domain_consensus_entry['ref_codon'][domain_identifier],
                        'consensus_domain_residue': reference_domain_consensus_entry['consensus_domain_residue'][domain_identifier],
                        'ref_residue':reference_domain_consensus_entry['ref_residue'][domain_identifier],
                }
                
                if annotated_domain_consensus_entry['ref_codon'] != entry['ref_codon']:
                    logging.getLogger(LOGGER_NAME).error("At "+information_name+" annotation: For domain '"+str(domain_id)+
                                                       "' for occurrence '"+str(domain_occurrence['identifier'])+
                                                       "' at aligned position '"+str(entry['uniprot_pos'])+
                                                       "' ref codon '"+annotated_domain_consensus_entry['ref_codon']+
                                                       "' did not match "+information_name+"  ref codon '"+entry['ref_codon']+"'")
                    continue
                
                if annotated_domain_consensus_entry['ref_residue'] != entry['ref_residue']:
                    logging.getLogger(LOGGER_NAME).error("At "+information_name+" annotation: For domain '"+str(domain_id)+
                                                       "' for occurrence '"+str(domain_occurrence['identifier'])+
                                                       "' at aligned position '"+str(entry['uniprot_pos'])+
                                                       "' ref_residue '"+annotated_domain_consensus_entry['ref_residue']+
                                                       "' did not match "+information_name+"  ref_residue '"+entry['ref_residue']+"'")
                    continue
                        
                # annotate the information from the additional information
                for key in additional_information_keys.keys():
                    annotated_domain_consensus_entry[key] = entry[additional_information_keys[key]]
                
                annotated_domain_consensus.append(annotated_domain_consensus_entry)
                
    return annotated_domain_consensus

def create_annotated_meta_domain(domain_id, domain_dataset, minimal_merged_meta_domain_ExAC_frequency,  merged_meta_domain_missense_only): 
    logging.getLogger(LOGGER_NAME).info("Started creating the '"+domain_id+"' 'meta'-domain")
    start_time = time.clock()
    
    # retrieve the data for the domain_id
    domain_of_interest_domain_data = domain_dataset[domain_dataset.external_database_id == domain_id]
    
    # Retrieve all the occurrences of the domain of interest
    domain_of_interest_occurrences = []
    gene_mappings = dict()
    for gene_name in pd.unique(domain_of_interest_domain_data.gene_name):
        # retrieve the gene mapping for this gene and save it
        gene_mappings[gene_name] = retrieve_single_gene_entries(gene_name)['gene_mapping']
        
        # use the current gene mapping for this iteration
        gene_mapping = gene_mappings[gene_name]
        
        # keep an occurrence counter
        occurence_in_this_gene_count = 0
        for domain in gene_mapping['interpro']:
            if domain['ext_db_id'] == domain_id:
                occurence_in_this_gene_count += 1
                occurence_id = domain_id +'_'+ gene_name+'_'+str(occurence_in_this_gene_count)
                occurrence_sequence = gene_mapping['uniprot']['sequence'][domain['start_pos']-1:domain['end_pos']]            
                occurrence_entry = {'gene_name':gene_name, 
                                    'identifier':occurence_id, 
                                    'sequence':occurrence_sequence,
                                    'start_pos':domain['start_pos'],
                                    'end_pos':domain['end_pos']}
                if occurrence_sequence != '':
                    domain_of_interest_occurrences.append(occurrence_entry)
                else:
                    logging.getLogger(LOGGER_NAME).warning("Domain occurrence '"+occurence_id+"' did not have a sequence and therefore was not considered")
    
    # Report statistics
    logging.getLogger(LOGGER_NAME).info("Found '"+str(len(domain_of_interest_occurrences))+"' occurrences of '"+domain_id+"' across HG19 over '"+str(len(pd.unique(domain_of_interest_domain_data.gene_name)))+"' genes")
    
    # Retrieve all the sequences of the domain of interest
    domain_of_interest_sequences = [domain_occurrence['sequence'] for domain_occurrence in domain_of_interest_occurrences]
    
    logging.getLogger(LOGGER_NAME).info("Starting HMM based alignment on for domain '"+domain_id+"' for '"+str(len(domain_of_interest_domain_data))+"' occurrences across HG19")
    # Run the HMMERAlign algorithm based on the Pfam HMM
    try:
        hmmeralign_output = HMMERApi.align_sequences_according_to_PFAM_HMM(domain_of_interest_sequences, domain_id)
    except (FoundNoPfamHMMException, FoundMoreThanOnePfamHMMException) as e:
        logging.getLogger(LOGGER_NAME).error(e)
        time_step = time.clock()
        logging.getLogger(LOGGER_NAME).info("Prematurely stopped creating the '"+domain_id+"' 'meta'-domain in "+str(time_step-start_time)+" seconds")
        return None
    logging.getLogger(LOGGER_NAME).info("Finished HMM based alignment on for domain '"+domain_id+"'")
    
    logging.getLogger(LOGGER_NAME).info("Starting annotation of the '"+domain_id+"' domains with ExAC, ClinVar, and HGMD information")
    ignore_list_of_indices = []
    for index in range(len(hmmeralign_output['alignments'])):
        domain_occurrence = domain_of_interest_occurrences[index]
        try:
            gene_mapping = gene_mappings[domain_occurrence['gene_name']]
            domain_region = analyse_dn_ds_over_protein_region(gene_mapping, domain_occurrence['start_pos']-1, domain_occurrence['end_pos'])
            hgmd_variation = domain_region['hgmd_information']
            clinvar_variation = domain_region["clinvar_information"]
            exac_variation = domain_region['exac_information']
            domain_occurrence['hgmd_information'] = sorted(hgmd_variation, key=lambda k: k['uniprot_pos'])
            domain_occurrence['exac_information'] = sorted(exac_variation, key=lambda k: k['uniprot_pos'])
            domain_occurrence['clinvar_information'] = sorted(clinvar_variation, key=lambda k: k['uniprot_pos']) 
        except (RegionIsNotEncodedBycDNAException, RegioncDNALengthDoesNotEqualProteinLengthException) as e:
            logging.getLogger(LOGGER_NAME).error(e)
            ignore_list_of_indices.append(index)
    logging.getLogger(LOGGER_NAME).info("Finished annotating the '"+domain_id+"' domains with ExAC, ClinVar, and HGMD information: '"+str(len(domain_of_interest_domain_data)-len(ignore_list_of_indices)) +"' domain occurrences of the original '"+str(len(domain_of_interest_domain_data))+"' occurrences remained")
    
    # Create the strict versions of the consensus alignment
    logging.getLogger(LOGGER_NAME).info("Creating the mappings for '"+str(len(domain_of_interest_domain_data)-len(ignore_list_of_indices)) +"' '"+domain_id+"' domain occurrences based on the HMM alignment to consensus and original domain sequence")
    
    # ensure we can map consensus residues back to consensus positions
    hmmeralign_output['consensus']['aligned_sequence'] = convert_pfam_fasta_alignment_to_original_aligned_sequence(hmmeralign_output['consensus']['alignment'])
    hmmeralign_output['consensus']['mapping_consensus_alignment_to_positions'] = map_sequence_to_aligned_sequence(hmmeralign_output['consensus']['sequence'], hmmeralign_output['consensus']['aligned_sequence'])
    
    # create mappings between domain occurrences and the domain consensus sequence
    for index in range(len(hmmeralign_output['alignments'])):
        if index not in ignore_list_of_indices:
            # retrieve current aligned domain
            domain_occurrence = domain_of_interest_occurrences[index]
            
            # Create a mapping from the aligned domain sequence to the domain sequence
            domain_occurrence['aligned_sequence'] = convert_pfam_fasta_alignment_to_original_aligned_sequence(hmmeralign_output['alignments'][index]['alignment'])
            domain_occurrence['mapping_domain_alignment_to_sequence_positions'] = map_sequence_to_aligned_sequence(domain_occurrence['sequence'], domain_occurrence['aligned_sequence'])
            
            # Generate the strict sequence for this domain; leaving only residues that were aligned to the domain consensus
            domain_occurrence['strict_aligned_sequence'] = convert_pfam_fasta_alignment_to_strict_fasta(hmmeralign_output['alignments'][index]['alignment'])
            
            # create the mapping between the strict alignments and the original consensus sequence
            domain_occurrence['mapping_aligned_domain_to_domain_consensus'] = createAlignedSequenceMapping(domain_occurrence['strict_aligned_sequence'], hmmeralign_output['consensus']['aligned_sequence'], False)
            
    logging.getLogger(LOGGER_NAME).info("Finished the mappings for '"+str(len(domain_of_interest_domain_data)-len(ignore_list_of_indices)) +"' '"+domain_id+"' domain occurrences")
    
    # Add the reference genome information
    logging.getLogger(LOGGER_NAME).info("Starting appending reference genome information to the '"+domain_id+"' 'meta'-domain")
    reference_domain_consensus = []
    for index in range(len(hmmeralign_output['alignments'])):
        if index not in ignore_list_of_indices:
            domain_occurrence = domain_of_interest_occurrences[index]
            gene_mapping = gene_mappings[domain_occurrence['gene_name']]
            for mapping_pos in sorted(domain_occurrence['mapping_aligned_domain_to_domain_consensus'].keys()):
                # retrieve the position in the domain consensus
                domain_consensus_pos = hmmeralign_output['consensus']['mapping_consensus_alignment_to_positions'][mapping_pos]
                # retrieve the position in the domain sequence
                ref_pos = domain_occurrence['mapping_domain_alignment_to_sequence_positions'][mapping_pos]
                
                # convert the position in the domain sequence to the uniprot position and genomic position
                uniprot_pos = domain_occurrence['start_pos'] + ref_pos -1
                cDNA_pos = (uniprot_pos * 3)+1
                cDNA_codon_end_pos = cDNA_pos+2
                
                # retrieve the residue at the consensus position and the residue at the domain position
                consensus_domain_residue = hmmeralign_output['consensus']['aligned_sequence'][mapping_pos]
                aligned_residue = domain_occurrence['aligned_sequence'][mapping_pos]
                
                # Double check if the mapped residues match 
                translation_residue = gene_mapping['GenomeMapping']['cDNA'][str(cDNA_pos)]['translation_residue']
                uniprot_residue = gene_mapping['GenomeMapping']['cDNA'][str(cDNA_pos)]['uniprot_residue']
                uniprot_residue_double_check = gene_mapping['uniprot']['sequence'][uniprot_pos]
                
                # Retrieve the genomic start and stop pos
                chromosome, genomic_start_pos = gene_mapping['GenomeMapping']['cDNA'][str(cDNA_pos)]['Genome'].split(':')
                chromosome_double_check, genomic_stop_pos = gene_mapping['GenomeMapping']['cDNA'][str(cDNA_codon_end_pos)]['Genome'].split(':')
                
                if aligned_residue != uniprot_residue:
                    logging.getLogger(LOGGER_NAME).error("At reference genome annotation: For domain '"+str(domain_id)+
                                                           "' for occurrence '"+str(domain_occurrence['identifier'])+
                                                           "' at aligned position '"+str(mapping_pos)+
                                                           "' aligned sequence residue '"+aligned_residue+
                                                           "' did not match uniprot residue '"+uniprot_residue+"'")
                    continue
                
                if translation_residue != uniprot_residue:
                    logging.getLogger(LOGGER_NAME).error("At reference genome annotation: For domain '"+str(domain_id)+
                                                           "' for occurrence '"+str(domain_occurrence['identifier'])+
                                                           "' at aligned position '"+str(mapping_pos)+
                                                           "' translation residue '"+translation_residue+
                                                           "' did not match uniprot residue '"+uniprot_residue+"'")
                    continue
                
                if uniprot_residue != uniprot_residue_double_check:
                    logging.getLogger(LOGGER_NAME).error("At reference genome annotation: For domain '"+str(domain_id)+
                                                           "' for occurrence '"+str(domain_occurrence['identifier'])+
                                                           "' at aligned position '"+str(mapping_pos)+
                                                           "' uniprot residue '"+uniprot_residue+
                                                           "' did not match double check uniprot residue '"+
                                                           uniprot_residue_double_check+"'")
                    continue
                
                if chromosome != chromosome_double_check:
                    logging.getLogger(LOGGER_NAME).error("At reference genome annotation: For domain '"+str(domain_id)+
                                                           "' for occurrence '"+str(domain_occurrence['identifier'])+
                                                           "' at aligned position '"+str(mapping_pos)+
                                                           "' chromosome '"+chromosome+
                                                           "' did not match double check chromosome '"+
                                                           chromosome_double_check+"'")
                    continue
                
                if gene_mappings[domain_occurrence['gene_name']]["translation_used"]["sequence"][uniprot_pos] == uniprot_residue:
                    
                    reference_domain_consensus_entry = {
                        'gencode_transcription_id':gene_mappings[domain_occurrence['gene_name']]["translation_used"]["transcription-id"],
                        'gencode_translation_name':gene_mappings[domain_occurrence['gene_name']]["translation_used"]["translation-name"],
                        'gencode_gene_id':gene_mappings[domain_occurrence['gene_name']]["translation_used"]["gene_name-id"],
                        'uniprot_ac':gene_mappings[domain_occurrence['gene_name']]['uniprot']['uniprot_ac'],
                        'uniprot_name':gene_mappings[domain_occurrence['gene_name']]['uniprot']['uniprot_name'],
                        'domain_identifier':domain_occurrence['identifier'],
                        'gene_name':domain_occurrence['gene_name'],
                        'swissprot_pos':uniprot_pos,
                        'domain_consensus_pos':domain_consensus_pos,
                        'chr':chromosome,
                        'chr_start':genomic_start_pos,
                        'chr_stop':genomic_stop_pos,
                        'ref_codon':gene_mapping['GenomeMapping']['cDNA'][str(cDNA_pos)]['translation_codon'],
                        'consensus_domain_residue': consensus_domain_residue,
                        'ref_residue':uniprot_residue,    
                    }
                    reference_domain_consensus.append(reference_domain_consensus_entry)
                else:
                    logging.getLogger(LOGGER_NAME).error("At reference genome annotation: For domain '"+str(domain_id)+
                                                       "' for occurrence '"+str(domain_occurrence['identifier'])+
                                                       "' at aligned position '"+str(uniprot_pos)+
                                                       "' uniprot residue '"+uniprot_residue+
                                                       "' did not translation reference residue '"+
                                                       gene_mappings[domain_occurrence['gene_name']]["translation_used"]["sequence"][uniprot_pos]+"'")
                        
    logging.getLogger(LOGGER_NAME).info("Finished appending reference genome information to the '"+domain_id+"' 'meta'-domain")
    
    # convert the domain consesus mapping into a dataframe
    reference_domain_consensus_df = pd.DataFrame(reference_domain_consensus)

    # Annotate genic information from the gene -> domain occurrence -> domain consensus
    # ExAC information
    logging.getLogger(LOGGER_NAME).info("Starting appending ExAC information to the '"+domain_id+"' 'meta'-domain")
    ExAC_additional_information_keys = {'alt_residue':'alt_residue', 'alt_codon':'alt_codon', 'ExAC_allele_frequency':'AF'}
    ExAC_annotated_domain_consensus = annotate_genic_information('ExAC', 'exac_information', reference_domain_consensus_df, domain_id, hmmeralign_output, domain_of_interest_occurrences, ignore_list_of_indices, ExAC_additional_information_keys)
    logging.getLogger(LOGGER_NAME).info("Finished appending ExAC information to the '"+domain_id+"' 'meta'-domain")
    # HGMD information
    logging.getLogger(LOGGER_NAME).info("Starting appending HGMD information to the '"+domain_id+"' 'meta'-domain")
    HGMD_additional_information_keys = {'alt_residue':'alt_residue', 'alt_codon':'alt_codon', 'HGMD_Prot':"PROT", 'HGMD_Phenotype':'PHEN', 'HGMD_Dna':"DNA", 'HGMD_STRAND':"STRAND", 'HGMD_MUT':"MUT", }
    HGMD_annotated_domain_consensus = annotate_genic_information('HGMD', 'hgmd_information', reference_domain_consensus_df, domain_id, hmmeralign_output, domain_of_interest_occurrences, ignore_list_of_indices, HGMD_additional_information_keys)
    logging.getLogger(LOGGER_NAME).info("Finished appending HGMD information to the '"+domain_id+"' 'meta'-domain")
    # ClinVar information
    logging.getLogger(LOGGER_NAME).info("Starting appending ClinVar information to the '"+domain_id+"' 'meta'-domain")
    ClinVar_additional_information_keys = {'alt_residue':'alt_residue', 'alt_codon':'alt_codon', 'ClinVar_ID':"ID", 'ClinVar_alleleID':'ALLELEID', 'ClinVar_review_stat':'CLNREVSTAT', 'ClinVar_disease_name':'CLNDN', 'ClinVar_disease_db':'CLNDISDB', 'ClinVar_sources':'CLNVI', 'ClinVar_geneinfo':'GENEINFO', 'ClinVar_allele_origin':'ORIGIN', 'ClinVar_SO':'CLNVCSO',}
    ClinVar_annotated_domain_consensus = annotate_genic_information('ClinVar', 'clinvar_information', reference_domain_consensus_df, domain_id, hmmeralign_output, domain_of_interest_occurrences, ignore_list_of_indices, ClinVar_additional_information_keys)
    logging.getLogger(LOGGER_NAME).info("Finished appending ClinVar information to the '"+domain_id+"' 'meta'-domain")
   
    # Formalize the meta domain
    meta_domain = {'domain_id':domain_id,
            'identifier':hmmeralign_output['consensus']['identifier'],
            'consensus_sequence':hmmeralign_output['consensus']['sequence'],
            'consensus_alignment':hmmeralign_output['consensus']['alignment'],
            'consensus_strict_alignment':hmmeralign_output['consensus']['aligned_sequence'],
            'HGMD':HGMD_annotated_domain_consensus,
            'ExAC':ExAC_annotated_domain_consensus,
            'ClinVar':ClinVar_annotated_domain_consensus,
            'reference':reference_domain_consensus,
            'failed_domains':[domain_of_interest_occurrences[index] for index in range(len(hmmeralign_output['alignments'])) if index not in ignore_list_of_indices]}
    
    logging.getLogger(LOGGER_NAME).info("Starting creating a merged domain consisting of HGMD, ExAC, ClinVar, and Reference information for the '"+domain_id+"' 'meta'-domain")
    merged_meta_domain = merge_meta_domain(meta_domain, minimal_merged_meta_domain_ExAC_frequency, merged_meta_domain_missense_only)
    meta_domain['merged_meta_domain'] = merged_meta_domain.to_dict('records')
    logging.getLogger(LOGGER_NAME).info("Finished creating a merged domain consisting of HGMD, ExAC, ClinVar, and Reference information for the '"+domain_id+"' 'meta'-domain")
    
    time_step = time.clock()
    logging.getLogger(LOGGER_NAME).info("Finished creating the '"+domain_id+"' 'meta'-domain in "+str(time_step-start_time)+" seconds")
    return meta_domain

if __name__ == '__main__':
    from BGVM.Tools.CustomLogger import initLogging
    from dev_settings import GENE2PROTEIN_ANNOTATED_HOMOLOGUE_DOMAINS_DATASET
    from BGVM.Domains.HomologuesDomains import load_homologue_domain_dataset
    from meta_domain_database_settings import FILTER_ON_MISSENSE_ONLY
    from meta_domain_database_settings import FILTER_ON_MINIMAL_EXAC_FREQUENCY
    initLogging(print_to_console=True, logging_level=logging.DEBUG)
     
    data = load_homologue_domain_dataset(GENE2PROTEIN_ANNOTATED_HOMOLOGUE_DOMAINS_DATASET)
      
    meta_domain_a = create_annotated_meta_domain('PF00048', data, FILTER_ON_MINIMAL_EXAC_FREQUENCY, FILTER_ON_MISSENSE_ONLY)
    meta_domain_b = create_annotated_meta_domain('PF00153', data, FILTER_ON_MINIMAL_EXAC_FREQUENCY, FILTER_ON_MISSENSE_ONLY)
    meta_domain_c = create_annotated_meta_domain('PF00008', data, FILTER_ON_MINIMAL_EXAC_FREQUENCY, FILTER_ON_MISSENSE_ONLY)
    meta_domain_d = create_annotated_meta_domain('PF00089', data, FILTER_ON_MINIMAL_EXAC_FREQUENCY, FILTER_ON_MISSENSE_ONLY)
    