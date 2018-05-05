from textx.exceptions import TextXSemanticError


class SimpleType(object):
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

    def __str__(self):
        return self.name


def get_classes():
    return [SimpleType]


def get_builtins():
    return {
            'int': SimpleType(None, 'int'),
            'string': SimpleType(None, 'string')
    }


def model_proc(model, metamodel):
    '''
    Check for conflict class names in model file
    '''
    cls_names = [cls.name for cls in model.classes]
    for c_name in cls_names:
        if cls_names.count(c_name) > 1:
            raise TextXSemanticError("Class name '%s' is already defined!" % c_name)


def get_model_proc():
    return [model_proc]


def class_obj_proc(cls):
    '''
    Check if class name start with capital letter
    '''
    if cls.name != cls.name.capitalize():
        err = TextXSemanticError("Class name '%s' must start with capital letter!" % cls.name)
        err.offset = cls._tx_position
        raise err
    
def get_obj_proc():
    return {
        'Class': class_obj_proc
    }
