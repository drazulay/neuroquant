import re

from string import printable


"""
NQCommand

Base class for all commands
"""
class NQCommand(object):

    def __init__(self, definition):
        self.definition = definition
        super().__init__()

    def get_description(self):
        return self.definition.get('description')

    """
    Returns result of calling method on NQCommand subclass intance with args
    and kwargs, or a dict with errors ({"errors":[...]}) if:

        - the required number of positional arguments were not passed
        - required keyword arguments are missing
        - the method does not exist in the NQCommand subclass
        - the method raises an exception when called with args and kwargs
    """
    def execute(self, *args, **kwargs):
        errors = []
        
        print(self.definition)
        print(args, kwargs)
        # check whether we have all required positional arguments
        n_args_req = len(list(filter(lambda arg: arg.startswith('!'),
            self.definition.get('args'))))
        n_args = len(args)
        if n_args != n_args_req:
            errors.append(f'{n_args_req} positional arguments required, {n_args} passed')

        # cast to specified data types
        for k, mod in self.definition.get('kwargs').items():
            # if the ! modifier is present the keyword argument is required
            if mod.find('!') >= 0 and k not in kwargs:
                errors.append(f'keyword argument {k} is required')
                continue

            # arg value
            v = kwargs[k]

            # if the '+' modifier is present we split the kwarg value on comma
            if mod.find('+') >= 0:
                v = v.split(',')

            # make sure we have a list
            if type(v) == str:
                v = [v]
            
            # strip modifiers to get the datatype
            dtype = mod.strip('!+')

            # some asshat protection because we eval the dtype, yolo!
            pattern = re.compile('[\W_]+', re.UNICODE)
            pattern.sub('', printable)
            dtype = ''.join(pattern.split(dtype))

            # map the datatype to the value
            v = [*map(eval(dtype), v)]

            # if we have a length=1 list use the 1st element
            if len(v) == 1:
                v = v.pop()

            kwargs[k] = v

        if errors == []:
            # try to call the method on the concrete class or catch and return
            # the error messages
            try:
                method = self.definition.get('method')
                return {"result": getattr(self, method)(*args, **kwargs)}
            except AttributeError as e:
                errors.append(str(e))
            except Exception as e:
                errors.append(str(e))

        return {"errors": errors}

