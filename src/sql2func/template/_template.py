__author__ = 'deadblue'

from dataclasses import dataclass
from typing import Any, Sequence, Literal

from ._compiler import compile_tree
from ._lexer import Lexer
from ._renderer import Renderer


@dataclass
class RenderResult:
    statement: str
    arguments: Sequence[Any]


class Template:

    _renderer: Renderer

    def __init__(self, renderer: Renderer) -> None:
        self._renderer = renderer

    def render(self, **kwargs) -> RenderResult:
        args = []
        statement = self._renderer.render(args, **kwargs)
        return RenderResult(
            statement=statement, arguments=args
        )

    @classmethod
    def parse(
        cls, source: str | Sequence[str]
    ) -> 'Template':
        """
        Parse SQL template to object

        Step:
            1. Source string to AST
            2. AST to Python code.
            3. Python code to binary.
        """
        if not isinstance(source, str):
            source = '\n'.join(source)
        tree = Lexer(source).parse()
        # TODO: 
        #   Support more other paramstyles than qmark
        #   Reference: https://peps.python.org/pep-0249/#paramstyle
        render_cls = compile_tree(tree)
        return cls(render_cls())
