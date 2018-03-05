import logging

from flask import Blueprint, redirect, g, render_template, url_for, request, session

from metadom import get_version
from metadom.presentation.web.forms import MetaDomForm
from metadom.domain.repositories import MappingRepository,\
    PfamDomainAlignmentRepository

_log = logging.getLogger(__name__)

bp = Blueprint('web', __name__)

@bp.route('/', methods=['GET'])
def index():
    _log.info("Rendering index page")
    return render_template('index.html')

@bp.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')

@bp.route('/help', methods=['GET'])
def help():
    return render_template('help.html')

@bp.route('/about', methods=['GET'])
def about():
    return render_template('contact.html')


@bp.route("/input", methods=['GET', 'POST'])
def input():
    form = MetaDomForm()
    if form.validate_on_submit():
        # get result
        mappings = MappingRepository.get_mapping_position(form.entry_id.data, 
                                                  form.position.data)
        
        alignments = PfamDomainAlignmentRepository.get_msa_alignment(form.entry_id.data)

        _log.debug("Redirecting to result page")

        session['mappings'] = mappings
        session['alignments'] = alignments
        return redirect(url_for('web.result'))

    _log.debug("Rendering input page")
    return render_template("input.html", form=form)


@bp.route("/result", methods=["GET"])
def result():
    mappings = session.get('mappings', None)
    alignments = session.get('alignments', None)
    return render_template("result.html", mappings=mappings, alignments=alignments)


@bp.before_request
def before_request():
    g.metadom_version = get_version()

@bp.errorhandler(Exception)
def exception_error_handler(error):  # pragma: no cover
    _log.error("Unhandled exception:\n{}".format(error))
    return render_template('error.html', msg=error), 500