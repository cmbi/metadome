from metadom.database import db

class Chromosome(db.Model):
    """
    Table: chromosomes
    Representation of a single chromosomal position
    
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
    id = db.Column(db.Integer, primary_key=True)
    chromosome = db.Column(db.String(5), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    
    # Relationships
    mappings = db.relationship('Mapping', back_populates="chromosome")
    
    def __repr__(self):
        return "<Chromosome(chromosome='%s', position='%s')>" % (
                            self.chromosome, self.position)