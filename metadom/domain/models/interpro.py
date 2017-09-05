from metadom.database import db

class Interpro(db.Model):
    """
    Table: interpro_domains
    Contains the representation of Interpro domain occurrences
    in uniprot sequences
    
    Fields
    id                        identifier
    ext_db_id                 External domain database identifier code
    name                      Name of the Interpro domain
    pfam_length               Length of the Interpro domain
    interpro_id               Interpro identifier
    uniprot_start             0 <= uniprot_start < uniprot_stop
    uniprot_stop              uniprot_stop <= uniprot_end
    protein_id                Foreign key
    
    Relationships
    many to one               protein
    one to many               pfam_domain_alignments
    """
    # Table configuration
    __tablename__ = 'interpro_domains'
    
    # Fields
    id = db.Column(db.Integer, primary_key=True)
    ext_db_id = db.Column(db.String(12), nullable=False)
    name = db.Column(db.String)
    pfam_length = db.Column(db.Integer, nullable=False)
    interpro_id = db.Column(db.String(12))
    uniprot_start = db.Column(db.Integer, nullable=False)
    uniprot_stop = db.Column(db.Integer, nullable=False)
    protein_id = db.Column(db.Integer, db.ForeignKey('proteins.id'), nullable=False)
    
    # Relationships
    protein = db.relationship("Protein", back_populates="interpro_domains")
    pfam_domain_alignments = db.relationship("PfamDomainAlignment", back_populates="pfam_domain")
    
    # Constraints
    __table_args__ = (db.UniqueConstraint('protein_id', 'ext_db_id', 'uniprot_start', 'uniprot_stop', name='_unique_protein_region'),
                     )
    
    def get_alignment(self):
        # TODO: create this method
        pass
    
    def __repr__(self):
        return "<Interpro(pfam_id='%s', name='%s', pfam_length='%s', interpro_id='%s', uniprot_start='%s', uniprot_stop='%s')>" % (
                            self.pfam_id, self.name, self.pfam_length, self.interpro_id, self.uniprot_start, self.uniprot_stop)