import shutil
from typing import Dict, IO, Optional

from git import Repo

import utils
from constant import OUTPUT_DIR, DATA_DIR, MC_VERSIONS, LANGUAGES, MCVersion, OUTPUT_DIFF_DIR, OUTPUT_PAGE_DIR, IMPORTANT_PHASES
from translation import language_context, tr, current_lang, get_lang_specified_file_name
from tree import PhaseTree

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


def write_nav_header(file_name: str, file: IO[str]):
	nav_list = []
	for lang in LANGUAGES:
		with language_context(lang):
			lang_name = tr('_language_name')
		if lang == current_lang():
			text = '**{}**'.format(lang_name)
		else:
			with language_context(lang):
				text = '[{}]({})'.format(lang_name, get_lang_specified_file_name(file_name))
		nav_list.append('{}'.format(text))
	file.write('{}\n'.format(' | '.join(nav_list)))
	file.write('\n')


def write_tree(root: PhaseTree, file: IO[str], *, simplified: bool = False, draw_line: bool = True):
	file.write('```\n')
	if simplified:
		root = root.extract(lambda n: n.node_id in IMPORTANT_PHASES)
		assert root is not None
	root.print_tree(lambda s: file.write(s + '\n'), draw_line=draw_line)
	file.write('```\n')
	file.write('\n')


def gen_page(mcv: MCVersion, file: IO[str]):
	file.write('# {}\n\n'.format(Text('title', mcv.name)))
	file.write('{}\n\n'.format(Text('applicable_version', mcv.version_range)))

	root = trees[mcv]
	file.write('## {}\n\n'.format(Text('phase_tree.simplified')))
	write_tree(root, file, simplified=True)

	file.write('## {}\n\n'.format(Text('phase_tree.full')))
	write_tree(root, file, simplified=False)

	file.write('## {}\n\n'.format(Text('phase_details')))

	def print_detail(node: PhaseTree):
		file.write('### {}\n\n'.format(node.name))
		file.write('{}\n\n'.format(node.detail))

	root.for_each(print_detail)


def gen_readme(lang: str):
	file_name = get_lang_specified_file_name('README.md')
	with utils.write_file(OUTPUT_PAGE_DIR / file_name) as f:
		write_nav_header(file_name, f)
		f.write('# {}\n\n'.format(Text('readme.index')))

		f.write('| {} | {} |\n'.format(Text('readme.mc_version'), Text('readme.applicable_version')))
		f.write('| --- | --- |\n')
		for mcv in MC_VERSIONS:
			f.write('| {} | {} |\n'.format('[{}](./phases/{}-{}.md)'.format(mcv.name, mcv.name, lang), mcv.version_range))
		f.write('\n')


def gen_pages():
	for lang in LANGUAGES:
		with language_context(lang):
			gen_readme(lang)

			for mcv in MC_VERSIONS:
				file_name = '{}-{}.md'.format(mcv.name, lang)
				with utils.write_file(OUTPUT_PAGE_DIR / 'phases' / file_name) as f:
					write_nav_header(file_name, f)
					gen_page(mcv, f)


def gen_git():
	name_full = 'phases_full.md'
	name_simplified = 'phases_simplified.md'
	for lang in LANGUAGES:
		repo_path = OUTPUT_DIFF_DIR / lang
		with language_context(lang):
			repo = Repo.init(repo_path)
			prev: Optional[MCVersion] = None
			for mcv in MC_VERSIONS:
				with utils.write_file(repo_path / name_simplified) as f:
					write_tree(trees[mcv], f, simplified=True, draw_line=False)
				with utils.write_file(repo_path / name_full) as f:
					write_tree(trees[mcv], f, simplified=False, draw_line=False)

				message = 'Minecraft {0}\n\nCurrent version: {0} ({1})'.format(mcv.name, mcv.version_range)
				if prev is not None:
					message += '\nPrevious version: {} ({})'.format(prev.name, prev.version_range)
				repo.index.add([name_full, name_simplified])
				repo.index.commit(message)

				prev = mcv


def main():
	clean()
	load()
	gen_pages()
	gen_git()


if __name__ == '__main__':
	main()
