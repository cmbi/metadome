from metadom.database import db
import enum
from metadom.domain.models.mapping import Mapping
from metadom import _log

class Protein(db.Model):
    """
    Table: proteins
    
    Fields
    id                        identifier
    uniprot_ac                uniprot accession code
    uniprot_name              uniprot name
    source                    'swissprot' or 'uniprot'
    
    Relationships
    one to many               mappings
    one to many               interpro_domains
    """
    # Custom field declarations
    class ProteinSource(enum.Enum):
        uniprot = 'uniprot'
        swissprot = 'swissprot'
    
    # Table configuration
    __tablename__ = 'proteins'
    
    # Fields
    id = db.Column(db.Integer, primary_key=True)
    uniprot_ac = db.Column(db.String(12), unique=True, nullable=False)
    uniprot_name = db.Column(db.String(20))
    source = db.Column(db.Enum(ProteinSource), nullable=False)
    
    # Relationships
    mappings = db.relationship('Mapping', back_populates="protein")
    interpro_domains = db.relationship("Interpro", back_populates="protein")
    
    def get_aa_sequence(self, skip_asterix_at_end=False):
        _aa_sequence = ""
        mappings = {x.uniprot_position:x.uniprot_residue for x in Mapping.query.filter_by(protein_id = self.id).all()}
        for key in sorted(mappings, key=lambda x: (x is None, x)):
            if skip_asterix_at_end and key is None:
                continue
            _aa_sequence+= mappings[key]
        return _aa_sequence
    
    def get_aa_region(self, region_start, region_stop, skip_asterix_at_end=False):
        return self.get_aa_sequence(skip_asterix_at_end)[region_start-1:region_stop]
    
    def __init__(self, _uniprot_ac, _uniprot_name, _source):
        if _source == 'swissprot':
            self.source = Protein.ProteinSource.swissprot
        elif _source == 'uniprot':
            self.source = Protein.ProteinSource.uniprot
        else:
            raise Exception('no source database defined for protein')
        self.uniprot_ac = _uniprot_ac
        self.uniprot_name = _uniprot_name

    def __repr__(self):
        return "<Protein(uniprot_ac='%s', uniprot_name='%s', source='%s')>" % (
                            self.uniprot_ac, self.uniprot_name, self.source)