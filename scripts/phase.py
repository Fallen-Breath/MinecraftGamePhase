from typing import List, Any, Callable, Optional

from translation import tr

_WRITER = Callable[[str], Any]


class PhaseTree:
	def __init__(self, node_id: str):
		self.node_id: str = node_id
		self.children: List['PhaseTree'] = []
		self.parent: Optional['PhaseTree'] = None

	def __repr__(self):
		return 'PhaseTree[id={}]'.format(self.node_id)

	@property
	def is_root(self) -> bool:
		return self.parent is None

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

	def print_tree(self, writer: _WRITER):
		items = [self.name]
		if not self.is_root:
			items.append('└── ' if self.is_last_child else '├── ')
		parent = self.parent
		while parent is not None and not parent.is_root:
			items.append('    ' if parent.is_last_child else '│   ')
			parent = parent.parent

		line = ''.join(reversed(items))
		writer(line)

		for child in self.children:
			child.print_tree(writer)

	def for_each(self, consumer: Callable[['PhaseTree'], Any]):
		def traverse(node: PhaseTree):
			consumer(node)
			for child in node.children:
				traverse(child)

		traverse(self)
