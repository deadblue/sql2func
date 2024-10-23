"""
Python Database API v2.0 classes definition.

Reference: https://peps.python.org/pep-0249/
"""

__author__ = 'deadblue'

from typing import (
    Any, Protocol, Sequence, runtime_checkable
)


@runtime_checkable
class Cursor(Protocol):

    arraysize: int

    def callproc(self, procname: str, parameters: Sequence[Any] = ()): ...

    def close(self) -> None: ...

    def execute(self, statement: str, parameters: Sequence[Any] = ()): ...

    def executemany(self, statement: str, parameters: Sequence[Any]): ...

    def fetchone(self) -> Sequence[Any]: ...

    def fetchmany(self, size: int) -> Sequence[Sequence[Any]]: ...

    def fetchall(self) -> Sequence[Sequence[Any]]: ...

    @property
    def description(self) -> Sequence[Sequence[Any]]: ...

    @property
    def rowcount(self) -> int: ...


@runtime_checkable
class Connection(Protocol):

    def cursor(self, *args) -> Cursor: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...

    def close(self) -> None: ...
