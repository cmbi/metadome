from collections import namedtuple
import gzip
import urllib

#Initialized GeneInfo named tuple. Note: namedtuple is immutable
gffInfoFields = ["seqid", "source", "type", "start", "end", "score", "strand", "phase", "attributes"]
GFFRecord = namedtuple("GFFRecord", gffInfoFields)

def parseGFFAttributes(attributeString):
    """Parse the GFF3 attribute column and return a dict
    
    __author__  = "Uli Koehler"
    __license__ = "Apache License v2.0"
    """#
    if attributeString == ".": return {}
    ret = {}
    for attribute in attributeString.split(";"):
        key, value = attribute.split("=")
        ret[urllib.request.unquote(key)] = urllib.request.unquote(value)
    return ret

def parseGFF3(filename, filter_on_values=None):
    """
    A minimalistic GFF3 format parser.
    Yields objects that contain info about a single GFF3 feature.
    
    Supports transparent gzip decompression.
    
    __author__  = "Uli Koehler"
    __license__ = "Apache License v2.0"
    """
    #Parse with transparent decompression
    openFunc = gzip.open if filename.endswith(".gz") else open
    with openFunc(filename) as infile:
        for line in infile:
            if line.startswith("#"): continue
            if not(filter_on_values is None):
                if type(filter_on_values) is list:
                    if any(s in line for s in filter_on_values): continue
                if type(filter_on_values) is str:
                    if not(filter_on_values in line): continue
            parts = line.strip().split("\t")
            #If this fails, the file format is not standard-compatible
            assert len(parts) == len(gffInfoFields)
            #Normalize data
            normalizedInfo = {
                "seqid": None if parts[0] == "." else urllib.request.unquote(parts[0]),
                "source": None if parts[1] == "." else urllib.request.unquote(parts[1]),
                "type": None if parts[2] == "." else urllib.request.unquote(parts[2]),
                "start": None if parts[3] == "." else int(parts[3]),
                "end": None if parts[4] == "." else int(parts[4]),
                "score": None if parts[5] == "." else float(parts[5]),
                "strand": None if parts[6] == "." else urllib.request.unquote(parts[6]),
                "phase": None if parts[7] == "." else urllib.request.unquote(parts[7]),
                "attributes": parseGFFAttributes(parts[8])
            }
            #Alternatively, you can emit the dictionary here, if you need mutability:
            #    yield normalizedInfo
            yield GFFRecord(**normalizedInfo)