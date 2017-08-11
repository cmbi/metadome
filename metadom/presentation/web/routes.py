import logging

from flask import Blueprint, render_template, current_app as app, url_for, request


from metadom import get_version
from metadom.presentation.web.forms import MetaDomForm
# from metadom.services.xssp import process_request

_log = logging.getLogger(__name__)

bp = Blueprint('web', __name__, static_folder='static',
               template_folder='templates')


@bp.route('/', methods=['GET'])
def index():
#     form = MetaDomForm()
#     if form.validate_on_submit():
#         celery_id = process_request(form.input_type.data, form.output_type.data,
#                                     form.pdb_id.data, request.files,
#                                     form.sequence.data)

#         _log.info("Redirecting to output page")
#         return redirect(url_for('dashboard.output',
#                                 input_type=form.input_type.data,
#                                 output_type=form.output_type.data,
#                                 celery_id=celery_id))
    
    _log.info("Rendering index page")
    
    return render_template('index.html')


@bp.errorhandler(Exception)
def exception_error_handler(error):  # pragma: no cover
    import traceback
    _log.error("Unhandled exception:\n{}".format(traceback.format_exc(error)))
    return render_template('error.html', msg=error), 500
