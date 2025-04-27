__author__ = 'deadblue'

import dataclasses
from collections.abc import Collection, Generator
from typing import (
    Any, Dict, Type, TypeVar, get_origin, get_args
)
from types import NoneType, UnionType

from ._compat import (
    is_pydantic_model
)


T = TypeVar('T')


def is_dict(cls: Type) -> bool:
    return issubclass(cls, Dict)

def is_collection(cls: Type) -> bool:
    origin_cls = get_origin(cls)
    return origin_cls is not None and issubclass(origin_cls, Collection)

def is_generator(cls: Type) -> bool:
    origin_cls = get_origin(cls)
    return origin_cls is not None and issubclass(origin_cls, Generator)

def get_item_type(cls: Type, def_cls: Type) -> Type | None:
    type_args = get_args(cls)
    if len(type_args) > 0:
        return type_args[0]
    else:
        return def_cls

def unpack_union_type(cls: Type) -> Type:
    if isinstance(cls, UnionType):
        for tp in get_args(cls):
            if tp is not NoneType:
                return tp
        return NoneType
    else:
        return cls

def convert_to(row: Dict[str, Any], cls: Type[T] | None) -> T:
    if dataclasses.is_dataclass(cls):
        return cls(**row)
    elif is_pydantic_model(cls):
        return cls.model_validate(row)
    elif cls is None or is_dict(cls):
        return row
    # Single column special case
    if len(row) == 1:
        value = next(iter(row.values()))
        if isinstance(value, cls):
            return value
    return None
