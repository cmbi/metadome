'''
Created on Aug 11, 2017

@author: laurens
'''

import re

from flask_wtf import Form
from wtforms.fields import FileField, SelectField, TextAreaField, TextField
from wtforms.validators import Regexp

from metadom.presentation.validators import (FileExtension, NAminoAcids,
                                           NotRequiredIfOneOf)


RE_PDB_ID = re.compile(r"^[0-9a-zA-Z]{4}$")


class MetaDomForm(Form):
#     input_type = SelectField(u'Input',
#                              choices=[('gene_id', 'PDB code'),
#                                       ('pdb_redo_id', 'PDB_REDO code'),
#                                       ('pdb_file', 'PDB file'),
#                                       ('sequence', 'Sequence')])
#     output_type = SelectField(u'Output',
#                               choices=[('text', 'TEXT'),])
    
    def __init__(self, allowed_extensions=None, **kwargs):
        super(MetaDomForm, self).__init__(**kwargs)
#         if allowed_extensions:
#             file_field = self._fields.get('file_')
#             file_field.validators.append(FileExtension(allowed_extensions))