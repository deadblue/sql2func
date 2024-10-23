__author__ = 'deadblue'

from abc import ABC, abstractmethod
from typing import Any, Dict


class Renderer(ABC):

    def get_value(self, var_name: str, context: Dict[str, Any]) -> Any:
        value = context
        for var_part in var_name.split('.'):
            if isinstance(value, dict):
                value = value.get(var_part, None)
            else:
                value = getattr(value, var_part)
        return value

    @abstractmethod
    def render(self, values, **context): pass
