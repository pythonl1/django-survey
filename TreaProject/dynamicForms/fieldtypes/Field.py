

class Validator(object):
    """
    Default validator
    """
    def validate(self, value, restrictions):
        #default validation or pass
        return True
    
    def get_validations(self, json, id):
        for page in json['pages']:
            for field in page['fields']:
                if (field['field_id'] == id):
                    return field['validations']