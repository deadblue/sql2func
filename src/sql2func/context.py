from __future__ import annotations

import logging
from contextvars import ContextVar, Token
from typing import Callable
from types import TracebackType

from .dbapi2 import Connection


_cv_ctx: ContextVar[SqlContext] = ContextVar('sql2func.context')

_logger = logging.getLogger(__name__)


Connector = Callable[[], Connection]


class SqlContext:

    _connector: Connector
    _conn: Connection | None = None
    _token: Token | None = None

    def __init__(self, connector: Connector) -> None:
        self._connector = connector

    def get_connection(self) -> Connection:
        if self._conn is None:
            self._conn = self._connector()
        return self._conn

    def push(self):
        if self._token is None:
            self._token = _cv_ctx.set(self)
        else:
            _logger.warning('Context has been pushed!')

    def pop(self, exc_value: BaseException | None):
        if self._token is None:
            _logger.warning('Context has been popped or never be pushed!')
            return
        if self._conn is not None:
            if exc_value is not None:
                self._conn.rollback()
            else:
                self._conn.commit()
            self._conn.close()
            self._conn = None
        _cv_ctx.reset(self._token)

    def __enter__(self) -> SqlContext:
        self.push()
        return self

    def __exit__(
            self, 
            exc_type: type[BaseException] | None, 
            exc_value: BaseException | None, 
            traceback: TracebackType | None
        ) -> None:
        self.pop(exc_value)


def current_context() -> SqlContext | None:
    return _cv_ctx.get(None)