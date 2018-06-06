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

@bp.route('/dashboard', methods=['GET'])
def dashboard():
    gene_names = GeneRepository.retrieve_all_gene_names_from_file()
    return render_template('dashboard.html', data=map(json.dumps, gene_names))

@bp.route('/dashboard_js')
def dashboard_js():
    # Renders the javascript used on the index page
    return render_template('/js/dashboard.js')

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

@bp.before_request
def before_request():
    g.metadom_version = get_version()

@bp.errorhandler(Exception)
def exception_error_handler(error):  # pragma: no cover
    _log.error("Unhandled exception:\n{}".format(error))
    _log.error(traceback.print_exc())
    return render_template('error.html', msg=error, stack_trace=traceback.print_exc()), 500