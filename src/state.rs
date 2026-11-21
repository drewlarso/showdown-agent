use std::sync::Arc;

use pyo3::pyclass;
use serde::Deserialize;

use crate::type_chart::Type;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "UPPERCASE")]
pub enum Category {
    Physical,
    Special,
    Status,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "UPPERCASE")]
pub enum Status {
    Brn,
    Fnt,
    Frz,
    Par,
    Psn,
    Slp,
    Tox,
    #[serde(rename = "")]
    None,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Item {
    ChoiceBand,
    ChoiceScarf,
    ChoiceSpecs,
    AssaultVest,
    Eviolite,
    Leftovers,
    LifeOrb,
    #[serde(rename = "")]
    NoItem,
    #[serde(other)]
    Other,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize, Default)]
pub struct Boosts {
    #[serde(rename = "atk")]
    #[serde(default)]
    pub attack: i32,
    #[serde(default)]
    pub defense: i32,
    #[serde(rename = "spa")]
    #[serde(default)]
    pub special_attack: i32,
    #[serde(rename = "spd")]
    #[serde(default)]
    pub special_defense: i32,
    #[serde(rename = "spe")]
    #[serde(default)]
    pub speed: i32,
}

#[derive(Debug, Clone, Deserialize)]
pub struct MoveState {
    pub id: Arc<String>,
    pub base_power: i32,
    pub move_type: Type,
    pub category: Category,
    pub priority: i32,
    pub accuracy: f64,
    pub prior: f64,
    #[serde(default)]
    pub heal: f64,
    #[serde(default)]
    pub drain: f64,
    #[serde(default)]
    pub recoil: f64,
    #[serde(default)]
    pub self_destruct: bool,
    #[serde(default)]
    pub self_boosts: Boosts,
}

#[derive(Debug, Clone, Deserialize)]
pub struct PokemonState {
    pub level: i32,
    pub hp_percent: f64,
    pub max_hp: i32,
    #[serde(rename = "atk")]
    pub attack: i32,
    pub defense: i32,
    #[serde(rename = "spa")]
    pub special_attack: i32,
    #[serde(rename = "spd")]
    pub special_defense: i32,
    #[serde(rename = "spe")]
    pub speed: i32,
    pub boosts: Boosts,
    pub status: Status,
    pub item: Item,
    pub types: Arc<[Type]>,
    pub moves: Arc<[MoveState]>,
    #[serde(default)]
    pub locked_move: Option<usize>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct GameState {
    pub friendly_pokemon: PokemonState,
    pub opponent_pokemon: PokemonState,
    pub friendly_bench: Arc<[PokemonState]>,
}

#[pyclass(module = "agent._core", frozen)]
#[derive(Debug, Clone, Copy, Deserialize)]
pub struct Action {
    #[pyo3(get)]
    pub is_switch: bool,
    #[pyo3(get)]
    pub index: usize,
}
