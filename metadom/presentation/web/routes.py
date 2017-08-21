import logging

from flask import Blueprint, redirect, g, render_template, url_for, request, session

from metadom import get_version
from metadom.presentation.web.forms import MetaDomForm
from metadom.domain.repositories import MappingRepository

_log = logging.getLogger(__name__)

bp = Blueprint('web', __name__)

@bp.route('/', methods=['GET'])
def index():
    _log.info("Rendering index page")
    return render_template('index.html')


@bp.route("/input", methods=['GET', 'POST'])
def input():
    form = MetaDomForm()
    if form.validate_on_submit():
        # get result
        mappings = MappingRepository.get_mappings(form.entry_id.data, 
                                                  form.position.data)

        _log.debug("Redirecting to result page")

        session['mappings'] = mappings
        return redirect(url_for('web.result'))

    _log.debug("Rendering input page")
    return render_template("input.html", form=form)


@bp.route("/result", methods=["GET"])
def result():
    mappings = session.get('mappings', None)
    return render_template("result.html", mappings=mappings)


@bp.before_request
def before_request():
    g.metadom_version = get_version()

@bp.errorhandler(Exception)
def exception_error_handler(error):  # pragma: no cover
    _log.error("Unhandled exception:\n{}".format(error))
    return render_template('error.html', msg=error), 500