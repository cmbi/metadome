from flask import Blueprint, redirect, g, render_template, url_for, request, session
from flask_mail import Message
import json
import traceback
from metadom import get_version
from metadom.domain.repositories import GeneRepository
from metadom.domain.services.mail.mail import mail
from metadom.presentation.web.forms import SupportForm
from metadom.presentation import api
from metadom.default_settings import DEFAULT_RECIPIENT

import logging

_log = logging.getLogger(__name__)

bp = Blueprint('web', __name__)

@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@bp.route('/metadom', methods=['GET'])
def metadom():
    return render_template('metadom.html')

@bp.route('/metadom/<string:transcript_id>/<string:domain_id>', methods=['GET'])
def metadom_with_data(transcript_id, domain_id):
    _result = api.routes.get_metadomains_for_transcript(transcript_id, domain_id, _jsonify=False)
    return render_template('metadom.html', data=_result)

@bp.route('/metadom_js')
def metadom_js():
    # Renders the javascript used on the index page
    return render_template('/js/metadom.js')

@bp.route('/tolerance', methods=['GET'])
def tolerance():
    gene_names = GeneRepository.retrieve_all_gene_names_from_file()
    return render_template('tolerance.html', data=map(json.dumps, gene_names))

@bp.route('/tolerance_js')
def tolerance_js():
    # Renders the javascript used on the index page
    return render_template('/js/tolerance.js')

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = SupportForm()
    if form.validate_on_submit():
        email = form.email.data
        body = form.body.data
        
        msg = Message(subject="Support Request",
                  sender=email,
                  recipients=[DEFAULT_RECIPIENT])
        
        msg.body = body
        
        mail.send(msg)

        return render_template('contact_sent.html')

    return render_template('contact.html', form=form)

@bp.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@bp.route('/method', methods=['GET'])
def method():
    return render_template('method.html')


# @bp.route("/input", methods=['GET', 'POST'])
# def input():
#     form = MetaDomForm()
#     if form.validate_on_submit():
#         # get result
#         mappings = MappingRepository.get_mapping_position(form.entry_id.data, 
#                                                   form.position.data)
#         
#         alignments = PfamDomainAlignmentRepository.get_msa_alignment(form.entry_id.data)
# 
#         _log.debug("Redirecting to result page")
# 
#         session['mappings'] = mappings
#         session['alignments'] = alignments
#         return redirect(url_for('web.result'))
# 
#     _log.debug("Rendering input page")
#     return render_template("input.html", form=form)


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
    _log.error(traceback.print_exc())
    return render_template('error.html', msg=error, stack_trace=traceback.print_exc()), 500