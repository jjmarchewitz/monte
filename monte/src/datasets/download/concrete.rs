use download_into_dataframe::DownloadIntoDataframe;
use polars::prelude::*;
use serde::Deserialize;

#[derive(Deserialize, Debug, DownloadIntoDataframe)]
#[download_into_dataframe(
    url = "https://raw.githubusercontent.com/monte-rs/monte-datasets/main/concrete/concrete.json"
)]
pub struct ConcreteRecord {
    #[serde(alias = "Cement (component 1)(kg in a m^3 mixture)")]
    cement: Option<f32>,
    #[serde(alias = "Blast Furnace Slag (component 2)(kg in a m^3 mixture)")]
    slag: Option<f32>,
    #[serde(alias = "Fly Ash (component 3)(kg in a m^3 mixture)")]
    fly_ash: Option<f32>,
    #[serde(alias = "Water  (component 4)(kg in a m^3 mixture)")]
    water: Option<f32>,
    #[serde(alias = "Superplasticizer (component 5)(kg in a m^3 mixture)")]
    superplasticizer: Option<f32>,
    #[serde(alias = "Coarse Aggregate  (component 6)(kg in a m^3 mixture)")]
    coarse_aggregate: Option<f32>,
    #[serde(alias = "Fine Aggregate (component 7)(kg in a m^3 mixture)")]
    fine_aggregate: Option<f32>,
    #[serde(alias = "Age (day)")]
    age: Option<i32>,
    #[serde(alias = "Concrete compressive strength(MPa, megapascals)")]
    target: Option<f32>,
}
