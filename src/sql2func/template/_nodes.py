__author__ = 'deadblue'

from abc import ABC
from dataclasses import dataclass, field
from typing import List


class Node(ABC): pass


@dataclass
class NodeContainer(Node, ABC):

    children: List[Node] = field(init=False)

    def __post_init__(self):
        self.children = []

    def append(self, node: Node):
        self.children.append(node)


@dataclass
class VarNode(Node):
    var_name: str


@dataclass
class TextNode(Node):
    content: str


@dataclass
class ForNode(NodeContainer):
    var_name: str
    it_var_name: str
    separator: str = field(default=',')


@dataclass
class Tree(NodeContainer): 
    id: str
    ...
