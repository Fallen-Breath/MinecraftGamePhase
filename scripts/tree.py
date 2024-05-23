import functools
from typing import List, Any, Callable, Optional

import utils
from constant import DATA_DIR
from translation import tr

_WRITER = Callable[[str], Any]


class PhaseTree:
	@classmethod
	@functools.lru_cache
	def __read_phase_data(cls) -> dict:
		return utils.load_yaml(DATA_DIR / 'phase_data.yml')

	def __init__(self, node_id: str):
		self.node_id: str = node_id
		self.children: List['PhaseTree'] = []
		self.parent: Optional['PhaseTree'] = None
		self.data: dict = self.__read_phase_data().get(node_id) or {}

	def __repr__(self):
		return 'PhaseTree[id={}]'.format(self.node_id)

	@property
	def is_root(self) -> bool:
		return self.parent is None

	@property
	def is_leaf(self) -> bool:
		return len(self.children) == 0

	@property
	def is_last_child(self) -> bool:
		return not self.is_root and len(self.parent.children) > 0 and self.parent.children[-1] is self

	@property
	def name(self) -> str:
		return tr('phase.{}.name'.format(self.node_id))

	@property
	def detail(self) -> str:
		return tr('phase.{}.detail'.format(self.node_id))

	@classmethod
	def create(cls, data) -> 'PhaseTree':
		if isinstance(data, str):
			node_id = data
			children = []
		elif isinstance(data, dict):
			assert len(data) == 1
			node_id, children = list(data.items())[0]
		else:
			raise TypeError()
		node = PhaseTree(node_id)
		for child in children:
			node.add_child(cls.create(child))
		return node

	def add_child(self, node: 'PhaseTree'):
		self.children.append(node)
		node.parent = self

	def for_each(self, consumer: Callable[['PhaseTree'], Any]):
		def traverse(node: PhaseTree):
			consumer(node)
			for child in node.children:
				traverse(child)

		traverse(self)

	def print_tree(self, writer: _WRITER, *, draw_line: bool = True):
		def get_item_line(node: PhaseTree) -> str:
			if not draw_line:
				return '    '
			if node.is_last_child:
				return '└── '
			return '├── '

		def get_parent_line(node: PhaseTree) -> str:
			if node.is_root:
				return ''
			if not draw_line or node.is_last_child:
				return '    '
			return '│   '

		def __print_tree(node, prefix: str):
			line = node.name
			if not node.is_root:
				line = get_item_line(node) + line
			writer(prefix + line)

			for child in node.children:
				__print_tree(child, prefix + get_parent_line(node))

		__print_tree(self, '')

	def extract(self, predicate: Callable[['PhaseTree'], bool]) -> Optional['PhaseTree']:
		node = PhaseTree(self.node_id)
		if self.is_leaf:
			if predicate(self):
				return node
			return None

		for child in self.children:
			c = child.extract(predicate)
			if c is not None:
				node.add_child(c)

		if len(node.children) > 1 or predicate(self):
			return node
		elif len(node.children) == 1:  # remove useless chaining node
			return node.children[0]
		return None
