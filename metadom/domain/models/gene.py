from metadom.database import db
import enum
from metadom.domain.models.mapping import Mapping

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
    gencode_gene_id = db.Column(db.String(50))
    havana_gene_id = db.Column(db.String(50))
    havana_translation_id = db.Column(db.String(50))
    sequence_length = db.Column(db.Integer)
    
    # Relationships
    mappings = db.relationship('Mapping', back_populates="gene")
    
    def get_cDNA_sequence(self):
        _cDNA_sequence = ""
        mappings = {x.cDNA_position:x.allele for x in Mapping.query.filter_by(gene_id = self.id).all()}
        for key in sorted(mappings.keys()):
            _cDNA_sequence+= mappings[key]
        return _cDNA_sequence
    
    def get_aa_sequence(self):
        _aa_sequence = ""
        mappings = {x.amino_acid_position:x.amino_acid_residue for x in Mapping.query.filter_by(gene_id = self.id).all()}
        for key in sorted(mappings, key=lambda x: (x is None, x)):
            _aa_sequence+= mappings[key]
        return _aa_sequence
    
    def __init__(self, _strand, _gene_name, _gencode_transcription_id, 
                 _gencode_translation_name, _gencode_gene_id, _havana_gene_id, 
                 _havana_translation_id, _sequence_length):
        if _strand == '-':
            self.strand = Gene.Strand.minus
        elif _strand == '+':
            self.strand = Gene.Strand.plus
        else:
            raise Exception('no strand defined for gene')
        
        self.gene_name = _gene_name
        self.gencode_transcription_id = _gencode_transcription_id
        self.gencode_translation_name = _gencode_translation_name
        self.gencode_gene_id = _gencode_gene_id
        self.havana_gene_id = None if _havana_gene_id == '-' else _havana_gene_id
        self.havana_translation_id = None if _havana_translation_id == '-' else _havana_translation_id
        self.sequence_length = _sequence_length
    
    def __repr__(self):
        return "<Gene(strand='%s', gene_name='%s', gencode_transcription_id='%s', gencode_translation_name='%s', gencode_gene_id='%s', havana_gene_id='%s', havana_translation_id='%s')>" % (
                            self.strand, self.gene_name, self.gencode_transcription_id, self.gencode_translation_name, self.gencode_gene_id, self.havana_gene_id, self.havana_translation_id)
        