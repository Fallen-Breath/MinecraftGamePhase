import shutil
from typing import Callable, Any

import utils
from constant import OUTPUT_DIR, DATA_DIR, MC_VERSIONS, LANGUAGES, MCVersion, OUTPUT_PHASES_DIR
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
	OUTPUT_PHASES_DIR.mkdir()


def generate_page(mcv: MCVersion, writeln: Callable[[str], Any]):
	w = utils.load_yaml(DATA_DIR / 'phase' / '{}.yml'.format(mcv.name))
	writeln('# {}\n'.format(Text('title', mcv.name)))
	writeln('{}\n'.format(Text('applicable_version', mcv.version_range)))

	writeln('# {}\n'.format(Text('phase_tree')))
	root = PhaseTree.create(w)
	writeln('```')
	root.print_tree(writeln)
	writeln('```')
	writeln('')

	writeln('# {}\n'.format(Text('phase_details')))

	def print_detail(node: PhaseTree):
		writeln('### {}\n'.format(node.name))
		writeln('{}\n'.format(node.detail))

	root.for_each(print_detail)


def generate():
	with open(OUTPUT_DIR / 'README.md', 'w', encoding='utf8') as f:
		f.write('# Index\n\n')

		f.write('| Minecraft version | Links |\n'.format(Text('mc_version'), Text('link')))
		f.write('| --- | --- |\n')
		for mcv in MC_VERSIONS:
			items = []
			for lang in LANGUAGES:
				with language_context(lang):
					items.append(' [{}](./phases/{}-{}.md)'.format(tr('_language_name'), mcv.name, lang))
			f.write('| {} | {} |\n'.format(mcv.version_range, ', '.join(items)))
		f.write('\n')

	for mcv in MC_VERSIONS:
		for lang in LANGUAGES:
			with language_context(lang):
				with open(OUTPUT_PHASES_DIR / '{}-{}.md'.format(mcv.name, lang), 'w', encoding='utf8') as f:
					generate_page(mcv, lambda s: f.write(s + '\n'))


def main():
	clean()
	generate()


if __name__ == '__main__':
	main()
