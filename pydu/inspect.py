from __future__ import absolute_import

import inspect

from pydu.compat import PY2


#########################################
# funcs for PY2
#########################################
if PY2:
    def getargspec(func):
        return inspect.getargspec(func)


    def get_func_args(func):
        argspec = inspect.getargspec(func)
        if inspect.ismethod(func):
            return argspec[1:] # ignore 'self'
        return argspec.args


    def get_func_full_args(func):
        """
        Return a list of (argument name, default value) tuples. If the argument
        does not have a default value, omit it in the tuple. Arguments such as
        *args and **kwargs are also included.
        """
        argspec = inspect.getargspec(func)
        args = argspec.args[1:]  # ignore 'self'
        defaults = argspec.defaults or []
        # Split args into two lists depending on whether they have default value
        no_default = args[:len(args) - len(defaults)]
        with_default = args[len(args) - len(defaults):]
        # Join the two lists and combine it with default values
        args = [(arg,) for arg in no_default] + zip(with_default, defaults)
        # Add possible *args and **kwargs and prepend them with '*' or '**'
        varargs = [('*' + argspec.varargs,)] if argspec.varargs else []
        kwargs = [('**' + argspec.keywords,)] if argspec.keywords else []
        return args + varargs + kwargs


    def func_accepts_kwargs(func):
        # Not all callables are inspectable with getargspec, so we'll
        # try a couple different ways but in the end fall back on assuming
        # it is -- we don't want to prevent registration of valid but weird
        # callables.
        try:
            argspec = inspect.getargspec(func)
        except TypeError:
            try:
                argspec = inspect.getargspec(func.__call__)
            except (TypeError, AttributeError):
                argspec = None
        return not argspec or argspec[2] is not None


    def func_accepts_var_args(func):
        """
        Return True if function 'func' accepts positional arguments *args.
        """
        return inspect.getargspec(func)[1] is not None


    def func_supports_parameter(func, parameter):
        args, varargs, varkw, defaults = inspect.getargspec(func)
        return parameter in args

#########################################
# funcs for PY3
#########################################
else:
    def getargspec(func):
        sig = inspect.signature(func)
        args = [
            p.name for p in sig.parameters.values()
            if p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
        ]
        varargs = [
            p.name for p in sig.parameters.values()
            if p.kind == inspect.Parameter.VAR_POSITIONAL
        ]
        varargs = varargs[0] if varargs else None
        varkw = [
            p.name for p in sig.parameters.values()
            if p.kind == inspect.Parameter.VAR_KEYWORD
        ]
        varkw = varkw[0] if varkw else None
        defaults = [
                       p.default for p in sig.parameters.values()
                       if
                       p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD and p.default is not p.empty
                   ] or None
        return args, varargs, varkw, defaults


    def get_func_args(func):
        sig = inspect.signature(func)
        return [
            arg_name for arg_name, param in sig.parameters.items()
            if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
        ]


    def get_func_full_args(func):
        """
        Return a list of (argument name, default value) tuples. If the argument
        does not have a default value, omit it in the tuple. Arguments such as
        *args and **kwargs are also included.
        """
        sig = inspect.signature(func)
        args = []
        for arg_name, param in sig.parameters.items():
            name = arg_name
            # Ignore 'self'
            if name == 'self':
                continue
            if param.kind == inspect.Parameter.VAR_POSITIONAL:
                name = '*' + name
            elif param.kind == inspect.Parameter.VAR_KEYWORD:
                name = '**' + name
            if param.default != inspect.Parameter.empty:
                args.append((name, param.default))
            else:
                args.append((name,))
        return args


    def func_accepts_kwargs(func):
        return any(
            p for p in inspect.signature(func).parameters.values()
            if p.kind == p.VAR_KEYWORD
        )


    def func_accepts_var_args(func):
        """
        Return True if function 'func' accepts positional arguments *args.
        """
        return any(
            p for p in inspect.signature(func).parameters.values()
            if p.kind == p.VAR_POSITIONAL
        )


    def func_supports_parameter(func, parameter):
        return parameter in inspect.signature(func).parameters


#########################################
# common funcs
#########################################
def func_has_no_args(func):
    args = inspect.getargspec(func)[0] if PY2 else [
        p for p in inspect.signature(func).parameters.values()
        if p.kind == p.POSITIONAL_OR_KEYWORD
    ]
    return len(args) == 1