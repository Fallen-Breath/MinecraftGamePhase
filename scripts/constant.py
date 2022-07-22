from pathlib import Path
from typing import List, NamedTuple

import utils

ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / 'data'
OUTPUT_DIR = ROOT_DIR / 'pages'
assert DATA_DIR.is_dir()

__meta = utils.load_yaml(DATA_DIR / 'meta.yml')
LANGUAGES: List[str] = __meta['languages']
DEFAULT_LANGUAGE: str = LANGUAGES[0]
IMPORTANT_PHASES: List[str] = __meta['important_phases']


class MCVersion(NamedTuple):
	name: str
	version_range: str


MC_VERSIONS: List[MCVersion] = []
for name, vr in __meta['mc_version'].items():
	MC_VERSIONS.append(MCVersion(name, vr))
