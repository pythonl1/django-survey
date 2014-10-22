
from dynamicForms.fieldtypes import TextField
from dynamicForms.fieldtypes import FieldFactory


class TextAreaField(TextField.TextField):
    """
    Validator for text area is the same as simple TextField
    """
    template_name = "text_area/template.html"
    edit_template_name = "text_area/template_edit.html"
    prp_template_name = "text_area/properties.html"

    def __str__(self):
        return "Multi Line Text"

FieldFactory.FieldFactory.register('TextAreaField', TextAreaField)
