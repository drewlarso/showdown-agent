from dataclasses import dataclass

from agent.state import ActionState, PokeState


@dataclass(frozen=True)
class OrderBranch:
    probability: float
    friendly_goes_first: bool


def resolve_order(
    friendly_action: ActionState,
    opponent_action: ActionState,
    friendly_pokemon: PokeState,
    opponent_pokemon: PokeState,
) -> list[tuple[float, bool]]:  # (probability, friendly_goes_first)
    friendly_priority = friendly_action.priority
    opponent_priority = opponent_action.priority

    if friendly_priority > opponent_priority:
        return [(1.0, True)]
    if friendly_priority < opponent_priority:
        return [(1.0, False)]

    friendly_speed = friendly_pokemon.stats["spe"] or 100
    opponent_speed = opponent_pokemon.stats["spe"] or 100

    if friendly_speed > opponent_speed:
        return [(1.0, True)]
    if friendly_speed < opponent_speed:
        return [(1.0, False)]

    return [(0.5, True), (0.5, False)]
