import logging

from metadom.database import db
from metadom.domain.models.mapping import Mapping
from metadom.domain.models.chromosome import Chromosome
from metadom.domain.models.gene import Gene
from metadom.domain.models.protein import Protein
from metadom.domain.models.pfam import Pfam

# from sqlalchemy import and_
from metadom.domain.services import test_connection, list_tables

_log = logging.getLogger(__name__)

class MappingRepository:

    @staticmethod
    def get_mappings(entry_id, position):
        # TODO: remove when testing is done
        _log.info("connection: "+str(test_connection()))
        _log.info(list_tables())
        _log.info("got entry:" +str(entry_id)+" and position: "+str(position))
         
        # Default mapping
        mapping = {}
         
        # TODO: create handling of specific type of queries
        # TODO: make use of services
        
        # This is a pfam with position query
        for x in db.session.query(Mapping).join(Pfam).filter(db.and_(
            Mapping.pfam_consensus_position==position,
            Pfam.pfam_id==entry_id)):
            for y in db.session.query(Chromosome).filter(Chromosome.id ==
                                                       x.chromosome_id):
                chr_key = str(y.chromosome)+":"+str(y.position)
                if chr_key in mapping:
                    _log.error('Dublicate chromosome entry')
                else:
                    mapping[chr_key] = str(x)
          
        _log.info('got mapping: '+str(mapping))
        return mapping
