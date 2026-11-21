use pyo3::pyclass;

use crate::{
    mechanics::{DEFAULT_ROLL_MULTIPLIER, get_damage_percent},
    simulate::{simulate_switch, simulate_turn},
    state::{Action, GameState, PokemonState},
};

const ALIVE_BONUS: f64 = 0.5;
const DAMAGE_FLOOR: f64 = 0.05;

impl GameState {
    fn value(&self) -> f64 {
        let mut friendly_value = self.friendly_pokemon.value();
        for pokemon_state in self.friendly_bench.iter() {
            friendly_value += pokemon_state.value();
        }
        friendly_value - self.opponent_pokemon.value()
    }
}

impl PokemonState {
    fn value(&self) -> f64 {
        if self.hp_percent <= 0.0 {
            0.0
        } else {
            self.hp_percent + ALIVE_BONUS
        }
    }
}

#[pyclass(module = "agent._core", frozen)]
#[derive(Debug)]
pub struct SearchResult {
    #[pyo3(get)]
    action: Option<Action>,
    #[pyo3(get)]
    action_values: Vec<(Action, f64)>,
    #[pyo3(get)]
    nodes_processed: i64,
}

pub fn get_best_action(state: &GameState, depth: i8) -> SearchResult {
    let mut nodes_processed = 0;
    let action_values = get_action_values(state, depth, &mut nodes_processed);

    let mut best_action = None;
    let mut best_value = f64::NEG_INFINITY;
    for &(action, value) in &action_values {
        if value > best_value {
            best_action = Some(action);
            best_value = value;
        }
    }

    SearchResult {
        action: best_action,
        action_values,
        nodes_processed,
    }
}

fn get_action_values(state: &GameState, depth: i8, nodes_processed: &mut i64) -> Vec<(Action, f64)> {
    let mut action_values = vec![];

    for action in state.friendly_actions() {
        let value = if action.is_switch && state.friendly_pokemon.hp_percent <= 0.0 {
            let switched_state = simulate_switch(state, action.index);
            max_node(&switched_state, depth, nodes_processed)
        } else {
            chance_node(state, action, depth, nodes_processed)
        };

        action_values.push((action, value));
    }

    action_values
}

fn chance_node(state: &GameState, friendly_action: Action, depth: i8, nodes_processed: &mut i64) -> f64 {
    let mut weighted_value = 0.0;
    let mut total_weight = 0.0;

    let opponent = &state.opponent_pokemon;
    for opponent_move_index in opponent.usable_move_indices() {
        let opponent_move = &opponent.moves[opponent_move_index];
        let damage = get_damage_percent(
            opponent,
            &state.friendly_pokemon,
            opponent_move,
            DEFAULT_ROLL_MULTIPLIER,
        );
        let move_weight = opponent_move.prior * (damage + DAMAGE_FLOOR);

        for (probability, next_state) in simulate_turn(state, friendly_action, opponent_move_index) {
            let next_value = max_node(&next_state, depth - 1, nodes_processed);
            weighted_value += move_weight * probability * next_value;
        }

        total_weight += move_weight;
    }

    debug_assert!(total_weight > 0.0);
    weighted_value / total_weight
}

// def chance_node(state: GameState, friendly_action: Action, depth: int, counter: SearchCounter) -> float:
//     weighted_value = 0.0
//     total_weight = 0.0

//     opponent = state.opponent_pokemon
//     for move_index in get_usable_move_indices(opponent):
//         opponent_move = opponent.moves[move_index]
//         damage = get_damage_percent(opponent, state.friendly_pokemon, opponent_move)
//         move_weight = opponent_move.prior * (damage + DAMAGE_FLOOR)

//         for outcome_probability, next_state in simulate_turn(state, friendly_action, move_index):
//             next_value = max_node(next_state, depth - 1, counter)
//             weighted_value += move_weight * outcome_probability * next_value

//         total_weight += move_weight

//     assert total_weight > 0
//     return weighted_value / total_weight

fn max_node(state: &GameState, depth: i8, nodes_processed: &mut i64) -> f64 {
    *nodes_processed += 1;

    if depth <= 0 || state.has_anyone_fainted() {
        return state.value();
    }
    let action_values = get_action_values(state, depth, nodes_processed);
    if action_values.is_empty() {
        return state.value();
    }

    action_values
        .iter()
        .map(|(_, value)| *value)
        .fold(f64::NEG_INFINITY, f64::max)
}
