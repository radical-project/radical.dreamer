
class RDException(Exception):

    """RDError is the basic exception raised by RADICAL-DREAMER."""

    def __init__(self, msg):
        super().__init__(msg)


class RDTypeError(RDException):

    """RDTypeError is raised if value of a wrong type is passed to a function or
    assigned as an attribute of an object."""

    def __init__(self, expected_type, actual_type, entity=None):
        if entity:
            msg = 'Entity: %s; Expected (base) type(s) is %s, but got %s.' % (
                str(entity),
                str(expected_type),
                str(actual_type))
        else:
            msg = 'Expected (base) type(s) is %s, but got %s.' % (
                str(expected_type),
                str(actual_type))
        super().__init__(msg)


class RDValueError(RDException):

    """RDValueError is raised if value that is unacceptable is passed to a
    function or assigned as an attribute of an object."""

    def __init__(self, obj, attribute, expected_value, actual_value):
        if type(expected_value) != list:
            msg = \
                'Value for attribute %s of object %s is incorrect. ' \
                'Expected value is %s, but got %s.' % (
                    str(attribute),
                    str(obj),
                    str(expected_value),
                    str(actual_value))
        else:
            expected_values_str = ''
            for item in expected_value:
                expected_values_str += str(item)
            msg = \
                'Value for attribute %s of object %s is incorrect. ' \
                'Expected values are %s, but got %s.' % (
                    str(attribute),
                    str(obj),
                    str(expected_values_str),
                    str(actual_value))
        super().__init__(msg)
