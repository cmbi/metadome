import logging

from flask import Blueprint, redirect, render_template, url_for, request

from metadom.presentation.web.forms import MetaDomForm


_log = logging.getLogger(__name__)

bp = Blueprint('web', __name__, static_folder='static',
               template_folder='templates')


@bp.route('/', methods=['GET'])
def index():
    _log.info("Rendering index page")
    return render_template('index.html')


@bp.route("/input", methods=['GET', 'POST'])
def input():
    form = MetaDomForm()
    if form.validate_on_submit():
        # form.entry_id.data, form.postion.data)

        #mappings = MappingRepository.get_mappings(entry_id, position)
        mappings = {
            "test": "hey there"
        }

        # TODO: access database
        # TODO: render result template

        _log.debug("Redirecting to result page")

        # TODO: Send data to result page
        return redirect(url_for('web.result', mappings=mappings))

    _log.debug("Rendering input page")
    return render_template("input.html", form=form)


@bp.route("/result", methods=["GET"])
def result():
    mappings = request.args['mappings']
    return render_template("result.html", mappings=mappings)


@bp.errorhandler(Exception)
def exception_error_handler(error):  # pragma: no cover
    import traceback
    _log.error("Unhandled exception:\n{}".format(traceback.format_exc(error)))
    return render_template('error.html', msg=error), 500
