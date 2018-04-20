from flask_wtf import Form
from flask_wtf.form import FlaskForm
from wtforms.fields import TextField
from wtforms.fields.html5 import EmailField
from wtforms.fields.simple import TextAreaField
from wtforms import validators


class MetaDomForm(Form):
    entry_id = TextField(u'ID')
    position = TextField(u'Position')

    def __init__(self, allowed_extensions=None, **kwargs):
        super(MetaDomForm, self).__init__(**kwargs)


class SupportForm(FlaskForm):
    email = EmailField('Email',
                       [validators.DataRequired(), validators.Email()])
    body = TextAreaField('Body')