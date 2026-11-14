def modify_attack(item: str, category: str, attack: int):
    match item:
        case "choiceband" if category == "PHYSICAL":
            return attack * 3 // 2
        case "choicespecs" if category == "SPECIAL":
            return attack * 3 // 2
        case _:
            return attack


def modify_defense(item: str, category: str, defense: int):
    match item:
        case "assaultvest" if category == "SPECIAL":
            return defense * 3 // 2
        case "eviolite":
            return defense * 3 // 2
        case _:
            return defense


def modify_speed(item: str, speed: int):
    match item:
        case "choicescarf":
            return speed * 3 // 2
        case _:
            return speed


def modify_damage(item: str, damage: int):
    match item:
        case "lifeorb":
            return damage * 13 // 10
        case _:
            return damage


def end_of_turn_hp(item: str, hp_percent: float):
    if hp_percent <= 0:
        return hp_percent
    match item:
        case "leftovers":
            return min(1.0, hp_percent + 1 / 16)
        case _:
            return hp_percent
