from metadom.database import db

class PfamDomainAlignment(db.Model):
    """
    Table: pfam_domain_alignment
    Contains a aligned positions of uniprot residues to 
    Pfam domain occurrences in uniprot sequences
    
    Fields
    id                        identifier
    domain_consensus_position The consensus position of the pfam domain
    domain_consensus_residue  The consensus residue of the pfam domain
    mapping_id                Foreign key
    protein_id                Foreign key
    
    Relationships
    many to one               mappings
    many to one               protein
    """
    # Table configuration
    __tablename__ = 'pfam_domain_alignments'
    
    # Fields
    id = db.Column(db.Integer, primary_key=True)
    domain_consensus_position = db.Column(db.Integer)
    domain_consensus_residue = db.Column(db.String(1))
    mapping_id = db.Column(db.Integer, db.ForeignKey('mappings.id'), nullable=False)
    domain_id = db.Column(db.Integer, db.ForeignKey('interpro_domains.id'), nullable=False)
    
    # Relationships
    mappings = db.relationship('Mapping', back_populates="pfam_domain_alignment")
    domain = db.relationship('Interpro', back_populates="pfam_domain_alignments")
    
    # Constraints
    __table_args__ = (db.UniqueConstraint('domain_id', 'mapping_id', name='_unique_protein_domain_position'),
                     )
    
    def __repr__(self):
        return "<PfamDomainAlignment(domain_id='%s', mapping_id='%s')>" % (
                            self.domain_id, self.mapping_id)