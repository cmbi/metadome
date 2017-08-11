class MappingRepository:

    @staticmethod
    def get_mappings(entry_id, position):

        # This is a pfam query
        # mappings = session.query(Mapping).join(Pfam).filter(and_(
            # Mapping.pfam_consensus_position==position,
            # Pfam.pfam_id==entry_id))
        return {}
