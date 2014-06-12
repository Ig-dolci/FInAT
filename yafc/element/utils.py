"""
from http://stackoverflow.com/questions/2025562/inherit-docstrings-in-python-class-inheritance

doc_inherit decorator

Usage:

class Foo(object):
    def foo(self):
        "Frobber"
        pass

class Bar(Foo):
    @doc_inherit
    def foo(self):
        pass

Now, Bar.foo.__doc__ == Bar().foo.__doc__ == Foo.foo.__doc__ == "Frobber"
"""

import pymbolic.primitives as p
from functools import wraps


class DocInherit(object):
    """
    Docstring inheriting method descriptor

    The class itself is also used as a decorator
    """

    def __init__(self, mthd):
        self.mthd = mthd
        self.name = mthd.__name__

    def __get__(self, obj, cls):
        if obj:
            return self.get_with_inst(obj, cls)
        else:
            return self.get_no_inst(cls)

    def get_with_inst(self, obj, cls):

        overridden = getattr(super(cls, obj), self.name, None)

        @wraps(self.mthd, assigned=('__name__','__module__'))
        def f(*args, **kwargs):
            return self.mthd(obj, *args, **kwargs)

        return self.use_parent_doc(f, overridden)

    def get_no_inst(self, cls):

        for parent in cls.__mro__[1:]:
            overridden = getattr(parent, self.name, None)
            if overridden:
                break

        @wraps(self.mthd, assigned=('__name__', '__module__'))
        def f(*args, **kwargs):
            return self.mthd(*args, **kwargs)

        return self.use_parent_doc(f, overridden)

    def use_parent_doc(self, func, source):
        if source is None:
            raise NameError("Can't find '%s' in parents" % self.name)
        func.__doc__ = source.__doc__
        return func

doc_inherit = DocInherit


class KernelDataDictionary(dict):

    def __init__(self):
        self._identifiers = {}
        self.prefix = 'i'

    def new_identifier(self, prefix=None):

        prefix = prefix or self.prefix

        '''Returns an identifier, guaranteed to be unique'''
        if prefix in self._identifiers:
            self._identifiers[prefix] += 1
        else:
            self._identifiers[prefix] = 0
        return p.Variable(prefix + str(self._identifiers[prefix]))


class KernelData(object):
    def __init__(self):

        self.static = KernelDataDictionary()
        self.params.prefix = 'phi'
        self.params = KernelDataDictionary()
        self.params.prefix = 'w'
