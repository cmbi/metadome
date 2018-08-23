from metadome.domain.data_generation.mapping.meta_domain_mapping import generate_pfam_aligned_codons
from metadome.domain.models.entities.codon import Codon, MalformedCodonException
from metadome.default_settings import METADOMAIN_DIR,\
    METADOMAIN_MAPPING_FILE_NAME, METADOMAIN_DETAILS_FILE_NAME
import pandas as pd
import json
import os

import logging

_log = logging.getLogger(__name__)

class UnsupportedMetaDomainIdentifier(Exception):
    pass

class NotEnoughOccurrencesForMetaDomain(Exception):
    pass

class MetaDomain(object):
    """
    MetaDomain Model Entity
    Used for representation of meta domains
    
    Variables
    name                       description
    domain_id                  str the id / accession code of this domain 
    consensus_length           int length of the domain consensus
    n_proteins                 int number of unique genes containing this domain
    n_instances                int number of unique instances containing this domain
    mappings_per_consensus_pos dictionary of mappings per metadomain consensus positions; {POS: [models.mapping.Mapping]}
    consensus_pos_per_protein  dictionary of protein ids with their uniprot positions mapped to consensus {protein_id: {uniprot_pos:<int:consensus_position>}}
    """
    
    def get_codons_aligned_to_consensus_position(self, consensus_position):
        # TODO: should return meta-codons based on the dataframe
#         pass
        """Retrieves meta_codons for this consensus position"""
        codons = []
        
