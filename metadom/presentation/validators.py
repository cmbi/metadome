import logging
import re

from wtforms.validators import Required, StopValidation, ValidationError


RE_FASTA_DESCRIPTION = re.compile(r"^>\S.*\n")
RE_SEQ = re.compile(r"^[XARNDCEQGHILKMFPSTWYVxarndceqghilkmfpstwyv]+$")


_log = logging.getLogger(__name__)


class FileExtension(object):
    """
    Validate the PDB or mmCIF file extension.
    raise ValidationError if the extension of the given filename is not
        supported.
    The extension check is case insensitive.
    """
    def __init__(self, allowed):
        self.allowed = {e.lower() for e in allowed}
        self.message = ('Only the following file extensions are ' +
                        'supported: .{}').format(' .'.join(allowed))

    def __call__(self, form, field):
        field.errors = []
        name = field.data.filename
        if '.' not in name or \
                name.rsplit('.', 1)[1].lower() not in self.allowed:
            raise ValidationError(self.message)


class NotRequiredIfOneOf(Required):
    """
    Validate a field if and only if all other fields have not been given.
    raise StopValidation without a message when other data is found for another
        field and remove prior errors from the field.
    """

    def __init__(self, other_field_names, *args, **kwargs):
        self.other_field_names = other_field_names

        self.message = ("This field is required if '{}' "
                        "{} not been provided.").format(
                            "' and '".join(other_field_names),
                            "have" if len(other_field_names) > 0 else "has")

        super(NotRequiredIfOneOf, self).__init__(message=self.message,
                                                 *args, **kwargs)

    def __call__(self, form, field):
        for field_name in self.other_field_names:
            other_field = form._fields.get(field_name)
            if other_field is None:
                raise Exception("No field named '{}' in form".format(
                    field_name))

            if bool(other_field.data):
                field.errors[:] = []
                raise StopValidation()

        super(NotRequiredIfOneOf, self).__call__(form, field)


class NAminoAcids(object):
    """
    Validate a protein sequence field.
    raise ValidationError if less than min amino acids have been given.
    Amino Acids can be from the set ACDEFGHIKLMNPQRSTVWXY.
    Single sequence FASTA and lowercase 1-letter codes are also accepted.
    Whitespace, sequence numbers, and asteriks are ignored.
    """

    def __init__(self, min=-1, len_message=None, set_message=None,
                 fasta_message=None):
        self.min = min
        if not len_message:
            len_message = u'Must be at least {0:d} amino acids long.'.format(
                min)
        if not set_message:
            set_message = u'This field only accepts 1-letter codes from ' + \
                          'the set "ACDEFGHIKLMNPQRSTVWXY".'
        if not fasta_message:
            fasta_message = u'Multiple sequence FASTA input ' + \
                            'is currently not supported. ' + \
                            'The first line of FASTA input should start ' + \
                            'with ">" followed by a description.'
        self.len_message = len_message
        self.set_message = set_message
        self.fasta_message = fasta_message