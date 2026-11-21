use std::{mem::replace, sync::Arc};

use crate::{
    mechanics::{DEFAULT_ROLL_MULTIPLIER, get_damage_percent},
    state::{Action, Boosts, GameState, Item, MoveState, PokemonState},
};

impl Boosts {
    pub fn with_change(&self, other: Boosts) -> Boosts {
        let clamp = |b| i32::clamp(b, -6, 6);
        Boosts {
            attack: clamp(self.attack + other.attack),
            defense: clamp(self.defense + other.defense),
            special_attack: clamp(self.special_attack + other.special_attack),
            special_defense: clamp(self.special_defense + other.special_defense),
            speed: clamp(self.speed + other.speed),
        }
    }
}

impl PokemonState {
    pub fn usable_move_indices(&self) -> Vec<usize> {
        if let Some(index) = self.locked_move {
            vec![index]
        } else {
            (0..self.moves.len()).collect()
        }
    }

    pub fn is_fainted(&self) -> bool {
        self.hp_percent <= 0.0
    }

    pub fn reset_on_switch(&mut self) {
        self.boosts = Boosts::default();
        self.locked_move = None;
    }

    pub fn end_turn(&mut self) {
        self.hp_percent = self.end_of_turn_hp()
    }
}

impl GameState {
    pub fn friendly_actions(&self) -> Vec<Action> {
        let usable_move_indices = self.friendly_pokemon.usable_move_indices();
        let moves = usable_move_indices.iter().map(|&index| Action {
            is_switch: false,
            index,
        });
        let switches = self
            .friendly_bench
            .iter()
            .enumerate()
            .filter(|(_, state)| !state.is_fainted())
            .map(|(index, _)| Action { is_switch: true, index });
        moves.chain(switches).collect()
    }

    pub fn has_anyone_fainted(&self) -> bool {
        self.friendly_pokemon.is_fainted() || self.opponent_pokemon.is_fainted()
    }

    pub fn end_turn(&mut self) {
        self.friendly_pokemon.end_turn();
        self.opponent_pokemon.end_turn();
    }

    pub fn attacker_defender_mut(&mut self, friendly_attacking: bool) -> (&mut PokemonState, &mut PokemonState) {
        if friendly_attacking {
            (&mut self.friendly_pokemon, &mut self.opponent_pokemon)
        } else {
            (&mut self.opponent_pokemon, &mut self.friendly_pokemon)
        }
    }
}

pub fn simulate_turn(state: &GameState, friendly_action: Action, opponent_move_index: usize) -> Vec<(f64, GameState)> {
    let mut outcomes = if friendly_action.is_switch {
        let switched_state = simulate_switch(state, friendly_action.index);
        simulate_move(&switched_state, opponent_move_index, false)
    } else {
        let friendly_move = &state.friendly_pokemon.moves[friendly_action.index];
        let opponent_move = &state.opponent_pokemon.moves[opponent_move_index];
        let friendly_first_chance = get_friendly_first_chance(state, friendly_move, opponent_move);

        let mut outcomes: Vec<(f64, GameState)> = vec![];
        for (order_probability, friendly_first) in [(friendly_first_chance, true), (1.0 - friendly_first_chance, false)]
        {
            if order_probability <= 0.0 {
                continue;
            }

            let (first_index, second_index) = if friendly_first {
                (friendly_action.index, opponent_move_index)
            } else {
                (opponent_move_index, friendly_action.index)
            };

            for (first_probability, first_state) in simulate_move(state, first_index, friendly_first) {
                let branch_probability = order_probability * first_probability;
                if first_state.has_anyone_fainted() {
                    outcomes.push((branch_probability, first_state));
                    continue;
                }

                for (second_probability, second_state) in simulate_move(&first_state, second_index, !friendly_first) {
                    outcomes.push((branch_probability * second_probability, second_state));
                }
            }
        }
        outcomes
    };

    for (_, next_state) in &mut outcomes {
        next_state.end_turn();
    }
    outcomes
}

pub fn simulate_switch(state: &GameState, bench_index: usize) -> GameState {
    let mut bench = state.friendly_bench.to_vec();
    let mut current_active = state.friendly_pokemon.clone();
    current_active.reset_on_switch();
    let new_active = replace(&mut bench[bench_index], current_active);
    GameState {
        friendly_pokemon: new_active,
        opponent_pokemon: state.opponent_pokemon.clone(),
        friendly_bench: bench.into(),
    }
}

fn get_friendly_first_chance(state: &GameState, friendly_move: &MoveState, opponent_move: &MoveState) -> f64 {
    if friendly_move.priority > opponent_move.priority {
        return 1.0;
    } else if friendly_move.priority < opponent_move.priority {
        return 0.0;
    }

    let friendly_speed = state.friendly_pokemon.effective_speed();
    let opponent_speed = state.opponent_pokemon.effective_speed();
    if friendly_speed > opponent_speed {
        return 1.0;
    } else if friendly_speed < opponent_speed {
        return 0.0;
    }

    0.5
}

fn simulate_move(state: &GameState, move_index: usize, friendly_attacking: bool) -> Vec<(f64, GameState)> {
    let mut possibilities = vec![];
    let mut next_state = state.clone();

    let (attacker, _defender) = next_state.attacker_defender_mut(friendly_attacking);
    let moves = Arc::clone(&attacker.moves);
    let move_state = &moves[move_index];
    if [Item::ChoiceBand, Item::ChoiceScarf, Item::ChoiceSpecs].contains(&attacker.item) {
        attacker.locked_move = Some(move_index);
    }

    if move_state.accuracy < 1.0 {
        possibilities.push((1.0 - move_state.accuracy, next_state.clone()));
    }

    let (attacker, defender) = next_state.attacker_defender_mut(friendly_attacking);
    let damage_percent = get_damage_percent(attacker, defender, move_state, DEFAULT_ROLL_MULTIPLIER);
    let damage_dealt = damage_percent.min(defender.hp_percent);
    defender.hp_percent -= damage_dealt;

    let damage_hp = damage_dealt * (defender.max_hp as f64);
    let hp_change = move_state.heal + (move_state.drain - move_state.recoil) * damage_hp / (attacker.max_hp as f64);
    attacker.hp_percent = if move_state.self_destruct {
        0.0
    } else {
        (attacker.hp_percent + hp_change).clamp(0.0, 1.0)
    };
    attacker.boosts = attacker.boosts.with_change(move_state.self_boosts);

    possibilities.push((move_state.accuracy, next_state));
    possibilities
}
