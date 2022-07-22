import shutil
from typing import Callable, Any, NamedTuple

import utils
from constant import OUTPUT_DIR, DATA_DIR, MC_VERSIONS, LANGUAGES, MCVersion
from phase import PhaseTree
from translation import language_context, tr


class Text:
	def __init__(self, key: str, *args):
		self.key = key
		self.args = args

	def __str__(self) -> str:
		return tr('page.' + self.key, *self.args)


def clean():
	if OUTPUT_DIR.exists():
		shutil.rmtree(OUTPUT_DIR)
	OUTPUT_DIR.mkdir()


def generate_page(mcv: MCVersion, writeln: Callable[[str], Any]):
	w = utils.load_yaml(DATA_DIR / 'phase' / '{}.yml'.format(mcv.name))
	writeln('# {}\n\n'.format(Text('title', mcv.name)))
	writeln('{}\n\n'.format(Text('applicable_version', mcv.version_range)))

	writeln('# {}\n\n'.format(Text('phase_tree')))
	root = PhaseTree.create(w)
	writeln('```\n')
	root.print_tree(writeln)
	writeln('```\n')

	writeln('# {}\n\n'.format(Text('phase_details')))

	def print_detail(node: PhaseTree):
		writeln('### {}\n\n'.format(node.name))
		writeln('{}\n\n'.format(node.detail))

	root.for_each(print_detail)


def generate():
	with open(OUTPUT_DIR / 'README.md', 'w', encoding='utf8') as f:
		f.write('# Index\n\n')
		for mcv in MC_VERSIONS:
			f.write('- {}:'.format(mcv.version_range))
			for lang in LANGUAGES:
				with language_context(lang):
					f.write(' [[{}]](./{}-{}.md)'.format(tr('_language_name'), mcv.name, lang))
			f.write('\n')
		f.write('\n')

	for mcv in MC_VERSIONS:
		for lang in LANGUAGES:
			with language_context(lang):
				with open(OUTPUT_DIR / '{}-{}.md'.format(mcv.name, lang), 'w', encoding='utf8') as f:
					generate_page(mcv, lambda s: f.write(s + '\n'))


def main():
	clean()
	generate()


if __name__ == '__main__':
	main()
