import enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Enum

Base = declarative_base()


class Chromosome(Base):
    """
    CREATE TABLE `chromosomes` (
      `id` INTEGER NOT NULL AUTO_INCREMENT DEFAULT NULL,
      `chromosome` CHAR(2) NULL DEFAULT NULL,
      `position` INTEGER NULL DEFAULT NULL,
      PRIMARY KEY (`id`)
    );"""
    
    __tablename__ = 'chromosomes'
    
    id = Column(Integer, primary_key=True)
    chromosome = Column(String(2))                      # chromosome '1'-'22', 'X' or 'Y'
    position = Column(Integer)                          # position in the chromosome
    
    def __repr__(self):
        return "<Chromosome(chromosome='%s', position='%s')>" % (
                            self.chromosome, self.position)
    

class Mapping(Base):
    """
    CREATE TABLE `mapping` (
      `id` INTEGER NOT NULL AUTO_INCREMENT DEFAULT NULL,
      `allele` CHAR(1) NULL DEFAULT NULL,
      `codon` CHAR(3) NULL DEFAULT NULL,
      `codon_allele_position` INTEGER NULL DEFAULT NULL,
      `amino_acid_residue` CHAR(1) NULL DEFAULT 'X',
      `cDNA_position` INTEGER NULL DEFAULT NULL,
      `uniprot_position` INTEGER NULL DEFAULT NULL,
      `pfam_consensus_position` INTEGER NULL DEFAULT NULL,
      PRIMARY KEY (`id`)
    );"""
    
    __tablename__ = 'mapping'
    
    id = Column(Integer, primary_key=True)
    allele = Column(String(1))                          # 'A', 'T', 'C', 'G'
    codon = Column(String(3))                           # all triplet combinations of the alleles 
    codon_allele_position = Column(Integer)             # 0, 1, 2, or None
    amino_acid_residue = Column(String(1))              # one of the 20 amino acids, * or None
    cDNA_position = Column(Integer)                     # the position in the cDNA
    uniprot_position = Column(Integer)                  # the position in the protein
    pfam_consensus_position = Column(Integer)           # position in the aligned Pfam domain or None
    
    def __repr__(self):
        return "<Mapping(allele='%s', codon='%s', codon_allele_position='%s', amino_acid_residue='%s', cDNA_position='%s', uniprot_position='%s', pfam_consensus_position='%s')>" % (
                            self.allele, self.codon, self.codon_allele_position, self.amino_acid_residue, self.cDNA_position, self.uniprot_position, self.pfam_consensus_position)
    
    
class Pfam(Base):
    """
    CREATE TABLE `pfam` (
      `id` INTEGER NULL AUTO_INCREMENT DEFAULT NULL,
      `pfam_id` VARCHAR(10) NOT NULL DEFAULT 'NULL',
      `name` VARCHAR(255) NULL DEFAULT NULL,
      `interpro_id` VARCHAR(12) NULL DEFAULT NULL,
      `uniprot_ac` VARCHAR(12) NULL DEFAULT NULL,
      `uniprot_start` INTEGER NOT NULL DEFAULT 0,
      `uniprot_stop` INTEGER NOT NULL DEFAULT 0,
      PRIMARY KEY (`id`)
    );
    """
    
    __tablename__ = 'pfam'
    
    id = Column(Integer, primary_key=True)
    pfam_id = Column(String(12))                        # Pfam identifier code 'PF#####'
    name = Column(String)                               # Name of the Pfam domain
    interpro_id = Column(String(12))                    # Interpro identifier  
    uniprot_ac = Column(String(12))                     # uniprot accession code
    uniprot_start = Column(Integer)                     # 0 <= uniprot_start < uniprot_stop
    uniprot_stop = Column(Integer)                      # uniprot_stop <= uniprot_end
    
    
    def __repr__(self):
        return "<Pfam(pfam_id='%s', name='%s', interpro_id='%s', uniprot_ac='%s', uniprot_start='%s', uniprot_stop='%s')>" % (
                            self.pfam_id, self.name, self.interpro_id, self.uniprot_ac, self.uniprot_start, self.uniprot_stop)

class Protein(Base):
    """
    CREATE TABLE `protein` (
      `id` INTEGER NULL AUTO_INCREMENT DEFAULT NULL,
      `uniprot_ac` VARCHAR(12) NOT NULL DEFAULT 'NULL',
      `uniprot_name` VARCHAR(20) NULL DEFAULT NULL,
      `source` ENUM ('swissprot','uniprot'),
      PRIMARY KEY (`id`),
      UNIQUE KEY (`uniprot_ac`),
    KEY (`uniprot_ac`)
    );"""
    
    class ProteinSource(enum.Enum):
        uniprot = 'uniprot'
        swissprot = 'swissprot'
    
    
    __tablename__ = 'protein'
    
    id = Column(Integer, primary_key=True)
    uniprot_ac = Column(String(12), unique=True)
    uniprot_name = Column(String(20))
    source = Column(Enum(ProteinSource))

    def __repr__(self):
        return "<Protein(uniprot_ac='%s', uniprot_name='%s', source='%s')>" % (
                            self.uniprot_ac, self.uniprot_name, self.source)

class Gene(Base):
    """
    CREATE TABLE `gene` (
      `id` INTEGER NULL AUTO_INCREMENT DEFAULT NULL,
      `strand` ENUM ('+', '-'),
      `gene_name` VARCHAR(50) NOT NULL DEFAULT '',
      `gencode_transcription_id` VARCHAR(50) NOT NULL DEFAULT '',
      `gencode_translation_name` VARCHAR(50) NOT NULL DEFAULT '',
      `gencode_gene_id` VARCHAR(50) NOT NULL DEFAULT '',
      `havana_gene_id` VARCHAR(50) NOT NULL DEFAULT '',
      `havana_translation_id` VARCHAR(50) NOT NULL DEFAULT '',
      PRIMARY KEY (`id`),
      UNIQUE KEY (`gencode_transcription_id`, `gencode_translation_name`, `havana_translation_id`)
    );"""
    
    class Strand(enum.Enum):
        plus = '+'
        minus = '-'
        
    __tablename__ = 'gene'
    
    id = Column(Integer, primary_key=True)
    strand = Column(Enum(Strand))
    gene_name = Column(String(50))
    gencode_transcription_id = Column(String(50))
    gencode_translation_name = Column(String(50))
    gencode_gene_id = Column(String(50))
    havana_gene_id = Column(String(50))
    havana_translation_id = Column(String(50))
    
    def __repr__(self):
        return "<Gene(strand='%s', gene_name='%s', gencode_transcription_id='%s', gencode_translation_name='%s', gencode_gene_id='%s', havana_gene_id='%s', havana_translation_id='%s')>" % (
                            self.strand, self.gene_name, self.gencode_transcription_id, self.gencode_translation_name, self.gencode_gene_id, self.havana_gene_id, self.havana_translation_id)