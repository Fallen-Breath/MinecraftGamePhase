from contextlib import contextmanager
from os import PathLike
from pathlib import Path
from typing import Union, IO

from ruamel.yaml import YAML


def load_yaml(path: Union[str, PathLike]) -> dict:
	with open(path, 'r', encoding='utf8') as f:
		return YAML(typ='safe').load(f)


@contextmanager
def write_file(path: Union[str, PathLike]) -> IO[str]:
	if isinstance(path, str):
		path = Path(path)
	path.parent.mkdir(parents=True, exist_ok=True)
	with open(path, 'w', encoding='utf8') as f:
		yield f
