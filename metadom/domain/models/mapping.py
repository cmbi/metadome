from metadom.database import db

class Mapping(db.Model):
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
    id = db.Column(db.Integer, primary_key=True)
    allele = db.Column(db.String(1))
    codon = db.Column(db.String(3))
    codon_allele_position = db.Column(db.Integer)
    amino_acid_residue = db.Column(db.String(1))
    cDNA_position = db.Column(db.Integer)
    uniprot_position = db.Column(db.Integer)
    pfam_consensus_position = db.Column(db.Integer)
    chromosome_id = db.Column(db.Integer, db.ForeignKey('chromosomes.id'), nullable=False)
    gene_id = db.Column(db.Integer, db.ForeignKey('genes.id'), nullable=False)
    protein_id = db.Column(db.Integer, db.ForeignKey('proteins.id'))
    pfam_domain_id = db.Column(db.Integer, db.ForeignKey('pfam_domains.id'))
    
    # Relationships
    chromosome = db.relationship('Chromosome', back_populates="mappings")
    gene = db.relationship("Gene", back_populates="mappings")
    protein = db.relationship("Protein", back_populates="mappings")
    pfam_domain = db.relationship("Pfam", back_populates="mappings")
    
    def __repr__(self):
        return "<Mapping(allele='%s', codon='%s', codon_allele_position='%s', amino_acid_residue='%s', cDNA_position='%s', uniprot_position='%s', pfam_consensus_position='%s')>" % (
                            self.allele, self.codon, self.codon_allele_position, self.amino_acid_residue, self.cDNA_position, self.uniprot_position, self.pfam_consensus_position)
    