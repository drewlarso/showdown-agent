import json
from pathlib import Path

import requests
from poke_env import to_id_str

URL = "https://pkmn.github.io/randbats/data/gen9randombattle.json"


def _convert_to_id_strs(value):
    if isinstance(value, dict):
        output = {}
        for k, v in value.items():
            output[_convert_to_id_strs(k)] = _convert_to_id_strs(v)
        return output
    if isinstance(value, list):
        output = []
        for v in value:
            output.append(_convert_to_id_strs(v))
        return output
    if isinstance(value, str):
        return to_id_str(value)
    return value


def fetch_randbats():
    print("fetching randbats...")
    data = requests.get(URL)

    data_folder = Path(__file__).parent.parent / "data"
    data_folder.mkdir(parents=True, exist_ok=True)
    file = data_folder / "randbats.json"
    file.touch(exist_ok=True)

    randbats = json.loads(data.content)
    randbats = _convert_to_id_strs(randbats)
    randbats = json.dumps(randbats)

    with open(file, "w") as f:
        f.write(randbats)
    print("success!")


if __name__ == "__main__":
    fetch_randbats()