#         # first check if the consensus position is present in the mappings_per_consensus_pos
#         if consensus_position in self.mappings_per_consensus_pos.keys():
#             mapping_per_gene_per_amino_acid_pos = dict()
#             
#             # first gather all mappings for the unique gene ids in combination with the amino acid pos
#             for mapping in self.mappings_per_consensus_pos[consensus_position]:
#                 if not mapping.gene_id in mapping_per_gene_per_amino_acid_pos.keys():
#                     mapping_per_gene_per_amino_acid_pos[mapping.gene_id] = dict()
#                 
#                 if not mapping.amino_acid_position in mapping_per_gene_per_amino_acid_pos[mapping.gene_id].keys():
#                     mapping_per_gene_per_amino_acid_pos[mapping.gene_id][mapping.amino_acid_position] = []
#                     
#                 mapping_per_gene_per_amino_acid_pos[mapping.gene_id][mapping.amino_acid_position].append(mapping)
#             
#             unique_codons = dict()
#             # retrieve the codons for these positions
#             for gene_id in mapping_per_gene_per_amino_acid_pos.keys():
#                 for amino_acid_position in mapping_per_gene_per_amino_acid_pos[gene_id].keys():
#                     try:
#                         _gencode_transcription_id = self.gencode_transcription_id_per_gene_id[gene_id]
#                         _uniprot_ac = self.protein_ac_per_protein_id[mapping_per_gene_per_amino_acid_pos[gene_id][amino_acid_position][0].protein_id]
#                         codon = Codon.initializeFromMapping(mapping_per_gene_per_amino_acid_pos[gene_id][amino_acid_position], _gencode_transcription_id, _uniprot_ac)
#                         # aggregate duplicate chromosomal regions
#                         if not codon.unique_str_representation() in unique_codons.keys():
#                             unique_codons[codon.unique_str_representation()] = []
#                         
#                         # add the codon to the dictionary
#                         unique_codons[codon.unique_str_representation()].append(codon)
#                     except MalformedCodonException as e:
#                         raise MalformedMappingsForMetaDomainPosition("Encountered a malformed codon mapping for domain '"
#                                                                      +str(self.domain_id)+"' in gene '"+str(gene_id)
#                                                                      +"', at amino_acid_position '"+str(amino_acid_position)
#                                                                      +"':" + str(e))
#             
#             # Now convert the codons to meta_codons
#             try:
#                 codons = [MetaCodon(unique_codons[key]) for key in unique_codons.keys()]
#             except MalformedAggregatedCodon as e:
#                 raise MalformedMappingsForMetaDomainPosition("Encountered a malformed aggregation of codons for domain '"
#                                                              +str(self.domain_id)+"' at domain consensus position '"
#                                                              +str(consensus_position)+"': " + str(e))
                
        # return the codons that correspond to this position
        return codons

    
    def __init__(self, domain_id, consensus_length, n_instances, meta_domain_mapping):
        self.domain_id = domain_id
        self.consensus_length = consensus_length
        self.n_instances = n_instances
        self.meta_domain_mapping = meta_domain_mapping
        
        # derive from meta_domain_mapping
        self.n_proteins = len(pd.unique(self.meta_domain_mapping.uniprot_ac))
        self.n_transcripts = len(pd.unique(self.meta_domain_mapping.gencode_transcription_id))
        
    @classmethod
    def initializeFromDomainID(cls, domain_id, recreate=False):        
        _log.info('Start initialization of MetaDomain for domain id: '+str(domain_id))
        
        # Set values needed for construction of this class
        consensus_length = 0
        meta_domain_mapping = []

        # Double check this conserns a Pfam domain
        if domain_id.startswith('PF'):
            # check if a Meta Domain is already mapped
            meta_domain_dir = METADOMAIN_DIR+domain_id
            meta_domain_details_file = meta_domain_dir+'/'+METADOMAIN_DETAILS_FILE_NAME
            meta_domain_mapping_file = meta_domain_dir+'/'+METADOMAIN_MAPPING_FILE_NAME
            
            # first check if the metadomain dir exist
            if not os.path.isdir(meta_domain_dir):
                raise UnsupportedMetaDomainIdentifier("For Pfam ID '"+str(domain_id)+"' there was no metadomain alignment present")
            
            # Check if the mapping has previously been build already
            if os.path.exists(meta_domain_mapping_file) and os.path.exists(meta_domain_details_file) and not recreate:
                # The mapping exists, load it
                _log.info('Loading previously build creation of MetaDomain for domain id: '+str(domain_id))
                # Read the files
                _log.info("Reading '{}'".format(meta_domain_mapping_file))
                meta_domain_mapping = pd.read_csv(meta_domain_mapping_file)
                _log.info("Reading '{}'".format(meta_domain_details_file))
                with open(meta_domain_details_file) as f:
                    meta_domain_details = json.load(f)
                    
                consensus_length = meta_domain_details['consensus_length']
                n_instances = meta_domain_details['n_instances']
            else:
                # The mapping does not exists yet, we need to create it
                _log.info('Start creation of MetaDomain for domain id: '+str(domain_id))
               
                # create the meta domain mapping alignment
                meta_codons_per_consensus_pos, consensus_length, n_instances = generate_pfam_aligned_codons(domain_id)
                
                # create the meta_domain_details
                meta_domain_details = {}
                meta_domain_details['consensus_length'] = consensus_length
                meta_domain_details['n_instances'] = n_instances
                
                # create the dataframe context for this meta_domain
                for consensus_pos in meta_codons_per_consensus_pos.keys():
                    for codon in meta_codons_per_consensus_pos[consensus_pos]:
                        _meta_codon = codon.toDict()
                        _meta_codon['consensus_pos'] = consensus_pos
                        _meta_codon['domain_id'] = domain_id
                        
                        meta_domain_mapping.append(_meta_codon)
                    
                # convert meta_domain_mapping to a pandas Dataframe
                meta_domain_mapping = pd.DataFrame(meta_domain_mapping)
                
                ## Save the results to disk
                # save meta_domain_details
                with open(meta_domain_details_file, 'w') as f:
                    json.dump(meta_domain_details, f)
                
                # save meta_domain_mapping to disk
                meta_domain_mapping.to_csv(meta_domain_mapping_file)
        else:
            raise UnsupportedMetaDomainIdentifier("Expected a Pfam domain, instead the identifier '"+str(domain_id)+"' was received")
        
        # Attempt to create the object
        meta_domain = cls(domain_id, consensus_length, n_instances, meta_domain_mapping)
        
        # return the object
        return meta_domain
    
    def __repr__(self):
        return "<MetaDomain(domain_id='%s', consensus_length='%s', n_proteins='%s', n_instances='%s')>" % (
                            self.domain_id, self.consensus_length, self.n_proteins, self.n_instances)
        