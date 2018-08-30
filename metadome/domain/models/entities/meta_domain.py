from metadome.domain.services.annotation.annotation import annotateSNVs
from metadome.domain.services.annotation.gene_region_annotators import annotateTranscriptWithClinvarData,\
    annotateTranscriptWithGnomADData
from metadome.domain.data_generation.mapping.meta_domain_mapping import generate_pfam_aligned_codons
from metadome.domain.models.entities.codon import Codon
from metadome.domain.models.entities.single_nucleotide_variant import SingleNucleotideVariant
from metadome.default_settings import METADOMAIN_DIR,\
    METADOMAIN_MAPPING_FILE_NAME, METADOMAIN_DETAILS_FILE_NAME,\
    METADOMAIN_SNV_ANNOTATION_FILE_NAME
import pandas as pd
import json
import os

import logging

_log = logging.getLogger(__name__)

class UnsupportedMetaDomainIdentifier(Exception):
    pass

class ConsensusPositionOutOfBounds(Exception):
    pass

class MetaDomain(object):
    """
    MetaDomain Model Entity
    Used for representation of meta domains
    
    Variables
    name                       description
    domain_id                  str the id / accession code of this domain 
    consensus_length           int length of the domain consensus
    n_proteins                 int number of unique proteins containing this domain
    n_instances                int number of unique instances containing this domain
    n_transcripts              int number of unique transcripts containing this domain
    meta_domain_mapping        pandas.DataFrame containing all codons annotated with corresponding consensus position
    meta_domain_annotation     pandas.DataFrame containing all SNVs with corresponding consensus position
    """
    
    def get_annotated_SNVs_for_consensus_position(self, consensus_position):
        #TODO: make a filtering here based on unque_snv_representation
        pass
    
    def get_consensus_positions_for_uniprot_position(self, uniprot_ac, uniprot_position):
        """Retrieves the consensus positions for this MetaDomain
        based on the uniprot ac and position"""
        consensus_positions = []
        # Retrieve all codons aligned to the consensus position
        aligned_to_position = self.meta_domain_mapping[(self.meta_domain_mapping.uniprot_ac == uniprot_ac) &\
                                                       (self.meta_domain_mapping.amino_acid_position == uniprot_position)]
        
        # check if there are any matches
        if len(aligned_to_position) > 0:
            # check how many matches and type check if all positions are the same
            unique_consensus_positions = pd.unique(aligned_to_position.consensus_pos)
            
            if len(unique_consensus_positions) > 1:
                _log.warning("There are more than one consensus positions assigned ('"+str(unique_consensus_positions)+"') to the protein '"+str(uniprot_ac)+"' for position '"+str(uniprot_position)+"'")
            
            consensus_positions = []
            for c_pos in unique_consensus_positions:
                consensus_positions.append(int(c_pos))
        else:
            _log.info("No alignment for domain '"+str(self.domain_id)+"' for uniprot_ac '"+str(uniprot_ac)+"' on position '"+str(uniprot_position)+"'" )
        
        return consensus_positions
    
    def get_codons_aligned_to_consensus_position(self, consensus_position):
        """Retrieves codons for this consensus position as:
        {Codon.unique_str_representation(): Codon}"""
        codons = {}
        
        if consensus_position < 0:
            raise ConsensusPositionOutOfBounds("The provided consensus position ('"+str(consensus_position)+"') is below zero, this position foes not exist")
        if consensus_position >= self.consensus_length:
            raise ConsensusPositionOutOfBounds("The provided consensus position ('"+str(consensus_position)+"') is above the maximum consensus length ('"+str(self.consensus_length)+"'), this position foes not exist")
        
        # Retrieve all codons aligned to the consensus position
        aligned_to_position = self.meta_domain_mapping[self.meta_domain_mapping.consensus_pos == consensus_position].to_dict('records')
        
        # first check if the consensus position is present in the mappings_per_consensus_pos
        if len(aligned_to_position) >0:
            codons = dict()
            for codon_dict in aligned_to_position:
                # initialize a codon from the dataframe row
                codon = Codon.initializeFromDict(codon_dict)
                
                # aggregate duplicate chromosomal regions
                if not codon.unique_str_representation() in codons.keys():
                    codons[codon.unique_str_representation()] = []

                # add the codon to the dictionary
                codons[codon.unique_str_representation()].append(codon)
                
        # return the codons that correspond to this position
        return codons
    
    def annotate_metadomain(self, reannotate=False):
        """Annotate this meta domain with gnomAD and ClinVar variants"""
        # check if a Meta Domain is already mapped
        meta_domain_dir = METADOMAIN_DIR+self.domain_id
        meta_domain_snv_annotation_file = meta_domain_dir+'/'+METADOMAIN_SNV_ANNOTATION_FILE_NAME
        
        # initialize the meta_domain_annotation as a list
        meta_domain_annotation = []
        
        # Check if the mapping has previously been annotated already
        if os.path.exists(meta_domain_snv_annotation_file) and not reannotate:
            # The mapping exists, load it
            _log.info('Loading previously annotated MetaDomain for domain id: '+str(self.domain_id))
            # Read the files
            _log.info("Reading '{}'".format(meta_domain_snv_annotation_file))
            meta_domain_annotation = pd.read_csv(meta_domain_snv_annotation_file)
        else:
            # The annotation does not exists yet, or needs be recreated/reannotated
            _log.info('Start annotation of MetaDomain for domain id: '+str(self.domain_id))
           
            # Retrieve all codons
            for consensus_position in range(self.consensus_length):
                meta_codons = self.get_codons_aligned_to_consensus_position(consensus_position)
                
                # iterate over meta_codons and add to metadom_entry
                for meta_codon_repr in meta_codons.keys():
                    # Check if we are dealing with the gene and protein_pos of interest
                    # just take the first
                    meta_codon = meta_codons[meta_codon_repr][0]
                    
                    gnomad_variant_annotation = annotateSNVs(annotateTranscriptWithGnomADData,
                                             mappings_per_chr_pos=meta_codon.retrieve_mappings_per_chromosome(),
                                             strand=meta_codon.strand, 
                                             chromosome=meta_codon.chr,
                                             regions=meta_codon.regions)
                    
                    for chrom_pos in gnomad_variant_annotation.keys():
                        for variant in gnomad_variant_annotation[chrom_pos]:
                            for _codon in meta_codons[meta_codon_repr]:
                                # create a variant object for this variant
                                variant = SingleNucleotideVariant.initializeFromVariant(_codon=_codon, _chr_position=chrom_pos, _alt_nucleotide=variant['ALT'], _variant_source='gnomAD')
                                
                                # create the variant entry
                                variant_entry = variant.toDict()
                                variant_entry['unique_snv_str_representation'] = variant.unique_snv_str_representation()
                                
                                # append gnomAD specific information
                                variant_entry['allele_number'] = variant['AN']
                                variant_entry['allele_count'] = variant['AC']
                                
                                meta_domain_annotation.append(variant_entry)
                    
                    clinvar_variant_annotation = annotateSNVs(annotateTranscriptWithClinvarData,
                                             mappings_per_chr_pos=meta_codon.retrieve_mappings_per_chromosome(),
                                             strand=meta_codon.strand, 
                                             chromosome=meta_codon.chr,
                                             regions=meta_codon.regions)
                    
                    
                    for chrom_pos in clinvar_variant_annotation.keys():
                        for variant in clinvar_variant_annotation[chrom_pos]:
                            for _codon in meta_codons[meta_codon_repr]:
                                # create a variant object for this variant
                                variant = SingleNucleotideVariant.initializeFromVariant(_codon=_codon, _chr_position=chrom_pos, _alt_nucleotide=variant['ALT'], _variant_source='ClinVar')
                                
                                # create the variant entry
                                variant_entry = variant.toDict()
                                variant_entry['unique_snv_str_representation'] = variant.unique_snv_str_representation()
                                
                                # append ClinVar specific information
                                variant_entry['clinvar_ID'] = variant['ID']
                                
                                meta_domain_annotation.append(variant_entry)
                        
            # convert meta_domain_mapping to a pandas Dataframe
            meta_domain_annotation = pd.DataFrame(meta_domain_annotation)
            
            # save meta_domain_mapping to disk
            meta_domain_annotation.to_csv(meta_domain_snv_annotation_file)
            
            # set to variable
            self.meta_domain_annotation = meta_domain_annotation
            
            _log.info('Finished annotation of MetaDomain for domain id: '+str(self.domain_id))
    
    def __init__(self, domain_id, consensus_length, n_instances, meta_domain_mapping):
        self.domain_id = domain_id
        self.consensus_length = consensus_length
        self.n_instances = n_instances
        self.meta_domain_mapping = meta_domain_mapping
        self.meta_domain_annotation = pd.DataFrame()
        
        # derive from meta_domain_mapping
        self.n_proteins = len(pd.unique(self.meta_domain_mapping.uniprot_ac))
        self.n_transcripts = len(pd.unique(self.meta_domain_mapping.gencode_transcription_id))
        
        # Annotate this meta domain
        self.annotate_metadomain()
        
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
        