use crate::{
    state::{Category, Item, MoveState, PokemonState, Status},
    type_chart::get_type_multiplier,
};

pub const DEFAULT_ROLL_MULTIPLIER: f64 = 0.925;

impl PokemonState {
    pub fn effective_speed(&self) -> i32 {
        let mut speed = get_boosted_stat(self.speed, self.boosts.speed);
        if self.status == Status::Par {
            speed /= 2;
        }
        if self.item == Item::ChoiceScarf {
            speed = speed * 3 / 2;
        }
        speed
    }

    pub fn end_of_turn_hp(&self) -> f64 {
        if self.item == Item::Leftovers && self.hp_percent > 0.0 {
            f64::min(1.0, self.hp_percent + (1.0 / 16.0))
        } else {
            self.hp_percent
        }
    }
}

pub fn get_damage_percent(
    attacker: &PokemonState,
    defender: &PokemonState,
    move_state: &MoveState,
    roll_multiplier: f64,
) -> f64 {
    if move_state.category == Category::Status {
        return 0.0;
    }

    let mut type_multiplier = 1.0;
    for defender_type in defender.types.iter() {
        type_multiplier *= get_type_multiplier(*defender_type, move_state.move_type);
    }
    if type_multiplier == 0.0 {
        return 0.0;
    }

    if let Some(fixed_damage) = get_fixed_damage_percent(attacker, defender, move_state) {
        return fixed_damage;
    }

    let base_power = get_base_power(attacker, defender, move_state);
    if base_power == 0 {
        return 0.0;
    }

    let (attack, defense) = get_attack_and_defense(attacker, defender, move_state.category);
    let mut base = ((2 * attacker.level) / 5 + 2) * base_power * attack / i32::max(1, defense);
    base = base / 50 + 2;

    let stab = if attacker.types.contains(&move_state.move_type) {
        1.5
    } else {
        1.0
    };

    let mut damage = ((base as f64) * roll_multiplier * stab * type_multiplier) as i32;
    if attacker.item == Item::LifeOrb {
        damage = damage * 13 / 10;
    }

    (damage as f64) / (defender.max_hp as f64)
}

fn get_fixed_damage_percent(attacker: &PokemonState, defender: &PokemonState, move_state: &MoveState) -> Option<f64> {
    match move_state.id.as_str() {
        "seismictoss" | "nightshade" => Some((attacker.level as f64) / (defender.max_hp as f64)),
        "superfang" | "ruination" => Some(defender.hp_percent / 2.0),
        "endeavor" => {
            let hp_difference =
                defender.hp_percent * (defender.max_hp as f64) - attacker.hp_percent * (attacker.max_hp as f64);
            let calculated = f64::max(0.0, hp_difference) / (defender.max_hp as f64);
            Some(calculated)
        }
        _ => None,
    }
}

fn get_base_power(attacker: &PokemonState, defender: &PokemonState, move_state: &MoveState) -> i32 {
    match move_state.id.as_str() {
        "lowkick" | "grassknot" | "heavyslam" | "heatcrash" => 60,
        "eruption" | "waterspout" | "dragonenergy" => {
            let calculated = (move_state.base_power as f64) * attacker.hp_percent;
            i32::max(1, calculated as i32)
        }
        "hex" if defender.status != Status::None => move_state.base_power * 2,
        "acrobatics" if attacker.item == Item::NoItem => move_state.base_power * 2,
        _ => move_state.base_power,
    }
}

fn get_attack_and_defense(attacker: &PokemonState, defender: &PokemonState, category: Category) -> (i32, i32) {
    let mut attack: i32;
    let mut defense: i32;

    if category == Category::Physical {
        attack = get_boosted_stat(attacker.attack, attacker.boosts.attack);
        defense = get_boosted_stat(defender.defense, defender.boosts.defense);

        if attacker.status == Status::Brn {
            attack /= 2;
        }
        if attacker.item == Item::ChoiceBand {
            attack = attack * 3 / 2;
        }
    } else {
        attack = get_boosted_stat(attacker.special_attack, attacker.boosts.special_attack);
        defense = get_boosted_stat(defender.special_defense, defender.boosts.special_defense);
        if category == Category::Special && attacker.item == Item::ChoiceSpecs {
            attack = attack * 3 / 2;
        }
    }
    if defender.item == Item::Eviolite || (category == Category::Special && defender.item == Item::AssaultVest) {
        defense = defense * 3 / 2;
    }

    (attack, defense)
}

fn get_boosted_stat(value: i32, boost: i32) -> i32 {
    if boost >= 0 {
        value * (2 + boost) / 2
    } else {
        value * 2 / (2 - boost)
    }
}
