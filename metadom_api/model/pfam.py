from metadom_api.controller import database
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint

class Pfam(database.Base):
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
    id = Column(Integer, primary_key=True)
    pfam_id = Column(String(12), nullable=False)
    name = Column(String)
    interpro_id = Column(String(12))
    uniprot_ac = Column(String(12), ForeignKey('proteins.uniprot_ac'), nullable=False)
    uniprot_start = Column(Integer, nullable=False)
    uniprot_stop = Column(Integer, nullable=False)
    
    # Relationships
    protein = relationship("Protein", back_populates="pfam_domains")
    mappings = relationship('Mapping', back_populates="pfam_domain")
    
    # Constraints
    __table_args__ = (UniqueConstraint('uniprot_ac', 'uniprot_start', 'uniprot_stop', name='_unique_protein_region'),
                     )
    
    def __repr__(self):
        return "<Pfam(pfam_id='%s', name='%s', interpro_id='%s', uniprot_ac='%s', uniprot_start='%s', uniprot_stop='%s')>" % (
                            self.pfam_id, self.name, self.interpro_id, self.uniprot_ac, self.uniprot_start, self.uniprot_stop)