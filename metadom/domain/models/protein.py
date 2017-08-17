from metadom.database import db
import enum

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
    one to many               pfam_domains
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
    pfam_domains = db.relationship("Pfam", back_populates="protein")

    def __repr__(self):
        return "<Protein(uniprot_ac='%s', uniprot_name='%s', source='%s')>" % (
                            self.uniprot_ac, self.uniprot_name, self.source)