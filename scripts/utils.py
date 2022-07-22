from os import PathLike
from typing import Union

from ruamel.yaml import YAML


def load_yaml(path: Union[str, PathLike]) -> dict:
	with open(path, 'r', encoding='utf8') as f:
		return YAML().load(f)
