from metadom.database import db

class Pfam(db.Model):
    """
    Table: pfam_domains
    
    Fields
    id                        identifier
    pfam_id                   Pfam identifier code 'PF#####'
    name                      Name of the Pfam domain
    interpro_id               Interpro identifier  
    uniprot_ac                uniprot accession code
    uniprot_start             0 <= uniprot_start < uniprot_stop
    uniprot_stop              uniprot_stop <= uniprot_end
    
    Relationships
    one to many               mappings
    many to one               protein
    """
    # Table configuration
    __tablename__ = 'pfam_domains'
    
    # Fields
    id = db.Column(db.Integer, primary_key=True)
    pfam_id = db.Column(db.String(12), nullable=False)
    name = db.Column(db.String)
    interpro_id = db.Column(db.String(12))
    uniprot_ac = db.Column(db.String(12), db.ForeignKey('proteins.uniprot_ac'), nullable=False)
    uniprot_start = db.Column(db.Integer, nullable=False)
    uniprot_stop = db.Column(db.Integer, nullable=False)
    
    # Relationships
    protein = db.relationship("Protein", back_populates="pfam_domains")
    mappings = db.relationship('Mapping', back_populates="pfam_domain")
    
    # Constraints
    __table_args__ = (db.UniqueConstraint('uniprot_ac', 'uniprot_start', 'uniprot_stop', name='_unique_protein_region'),
                     )
    
    def __repr__(self):
        return "<Pfam(pfam_id='%s', name='%s', interpro_id='%s', uniprot_ac='%s', uniprot_start='%s', uniprot_stop='%s')>" % (
                            self.pfam_id, self.name, self.interpro_id, self.uniprot_ac, self.uniprot_start, self.uniprot_stop)