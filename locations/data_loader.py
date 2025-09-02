import json
import os
from pathlib import Path
from functools import lru_cache
from urllib.request import urlopen

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "india_states_districts.json"
REMOTE_SOURCES = [
	# Preferred: curated list of India states and districts (community datasets)
	"https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/json/india_districts.json",
]


def _from_remote() -> dict:
	for url in REMOTE_SOURCES:
		try:
			with urlopen(url, timeout=10) as resp:
				data = json.loads(resp.read().decode("utf-8"))
				# Expected format: list of {"state_name": str, "district_name": str}
				state_to_districts = {}
				for row in data:
					state = row.get("state_name") or row.get("state") or row.get("State Name")
					dist = row.get("district_name") or row.get("district") or row.get("District Name")
					if not state or not dist:
						continue
					state_to_districts.setdefault(state.strip(), set()).add(dist.strip())
				return {
					"states": sorted(state_to_districts.keys()),
					"districts": {s: sorted(list(d)) for s, d in state_to_districts.items()},
				}
		except Exception:
			continue
	return {"states": [], "districts": {}}


@lru_cache(maxsize=1)
def load_india_locations() -> dict:
	# Local file first
	if DATA_FILE.exists():
		try:
			with open(DATA_FILE, "r", encoding="utf-8") as f:
				return json.load(f)
		except Exception:
			pass
	# Remote fallback
	return _from_remote()