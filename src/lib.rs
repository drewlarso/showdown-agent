use pyo3::prelude::*;

mod mechanics;
mod search;
mod simulate;
mod state;
mod type_chart;

#[pymodule]
mod _core {
    #[pymodule_export]
    use crate::search::SearchResult;
    #[pymodule_export]
    use crate::state::Action;

    use pyo3::{exceptions::PyValueError, prelude::*};

    use crate::{search::get_best_action, state::GameState};

    #[pyfunction]
    fn search_rust(state_json: String, depth: i8) -> PyResult<SearchResult> {
        let state: GameState =
            serde_json::from_str(&state_json).map_err(|e| PyValueError::new_err(format!("Invalid state JSON: {e}")))?;
        let opponent_moves = &state.opponent_pokemon.moves;
        if opponent_moves.is_empty() || opponent_moves.iter().any(|m| m.prior <= 0.0) {
            return Err(PyValueError::new_err(
                "opponent needs at least one move and all priors must be positive",
            ));
        }

        Ok(get_best_action(&state, depth))
    }
}
