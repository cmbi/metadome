from metadom.controller import database
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
import enum

class Protein(database.Base):
    """
    Table: proteins
    
    Fields
    id                        identifier
    uniprot_ac                uniprot accession code
    uniprot_name              uniprot name
    source                    'swissprot' or 'uniprot'
    
    Relationships
    one to many               mappings
    one to many               pfam_domains
    """
    # Custom field declarations
    class ProteinSource(enum.Enum):
        uniprot = 'uniprot'
        swissprot = 'swissprot'
    
    # Table configuration
    __tablename__ = 'proteins'
    
    # Fields
    id = Column(Integer, primary_key=True)
    uniprot_ac = Column(String(12), unique=True, nullable=False)
    uniprot_name = Column(String(20))
    source = Column(Enum(ProteinSource), nullable=False)
    
    # Relationships
    mappings = relationship('Mapping', back_populates="protein")
    pfam_domains = relationship("Pfam", back_populates="protein")

    def __repr__(self):
        return "<Protein(uniprot_ac='%s', uniprot_name='%s', source='%s')>" % (
                            self.uniprot_ac, self.uniprot_name, self.source)