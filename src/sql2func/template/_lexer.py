__author__ = 'deadblue'

from hashlib import sha1
from typing import Generator, Union

import jinja2
from jinja2 import lexer

from . import _nodes as nodes


_jinja_env = jinja2.Environment()
_jinja_lexer = lexer.get_lexer(_jinja_env)


class LexException(Exception):
    
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class UnexpectedTokenError(LexException):

    def __init__(self, token: lexer.Token) -> None:
        super().__init__(f'Line {token.lineno}: "{token.value}"')

class IncompleteBlockError(LexException):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Lexer:

    _tree_id: str
    _stream: lexer.TokenStream

    def __init__(self, source: str) -> None:
        self._tree_id = sha1(source.encode()).hexdigest()
        self._stream = _jinja_lexer.tokenize(source)

    def parse(self) -> nodes.Tree:
        tree = nodes.Tree(id=self._tree_id)
        for node in self._read_node():
            tree.append(node)
        return tree

    def _read_node(self, end_block: Union[str, None] = None) -> Generator[nodes.Node|None, None, None]:
        for token in self._stream:
            if token.type == lexer.TOKEN_DATA:
                yield nodes.TextNode(token.value)
            elif token.type == lexer.TOKEN_VARIABLE_BEGIN:
                yield self._read_var_node()
            elif token.type == lexer.TOKEN_BLOCK_BEGIN:
                yield self._read_block_node(end_block)

    def _read_var_node(self) -> nodes.VarNode:
        buf = []
        for token in self._stream:
            if token.type in (lexer.TOKEN_NAME, lexer.TOKEN_DOT):
                buf.append(token.value)
            elif token.type == lexer.TOKEN_VARIABLE_END:
                return nodes.VarNode(''.join(buf).strip())
            else:
                raise UnexpectedTokenError(token)
        raise IncompleteBlockError()

    def _read_block_node(self, end_block: Union[str, None]) -> nodes.Node:
        # Get token 
        token = self._next_token()
        if token is None: raise IncompleteBlockError()

        block_type = token.value
        if end_block is not None and block_type == end_block:
            self._skip_tokens(lexer.TOKEN_BLOCK_END)
            return None
        # TODO: Support more block, e.g.: if.
        if block_type == 'for':
            return self._read_for_block_node()
        else:
            raise UnexpectedTokenError(token)

    def _read_for_block_node(self) -> nodes.ForNode:
        for_node = nodes.ForNode(it_var_name='', var_name='')
        state = 0
        name_buf = []
        while True:
            token = self._next_token()
            if token is None: raise IncompleteBlockError()
            if state == 0:
                if token.type == lexer.TOKEN_NAME:
                    for_node.it_var_name = token.value
                    state = 1
                else:
                    raise UnexpectedTokenError(token)
            elif state == 1:
                if token.type == lexer.TOKEN_NAME and token.value == 'in':
                    state = 2
                else:
                    raise UnexpectedTokenError(token)
            elif state == 2:
                if token.type in (lexer.TOKEN_NAME, lexer.TOKEN_DOT):
                    name_buf.append(token.value)
                elif token.type == lexer.TOKEN_BLOCK_END:
                    for_node.var_name = ''.join(name_buf)
                    break
        for node in self._read_node('endfor'):
            if node is not None: 
                for_node.append(node)
            else:
                break
        return for_node

    def _next_token(self) -> lexer.Token | None:
        try:
            return next(self._stream)
        except StopIteration:
            return None

    def _skip_tokens(self, stop_token_type: str):
        for token in self._stream:
            if token.type == stop_token_type:
                return
        raise IncompleteBlockError()
