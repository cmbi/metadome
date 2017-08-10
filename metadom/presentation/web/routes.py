import logging

from flask import Blueprint, render_template

_log = logging.getLogger(__name__)

bp = Blueprint('web', __name__, static_folder='static',
               template_folder='templates')


@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@bp.errorhandler(Exception)
def exception_error_handler(error):  # pragma: no cover
    import traceback
    _log.error("Unhandled exception:\n{}".format(traceback.format_exc(error)))
    return render_template('error.html', msg=error), 500
