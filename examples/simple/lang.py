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
