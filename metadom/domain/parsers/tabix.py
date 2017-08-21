'''
Parser for vcf files and used for running tabix queries to such files
'''
import logging
import vcf
from enum import Enum

_log = logging.getLogger(__name__)

class NoInputFileCoordinateSystemSelectedException(Exception):
    pass

class variant_coordinate_system(Enum):
    """For differences, see: https://www.biostars.org/p/84686/"""
    zero_based = 1
    one_based = 2

def tabix_query(filename, chrom, start, end, inputfile_variant_coordinate_system, encoding='ascii'):
    """Call tabix and generate an array of strings for each line it returns."""    
    vcf_reader = vcf.Reader(filename=filename, encoding=encoding)
    try:
        if inputfile_variant_coordinate_system == variant_coordinate_system.one_based:
            for record in vcf_reader.fetch(chrom, start-1, end):
                yield record
        elif inputfile_variant_coordinate_system == variant_coordinate_system.zero_based:
            for record in vcf_reader.fetch(chrom, start, end):
                yield record
        else:
            raise NoInputFileCoordinateSystemSelectedException("No valid input file variant coordinate system was selected to adjust for when querying variant file")
    except (ValueError, NoInputFileCoordinateSystemSelectedException) as e:
        if e is NoInputFileCoordinateSystemSelectedException:
            raise e
        else:
            _log.error("Error while parsing record from '"+filename+"' in region 'chr"+str(chrom)+":"+str(start)+"-"+str(end)+"' :"+str(e))