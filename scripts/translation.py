from contextlib import contextmanager
from typing import Dict, Optional

from ruamel.yaml import YAML

import utils
from constant import LANGUAGES, DATA_DIR, DEFAULT_LANGUAGE

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
	prev_lang = lang
	__current_lang = lang
	try:
		yield
	finally:
		__current_lang = prev_lang


def __get(lang: str, key: str) -> Optional[str]:
	return __translation_dict.get(lang, {}).get(key)


def tr(key: str, *args, **kwargs):
	text = __get(__current_lang, key) or key
	return text.format(*args, **kwargs)


__load()
