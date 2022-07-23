import shutil
from typing import Callable, Any, Dict

from git import Repo

import utils
from constant import OUTPUT_DIR, DATA_DIR, MC_VERSIONS, LANGUAGES, MCVersion, OUTPUT_DIFF_DIR, OUTPUT_PAGE_DIR
from phase import PhaseTree
from translation import language_context, tr

trees: Dict[MCVersion, PhaseTree] = {}


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
	OUTPUT_PAGE_DIR.mkdir()
	OUTPUT_DIFF_DIR.mkdir()


def load():
	for mcv in MC_VERSIONS:
		data = utils.load_yaml(DATA_DIR / 'phase' / '{}.yml'.format(mcv.name))
		trees[mcv] = PhaseTree.create(data)


def gen_page(mcv: MCVersion, writeln: Callable[[str], Any]):
	writeln('# {}\n'.format(Text('title', mcv.name)))
	writeln('{}\n'.format(Text('applicable_version', mcv.version_range)))

	root = trees[mcv]
	writeln('# {}\n'.format(Text('phase_tree')))
	writeln('```')
	root.print_tree(writeln)
	writeln('```')
	writeln('')

	writeln('# {}\n'.format(Text('phase_details')))

	def print_detail(node: PhaseTree):
		writeln('### {}\n'.format(node.name))
		writeln('{}\n'.format(node.detail))

	root.for_each(print_detail)


def gen_pages():
	with utils.write_file(OUTPUT_PAGE_DIR / 'README.md') as f:
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
				with utils.write_file(OUTPUT_PAGE_DIR / 'phases' / '{}-{}.md'.format(mcv.name, lang)) as f:
					gen_page(mcv, lambda s: f.write(s + '\n'))


def gen_git():
	phase_file_name = 'phases.md'
	for lang in LANGUAGES:
		repo_path = OUTPUT_DIFF_DIR / lang
		with language_context(lang):
			repo = Repo.init(repo_path)
			for mcv in MC_VERSIONS:
				with utils.write_file(repo_path / phase_file_name) as f:
					f.write('```\n')
					trees[mcv].print_tree(lambda s: f.write(s + '\n'))
					f.write('```\n')
				repo.index.add([phase_file_name])
				repo.index.commit('Minecraft {}\n\nversion range: {}'.format(mcv.name, mcv.version_range))


def main():
	clean()
	load()
	gen_pages()
	gen_git()


if __name__ == '__main__':
	main()
