__author__ = 'deadblue'

from collections.abc import Collection, Generator
from contextlib import closing
from typing import (
    Any, Dict, List, Sequence, Type, TypeVar
)

from .context import current_context
from .dbapi2 import Cursor
from .exception import ContextError
from . import _typing as st


T = TypeVar('T')


def _get_cursor() -> Cursor:
    ctx = current_context()
    if ctx is None: 
        raise ContextError()
    conn = ctx.get_connection()
    return conn.cursor()


def _query_generator(
        statement: str, 
        parameters: Sequence[Any], 
        item_cls: Type[T]
    ) -> Generator[T, None, None]:
    with closing(_get_cursor()) as cursor:
        # Execute query
        cursor.execute(statement, parameters)
        # Get result columns
        cols = cursor.description
        col_count = len(cols)
        # Iterate rows
        while True:
            values = cursor.fetchone()
            if values is None: break
            # Convert sequence to dict
            row = {}
            for i in range(col_count):
                col_name = cols[i][0]
                row[col_name] = values[i]
            # Convert dict to item class
            yield st.convert_to(row, item_cls)


def _query_collection(
        statement: str, 
        parameters: Sequence[Any],
        item_cls: Type[T]
    ) -> Collection[T]:
    items: List[T] = []
    for item in _query_generator(statement, parameters, item_cls):
        items.append(item)
    return items


def execute_query(
        statement: str, 
        parameters: Sequence[Any],
        result_cls: Type[T]
    ) -> T:
    """
    Execute query statement and return result in expect type.

    Args:
        statement (str): Query statement.
        parameters (Sequence[Any]): Statement parameters.
        result_cls (Type[T]): Result type.

    Returns:
        T: Result in type.
    """
    ret_is_gen = st.is_generator(result_cls)
    ret_is_coll = st.is_collection(result_cls)
    item_cls = result_cls
    if ret_is_gen or ret_is_coll:
        item_cls = st.get_item_type(result_cls, Dict[str, Any])
    item_cls = st.unpack_union_type(item_cls)
    if ret_is_gen:
        return _query_generator(statement, parameters, item_cls)
    elif ret_is_coll:
        return _query_collection(statement, parameters, item_cls)
    else:
        for item in _query_generator(statement, parameters, item_cls):
            return item
        return None


def execute_update(statement: str, parameters: Sequence[Any]) -> int:
    """
    Execute update statement and return affected rows count.

    Args:
        statement (str): Update statement.
        parameters (Sequence[Any]): Statement parameters.

    Returns:
        int: Affected row count
    """
    with closing(_get_cursor()) as cursor:
        cursor.execute(statement, parameters)
        return cursor.rowcount
