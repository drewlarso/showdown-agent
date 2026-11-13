import json
from itertools import combinations
from pathlib import Path
from typing import Any

from poke_env.battle import Pokemon


def _load_randbats():
    data_file = Path(__file__).parent.parent.parent / "data" / "randbats.json"
    if not data_file.exists():
        raise RuntimeError("no randbats found, run the fetch_randbats.py script to fetch them")

    with open(data_file, "r") as f:
        data = json.loads(f.read())

    return data


RANDBATS = _load_randbats()


def get_role_info(pokemon: Pokemon, role: str):
    pokemon_info = _get_pokemon_info(pokemon)
    return pokemon_info["roles"][role]


def get_move_probabilities(pokemon: Pokemon, role: str):
    role_info = get_role_info(pokemon, role)
    pool = role_info["moves"]

    revealed = set(pokemon.moves)
    unknown = [move for move in pool if move not in revealed]

    open_slots = max(0, min(4, len(pool)) - len(revealed))
    share = min(1.0, open_slots / len(unknown)) if unknown else 0.0

    probabilities = {move: 1.0 for move in revealed}
    for move in unknown:
        probabilities[move] = share

    return probabilities


def get_role_probabilities(pokemon: Pokemon):
    pokemon_info = _get_pokemon_info(pokemon)
    roles: dict[str, Any] = pokemon_info["roles"]

    beliefs = {role: 1 / len(roles) for role in roles}

    for factor in [_get_move_likelyhood, _get_item_likelyhood, _get_ability_likelyhood]:
        likelyhood = {role: factor(pokemon, roles[role]) for role in roles}
        unnorm = {role: beliefs[role] * likelyhood[role] for role in roles}
        total = sum(unnorm.values())
        if total > 0:
            beliefs = {role: unnorm[role] / total for role in roles}

    return beliefs


def _get_pokemon_info(pokemon: Pokemon) -> dict[str, Any]:
    if pokemon.species in RANDBATS:
        return RANDBATS[pokemon.species]
    if pokemon.base_species in RANDBATS:
        return RANDBATS[pokemon.base_species]
    raise RuntimeError(f"could not find '{pokemon.species}' in the randbats file")


def _get_matching_sets(pokemon: Pokemon, role_info: dict[str, Any]):
    revealed = set(pokemon.moves)
    pool = role_info["moves"]

    possible_sets = list(combinations(pool, min(4, len(pool))))
    matching_sets = [s for s in possible_sets if revealed <= set(s)]

    return matching_sets, possible_sets


def _get_move_likelyhood(pokemon: Pokemon, role: dict[str, Any]):
    matching_sets, possible_sets = _get_matching_sets(pokemon, role)
    return len(matching_sets) / len(possible_sets)


def _get_item_likelyhood(pokemon: Pokemon, role: dict[str, Any]):
    if not pokemon.item or pokemon.item == "unknown_item":
        return 1.0
    choices = role["items"] or []
    return 1 / len(choices) if pokemon.item in choices else 0.0


def _get_ability_likelyhood(pokemon: Pokemon, role: dict[str, Any]):
    if not pokemon.ability or pokemon.ability == "unknown_ability":
        return 1.0
    choices = role["abilities"] or []
    return 1 / len(choices) if pokemon.ability in choices else 0.0
