from metadom.infrastructure import database
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class Chromosome(database.Base):
    """
    Table: chromosomes
    
    Fields
    id                        identifier
    chromosome                chromosome '1'-'22', 'X' or 'Y'
    position                  position in the chromosome
    
    Relationships
    one to many               mappings
    """
    
    # Table configuration
    __tablename__ = 'chromosomes'
    
    # Fields
    id = Column(Integer, primary_key=True)
    chromosome = Column(String(2), nullable=False)
    position = Column(Integer, nullable=False)
    
    # Relationships
    mappings = relationship('Mapping', back_populates="chromosome")
    
    def __repr__(self):
        return "<Chromosome(chromosome='%s', position='%s')>" % (
                            self.chromosome, self.position)