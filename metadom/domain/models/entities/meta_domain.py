from metadom.domain.repositories import InterproRepository
from metadom.domain.data_generation.mapping.meta_domain_mapping import generate_pfam_alignment_mappings

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
    n_proteins                    int number of unique genes containing this domain
    n_instances                int number of unique instances containing this domain
    mappings_per_consensus_pos dictionary of mappings per metadomain consensus positions; {POS: [models.mapping.Mapping]}
    consensus_pos_per_protein  dictionary of protein ids with their uniprot positions mapped to consensus {protein_is: {uniprot_pos:<int:consensus_position>}}
    """
    domain_id = str() 
    consensus_length = int()
    n_proteins = int()
    n_instances = int()
    mappings_per_consensus_pos = dict()
    consensus_pos_per_protein = dict()
    
    def __init__(self, domain_id):
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
        