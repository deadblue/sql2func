__author__ = 'deadblue'

import logging
from typing import List, Sequence

from ._nodes import Tree, Node, TextNode, VarNode, ForNode
from ._renderer import Renderer


# Code indent
____ = '    '

_logger = logging.getLogger(__name__)


def _escape_string(s: str) -> str:
    return s.replace('\\', r'\\').replace('\n', r'\n').replace("'", r"\'").replace('"', r'\"')

def _render_func_name(scope: str | None) -> str:
    return 'render' if scope is None else f'render_{scope}'

def _make_render_code(
        nodes: Sequence[Node], 
        source_buf: List[str],
        scope: str = None
    ):
    func_name = _render_func_name(scope)
    func_buf = [
        f"{____}def {func_name}(self, values, **context) -> str:",
        f"{____}{____}buf = []"
    ]
    for_id = 0
    for node in nodes:
        if isinstance(node, TextNode):
            text = _escape_string(node.content)
            func_buf.append(f"{____}{____}buf.append('{text}')")
        elif isinstance(node, VarNode):
            func_buf.append(f"{____}{____}values.append(self.get_value('{node.var_name}', context))")
            func_buf.append(f"{____}{____}buf.append('?')")
        elif isinstance(node, ForNode):
            sub_scope = f'for_{for_id}'
            _make_render_code(
                nodes=node.children, 
                source_buf=source_buf, 
                scope=sub_scope
            )
            func_buf.append(f"{____}{____}buf.append('{node.separator}'.join([")
            func_buf.append(f"{____}{____}{____}self.{_render_func_name(sub_scope)}(values, {node.it_var_name}=item)")
            func_buf.append(f"{____}{____}{____}for item in self.get_value('{node.var_name}', context)")
            func_buf.append(f"{____}{____}]))")
            for_id += 1
            pass
    func_buf.append(rf"{____}{____}return ''.join(buf)")
    source_buf.extend([
        '',
        '\n'.join(func_buf),
        ''
    ])


def compile_tree(tree: Tree) -> Renderer:
    renderer_class_name = f'Renderer_{tree.id}'
    # Make source
    source_buf = [
        f'from {Renderer.__module__} import Renderer',
        '',
        f'class {renderer_class_name}(Renderer):'
    ]
    _make_render_code(
        nodes=tree.children,
        source_buf=source_buf
    )
    source = '\n'.join(source_buf)
    _logger.debug('Render source code:\n%s', source)
    # Compile source
    code = compile(
        source=source,
        filename='<string>',
        mode='exec'
    )
    # Execute code
    global_vars, local_vars = {}, {}
    exec(code, global_vars, local_vars)
    # Extract render function
    return local_vars.get(renderer_class_name)
