import logging

from flask import abort, Blueprint, jsonify, render_template
from metadom.domain.models.interpro import Interpro
from metadom.domain.models.chromosome import Chromosome
from metadom.domain.models.mapping import Mapping

from sqlalchemy import and_

_log = logging.getLogger(__name__)

bp = Blueprint('api', __name__, url_prefix='/api', static_folder='static',
               template_folder='templates')

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
    import traceback
    _log.error("Unhandled exception:\n{}".format(traceback.format_exc(error)))
    return render_template('', msg=error), 500
