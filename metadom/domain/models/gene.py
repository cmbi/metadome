from metadom.application import db
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
import enum

class Gene(db.Model):
    """
    Table: genes
    
    Fields
    id                        identifier
    strand                    '+' or '-'
    gene_name                 Conventional (HAVANA) name of the gene
    gencode_transcription_id  e.g. ENST####...
    gencode_translation_name  e.g. BRCA1-###
    gencode_gene_id           e.g. ENSG####...
    havana_gene_id            e.g. OTTHUMG#####....
    havana_translation_id     e.g. OTTHUMT#####....
    
    Relationships
    one to many               mappings
    """
    # Custom field declarations
    class Strand(enum.Enum):
        plus = '+'
        minus = '-'
    
    # Table configuration
    __tablename__ = 'genes'
    
    # Fields
    id = Column(Integer, primary_key=True)
    strand = Column(Enum(Strand), nullable=False)
    gene_name = Column(String(50))
    gencode_transcription_id = Column(String(50), unique=True, nullable=False)
    gencode_translation_name = Column(String(50), unique=True, nullable=False)
    gencode_gene_id = Column(String(50), unique=True, nullable=False)
    havana_gene_id = Column(String(50), unique=True)
    havana_translation_id = Column(String(50), unique=True)
    
    # Relationships
    mappings = relationship('Mapping', back_populates="gene")
    
    
    def __repr__(self):
        return "<Gene(strand='%s', gene_name='%s', gencode_transcription_id='%s', gencode_translation_name='%s', gencode_gene_id='%s', havana_gene_id='%s', havana_translation_id='%s')>" % (
                            self.strand, self.gene_name, self.gencode_transcription_id, self.gencode_translation_name, self.gencode_gene_id, self.havana_gene_id, self.havana_translation_id)
        