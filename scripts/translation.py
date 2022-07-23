from contextlib import contextmanager
from typing import Dict, Optional

import utils
from constant import LANGUAGES, DATA_DIR, DEFAULT_LANGUAGE

__all__ = [
	'language_context',
	'current_lang',
	'tr',
]

# lang -> (key -> text)
__translation_dict: Dict[str, Dict[str, str]] = {}
__current_lang: str = DEFAULT_LANGUAGE


def __load():
	for lang in LANGUAGES:
		yml = utils.load_yaml(DATA_DIR / 'lang' / (lang + '.yml'))
		translation = {}
		__build(translation, yml, '')
		__translation_dict[lang] = translation


def __build(translation: Dict[str, str], obj: dict, path: str):
	for key, value in obj.items():
		full_key = key if len(path) == 0 else path + '.' + key
		if isinstance(value, str):
			translation[full_key] = value
		elif isinstance(value, dict):
			__build(translation, value, full_key)
		else:
			raise TypeError()


@contextmanager
def language_context(lang: str):
	global __current_lang
	prev_lang = __current_lang
	__current_lang = lang
	try:
		yield
	finally:
		__current_lang = prev_lang


def current_lang() -> str:
	return __current_lang


def __get(lang: str, key: str) -> Optional[str]:
	return __translation_dict.get(lang, {}).get(key)


def tr(key: str, *args, **kwargs):
	text = __get(__current_lang, key) or key
	return text.format(*args, **kwargs)


def get_lang_specified_file_name(name: str) -> str:
	base, extension = name.rsplit('.', 1)
	split = base.rsplit('-', 1)
	if len(split) == 2 and split[1] in LANGUAGES:
		base = split[0]  # remove existed language suffix
	if current_lang() == DEFAULT_LANGUAGE and base.upper() == 'README':
		return '{}.{}'.format(base, extension)
	else:
		return '{}-{}.{}'.format(base, current_lang(), extension)


__load()
