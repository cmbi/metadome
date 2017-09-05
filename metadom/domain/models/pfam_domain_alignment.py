from metadom.database import db

class PfamDomainAlignment(db.Model):
    """
    Table: pfam_domain_alignment
    Contains single alignment positions of uniprot residues to 
    Pfam domain occurrences in uniprot sequences
    
    Fields
    id                        identifier
    uniprot_position          position of aligned uniprot position
    pfam_position             The consensus position of the pfam domain
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
    uniprot_position = db.Column(db.Integer, nullable=False)
    pfam_position = db.Column(db.Integer)
    mapping_id = db.Column(db.Integer, db.ForeignKey('mappings.id'), nullable=True)
    pfam_id = db.Column(db.Integer, db.ForeignKey('interpro_domains.id'), nullable=False)
    
    # Relationships
    mappings = db.relationship('Mapping', back_populates="pfam_domain_alignment")
    pfam_domain = db.relationship('Interpro', back_populates="pfam_domain_alignments")
    
    # Constraints
    __table_args__ = (db.UniqueConstraint('pfam_id', 'uniprot_position', name='_unique_protein_domain_position'),
                     )
     
    def __repr__(self):
        return "<PfamDomainAlignment(pfam_id='%s', mapping_id='%s', uniprot_position='%s', pfam_position='%s')>" % (
                            self.pfam_id, self.mapping_id, self.uniprot_position, self.pfam_position)