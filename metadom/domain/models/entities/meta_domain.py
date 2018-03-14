from metadom.domain.repositories import InterproRepository
from metadom.domain.data_generation.mapping.mapping_generator import generate_pfam_alignment_mappings

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
    n_genes                    int number of unique genes containing this domain
    n_instances                int number of unique instances containing this domain
    mappings_per_consensus_pos dictionary of mappings per metadomain consensus positions; {POS: [models.mapping.Mapping]}
    """
    domain_id = str() 
    consensus_length = int()
    n_genes = int()
    n_instances = int()
    mappings_per_consensus_pos = dict()

    def __init__(self, domain_id):
        if domain_id.startswith('PF'):
            self.domain_id = domain_id
        
            # retrieve all domain occurrences for the domain_id
            domain_of_interest_occurrences = InterproRepository.get_domains_for_ext_domain_id(self.domain_id)    
            if len(domain_of_interest_occurrences) == 0:
                raise NotEnoughOccurrencesForMetaDomain("There are not enough occurrences for the '"+str(self.domain_id)+"' to create a meta domain")
            
            self.mappings_per_consensus_pos = generate_pfam_alignment_mappings(self.domain_id, domain_of_interest_occurrences)
        else:
            raise UnsupportedMetaDomainIdentifier("Expected a Pfam domain, instead the identifier '"+str(domain_id)+"' was received")    