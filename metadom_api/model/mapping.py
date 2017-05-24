from metadom_api.controller import database
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Mapping(database.Base):
    """
    Table: mapping
    
    Fields
    id                        identifier
    allele                    'A', 'T', 'C', 'G'
    codon                     all triplet combinations of the alleles 
    codon_allele_position     0, 1, 2, or None
    amino_acid_residue        one of the 20 amino acids, * or None
    cDNA_position             the position in the cDNA
    uniprot_position          the position in the protein
    pfam_consensus_position   position in the aligned Pfam domain or None
    chromosome_id             Foreign key
    gene_id                   Foreign key
    protein_id                Foreign key
    pfam_domain_id            Foreign key
    
    Relationships
    many to one               chromosome
    many to one               gene
    many to one               protein
    many to one               pfam_domain
    """
    # Table configuration
    __tablename__ = 'mapping'
    
    # Fields
    id = Column(Integer, primary_key=True)
    allele = Column(String(1))
    codon = Column(String(3))
    codon_allele_position = Column(Integer)
    amino_acid_residue = Column(String(1))
    cDNA_position = Column(Integer)
    uniprot_position = Column(Integer)
    pfam_consensus_position = Column(Integer)
    chromosome_id = Column(Integer, ForeignKey('chromosomes.id'), nullable=False)
    gene_id = Column(Integer, ForeignKey('genes.id'), nullable=False)
    protein_id = Column(Integer, ForeignKey('proteins.id'))
    pfam_domain_id = Column(Integer, ForeignKey('pfam_domains.id'))
    
    # Relationships
    chromosome = relationship('Chromosome', back_populates="mappings")
    gene = relationship("Gene", back_populates="mappings")
    protein = relationship("Protein", back_populates="mappings")
    pfam_domain = relationship("Pfam", back_populates="mappings")
    
    def __repr__(self):
        return "<Mapping(allele='%s', codon='%s', codon_allele_position='%s', amino_acid_residue='%s', cDNA_position='%s', uniprot_position='%s', pfam_consensus_position='%s')>" % (
                            self.allele, self.codon, self.codon_allele_position, self.amino_acid_residue, self.cDNA_position, self.uniprot_position, self.pfam_consensus_position)
    