from metadom.database import db

class Pfam(db.Model):
    """
    Table: pfam_domains
    Contains the representation of Pfam domain occurrences
    in uniprot sequences
    
    Fields
    id                        identifier
    pfam_id                   Pfam identifier code 'PF#####'
    name                      Name of the Pfam domain
    pfam_length               Length of the Pfam domain
    interpro_id               Interpro identifier
    uniprot_start             0 <= uniprot_start < uniprot_stop
    uniprot_stop              uniprot_stop <= uniprot_end
    protein_id                Foreign key
    
    Relationships
    many to one               protein
    """
    # Table configuration
    __tablename__ = 'pfam_domains'
    
    # Fields
    id = db.Column(db.Integer, primary_key=True)
    pfam_id = db.Column(db.String(12), nullable=False)
    name = db.Column(db.String)
    pfam_length = db.Column(db.Integer, nullable=False)
    interpro_id = db.Column(db.String(12))
    uniprot_start = db.Column(db.Integer, nullable=False)
    uniprot_stop = db.Column(db.Integer, nullable=False)
    protein_id = db.Column(db.Integer, db.ForeignKey('proteins.id'), nullable=False)
    
    # Relationships
    protein = db.relationship("Protein", back_populates="pfam_domains")
    pfam_domain_alignments = db.relationship("PfamDomainAlignment", back_populates="pfam_domain")
    
    # Constraints
    __table_args__ = (db.UniqueConstraint('protein_id', 'pfam_id', 'uniprot_start', 'uniprot_stop', name='_unique_protein_region'),
                     )
    
    def get_alignment(self):
        # TODO: create this method
        pass
    
    def __repr__(self):
        return "<Pfam(pfam_id='%s', name='%s', pfam_length='%s', interpro_id='%s', uniprot_start='%s', uniprot_stop='%s')>" % (
                            self.pfam_id, self.name, self.pfam_length, self.interpro_id, self.uniprot_start, self.uniprot_stop)