from metadom.domain.repositories import InterproRepository
from metadom.domain.data_generation.mapping.meta_domain_mapping import generate_pfam_alignment_mappings
from metadom.domain.models.entities.codon import Codon, MalformedCodonException
from metadom.domain.models.entities.meta_codon import MetaCodon, MalformedAggregatedCodon

class UnsupportedMetaDomainIdentifier(Exception):
    pass

class NotEnoughOccurrencesForMetaDomain(Exception):
    pass

class MalformedMappingsForMetaDomainPosition(Exception):
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
        """Retrieves meta_codons for this consensus position"""
        codons = []
        
        # first check if the consensus position is present in the mappings_per_consensus_pos
        if consensus_position in self.mappings_per_consensus_pos.keys():
            mapping_per_gene_per_amino_acid_pos = dict()
            
            # first gather all mappings for the unique gene ids in combination with the amino acid pos
            for mapping in self.mappings_per_consensus_pos[consensus_position]:
                if not mapping.gene_id in mapping_per_gene_per_amino_acid_pos.keys():
                    mapping_per_gene_per_amino_acid_pos[mapping.gene_id] = dict()
                
                if not mapping.amino_acid_position in mapping_per_gene_per_amino_acid_pos[mapping.gene_id].keys():
                    mapping_per_gene_per_amino_acid_pos[mapping.gene_id][mapping.amino_acid_position] = []
                    
                mapping_per_gene_per_amino_acid_pos[mapping.gene_id][mapping.amino_acid_position].append(mapping)
            
            unique_codons = dict()
            # retrieve the codons for these positions
            for gene_id in mapping_per_gene_per_amino_acid_pos.keys():
                for amino_acid_position in mapping_per_gene_per_amino_acid_pos[gene_id].keys():
                    try:
                        codon = Codon(mapping_per_gene_per_amino_acid_pos[gene_id][amino_acid_position])
                        # aggregate duplicate chromosomal regions
                        if not codon.unique_str_representation() in unique_codons.keys():
                            unique_codons[codon.unique_str_representation()] = []
                        
                        # add the codon to the dictionary
                        unique_codons[codon.unique_str_representation()].append(codon)
                    except MalformedCodonException as e:
                        raise MalformedMappingsForMetaDomainPosition("Encountered a malformed codon mapping for domain '"
                                                                     +str(self.domain_id)+"' in gene '"+str(gene_id)
                                                                     +"', at amino_acid_position '"+str(amino_acid_position)
                                                                     +"':" + str(e))
            
            # Now convert the codons to meta_codons
            try:
                codons = [MetaCodon(unique_codons[key]) for key in unique_codons.keys()]
            except MalformedAggregatedCodon as e:
                raise MalformedMappingsForMetaDomainPosition("Encountered a malformed aggregation of codons for domain '"
                                                             +str(self.domain_id)+"' at domain consensus position '"
                                                             +str(consensus_position)+"': " + str(e))
                
        # return the codons that correspond to this position
        return codons
            
            
    
    def __init__(self, domain_id):
        self.domain_id = str() 
        self.consensus_length = int()
        self.n_proteins = int()
        self.n_instances = int()
        self.mappings_per_consensus_pos = dict()
        self.consensus_pos_per_protein = dict()

        if domain_id.startswith('PF'):
            self.domain_id = domain_id
        
            # retrieve all domain occurrences for the domain_id
            domain_of_interest_occurrences = InterproRepository.get_domains_for_ext_domain_id(self.domain_id)    
            if len(domain_of_interest_occurrences) == 0:
                raise NotEnoughOccurrencesForMetaDomain("Domain '"+str(self.domain_id)+"' does not exists in the database")
            if len(domain_of_interest_occurrences) == 1:
                raise NotEnoughOccurrencesForMetaDomain("There are not enough occurrences for the '"+str(self.domain_id)+"' to create a meta domain")
            
            # create the meta domain mapping
            self.mappings_per_consensus_pos, self.consensus_pos_per_protein = generate_pfam_alignment_mappings(self.domain_id, domain_of_interest_occurrences)
            
            # set the remaining values
            self.n_instances = len(domain_of_interest_occurrences)
            self.consensus_length = len(self.mappings_per_consensus_pos)
            self.n_proteins = len(self.consensus_pos_per_protein)
        else:
            raise UnsupportedMetaDomainIdentifier("Expected a Pfam domain, instead the identifier '"+str(domain_id)+"' was received")
    
    def __repr__(self):
        return "<MetaDomain(domain_id='%s', consensus_length='%s', n_proteins='%s', n_instances='%s')>" % (
                            self.domain_id, self.consensus_length, self.n_proteins, self.n_instances)
        