__author__ = 'deadblue'

import inspect
from typing import (
    Callable, ParamSpec, Sequence, TypeVar
)

from .template import Template
from ._engine import execute_query, execute_update


P = ParamSpec('P')
R = TypeVar('R')


def select(statement: str | Sequence[str]):
    stmt_tmpl = Template.parse(statement)
    def wrapper_creator(func: Callable[P, R]) -> Callable[P, R]:
        func_spec = inspect.getfullargspec(func)
        is_method = len(func_spec.args) > 0 and func_spec.args[0] == 'self'
        ret_cls = func_spec.annotations.get('return', None)
        # TODO: Check result_cls here
        def wrapper(*args, **kwargs) -> R:
            call_args = inspect.getcallargs(func, *args, **kwargs)
            if is_method:
                call_args.pop('self', None)
            result = stmt_tmpl.render(**call_args)
            return execute_query(result.statement, result.arguments, ret_cls)
        return wrapper
    return wrapper_creator


def update(statement: str | Sequence[str]):
    stmt_tmpl = Template.parse(statement)
    def wrapper_creator(func: Callable[P, R]) -> Callable[P, R]:
        func_spec = inspect.getfullargspec(func)
        is_method = len(func_spec.args) > 0 and func_spec.args[0] == 'self'
        def wrapper(*args, **kwargs) -> R:
            call_args = inspect.getcallargs(func, *args, **kwargs)
            if is_method:
                call_args.pop('self', None)
            result = stmt_tmpl.render(**call_args)
            return execute_update(result.statement, result.arguments)
        return wrapper
    return wrapper_creator


insert = update

delete = update
