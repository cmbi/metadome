from metadom.database import db
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
    id = db.Column(db.Integer, primary_key=True)
    strand = db.Column(db.Enum(Strand), nullable=False)
    gene_name = db.Column(db.String(50))
    gencode_transcription_id = db.Column(db.String(50), unique=True, nullable=False)
    gencode_translation_name = db.Column(db.String(50), unique=True, nullable=False)
    gencode_gene_id = db.Column(db.String(50), unique=True, nullable=False)
    havana_gene_id = db.Column(db.String(50), unique=True)
    havana_translation_id = db.Column(db.String(50), unique=True)
    
    # Relationships
    mappings = db.relationship('Mapping', back_populates="gene")
    
    
    def __repr__(self):
        return "<Gene(strand='%s', gene_name='%s', gencode_transcription_id='%s', gencode_translation_name='%s', gencode_gene_id='%s', havana_gene_id='%s', havana_translation_id='%s')>" % (
                            self.strand, self.gene_name, self.gencode_transcription_id, self.gencode_translation_name, self.gencode_gene_id, self.havana_gene_id, self.havana_translation_id)
        