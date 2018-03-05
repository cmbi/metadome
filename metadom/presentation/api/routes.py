import logging

from flask import abort, Blueprint, jsonify, render_template
from metadom.domain.repositories import GeneRepository
from builtins import Exception
from metadom.domain.models.entities.gene_region import GeneRegion
from flask.globals import request
import traceback

_log = logging.getLogger(__name__)

bp = Blueprint('api', __name__)

@bp.route('/', methods=['GET'])
def api_doc():
    return render_template('api/docs.html')

@bp.route('/gene/geneToTranscript', methods=['GET'])
def get_default_transcript_ids():
    """This endpoint is a stub, to ensure deeper endpoints may be used"""
    pass

@bp.route('/gene/geneToTranscript/<string:gene_name>', methods=['GET'])
def get_transcript_ids_for_gene(gene_name):
    trancript_ids = GeneRepository.retrieve_all_transcript_ids(gene_name)
            
    return jsonify(trancript_ids)

@bp.route('/gene/geneTolerance', methods=['GET'])
def get_default_tolerance():
    """This endpoint is a stub, to ensure deeper endpoints may be used"""
    pass

@bp.route('/gene/geneTolerance/<transcript_id>/', methods=['GET'])
def get_gene_tolerance_no_end(transcript_id):
    if 'slidingWindow' in request.args:
        sliding_window = float(request.args['slidingWindow'])
    
    if 'frequency' in request.args:
        frequency = float(request.args['frequency'])
    
    if 'startpos' in request.args:
        start_pos = int(request.args['startpos'])
    else:
        start_pos = None
        
    if 'endpos' in request.args:
        end_pos = int(request.args['endpos'])
    else:
        end_pos = None
    
    # Retrieve the gene from the database
    gene = GeneRepository.retrieve_gene(transcript_id)
    
    if not gene is None:
        # build the gene region
        gene_region = GeneRegion(gene, start_pos, end_pos)
        
        return jsonify(str(gene_region))
        
        #TODO: further implement annotateSNVs
        #TODO: incorporate ExAC and gnoMAD
        # annotate HGMD
        
#         service.handleExacVariants();
# ===
#     /**
#      * Adds exac variants to the gene object by calling on the repository class to read tabix vcf files
#      * @throws IOException
#      */
#     public void handleExacVariants() throws IOException{
#         if (tabixFileReader==null) {
#             tabixFileReader = new TabixFileReader();
#         }
#         //TODO: check exac vs database
#         try {
#             int start = gene.getPositionList().get(0).getMappingsList().get(0).getChromosome().getPosition();
#             int stop = gene.getPositionList().get(gene.getPositionList().size()-1).getMappingsList().get(2).getChromosome().getPosition();
#             String chr = gene.getPositionList().get(0).getMappingsList().get(0).getChromosome().getChromosome().substring(3);
#             Map<Integer, TabixParser> tabixMap;
#             if (gene.getStrand().equals("minus")) {
#                 tabixMap = tabixFileReader.readTabixFile(chr, stop, start, exacTabixFile);
#             } else {
#                 tabixMap = tabixFileReader.readTabixFile(chr, start, stop, exacTabixFile);
#             }
#             gene = tabixFileReader.addExacVariants(gene, tabixMap);
#             
#         } catch(IOException e) {
#             LOG.error("Error with exac file" + e.getMessage());
#         }
#     }
# ===
#         if (endPosInt==0 ||endPosInt<startPosInt||endPosInt>service.getGene().getPositionList().size()){
#             endPosInt=service.getGene().getPositionList().size();
#         }
#         if (startPosInt>=endPosInt || startPosInt>= service.getGene().getPositionList().size()) {
#             startPosInt=0;
#         }
#         toleranceArray = service.calculateTolerance(service.getGene(), startPosInt, endPosInt, slidingWindowInt, frequencyDouble);
        
    else:
        abort(501)

    return jsonify(str())


# GET /api/chromosome/:id
@bp.route('/chromosome/<string:chromosome_id>', methods=['GET'])
def get_mapping_via_chr_pos(chromosome_id):
    pass
#     if len(locus) == 0:
#         abort(404)
#     return jsonify({'locus': locus[0]})

# GET /api/mapping/:id
@bp.route('/mapping/<string:mapping_id>', methods=['GET'])
def get_mapping_via_id(mapping_id):
    pass

# GET /api/gene/:id
@bp.route('/gene/<string:gene_id>', methods=['GET'])
def get_mapping_via_gene_id(gene_id):
    pass


# GET /api/protein/:id
@bp.route('/protein/<string:protein_id>', methods=['GET'])
def get_mapping_via_protein_id(protein_id):
    pass

# GET /api/pfam/:id
@bp.route('/pfam/<string:pfam_id>', methods=['GET'])
def get_mapping_via_pfam_id(pfam_id):
#     for x in session.query(Mapping).join(Interpro).filter(Interpro.pfam_id == pfam_id):
#         for y in session.query(Chromosome).filter(Chromosome.id == x.chromosome_id):
#             print(y,x)
    pass

# GET /api/pfam/:id/:position
@bp.route('/pfam/<string:pfam_id>/<int:position>', methods=['GET'])
def get_mapping_via_pfam_position(pfam_id, position):
#     for x in session.query(Mapping).join(Interpro).filter(and_(Mapping.pfam_consensus_position==position, Interpro.pfam_id == pfam_id)):
#         for y in session.query(Chromosome).filter(Chromosome.id == x.chromosome_id):
#             print(y,x)
    pass

@bp.errorhandler(Exception)
def exception_error_handler(error):  # pragma: no cover
    _log.error("Unhandled exception:\n{}".format(error))
    _log.error(traceback.print_exc())
    return render_template('error.html', msg=error), 500