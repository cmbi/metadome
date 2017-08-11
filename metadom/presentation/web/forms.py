from flask_wtf import Form
from wtforms.fields import TextField


class MetaDomForm(Form):
    entry_id = TextField(u'ID')
    position = TextField(u'Position')

    def __init__(self, allowed_extensions=None, **kwargs):
        super(MetaDomForm, self).__init__(**kwargs)
