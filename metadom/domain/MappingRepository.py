import logging

from metadom.infrastructure.database import Session
from metadom.domain.models.mapping import Mapping
from metadom.domain.models.chromosome import Chromosome
from metadom.domain.models.gene import Gene
from metadom.domain.models.protein import Protein
from metadom.domain.models.pfam import Pfam

from sqlalchemy import and_

_log = logging.getLogger(__name__)

class MappingRepository:

    @staticmethod
    def get_mappings(entry_id, position):
        
        session = Session()
        
        # TODO: remove when testing is done
        _log.info("got entry:" +str(entry_id)+" and position: "+str(position))
        
        # Default mapping
        mapping = {}
        
        # TODO: create handling of specific type of queries
        
        # This is a pfam with position query
        for x in session.query(Mapping).join(Pfam).filter(and_(
            Mapping.pfam_consensus_position==position,
            Pfam.pfam_id==entry_id)):
            for y in session.query(Chromosome).filter(Chromosome.id ==
                                                       x.chromosome_id):
                if 'chromosome_positions' in mapping:
                    mapping['chromosome_positions'].append((y,x))
                else:
                    mapping['chromosome_positions'] = [(y,x)]
         
            
        return mapping
