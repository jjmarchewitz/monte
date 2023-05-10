use download_into_dataframe::DownloadIntoDataframe;
use polars::prelude::*;
use serde::Deserialize;

#[derive(Deserialize, Debug, DownloadIntoDataframe)]
#[download_url(
    url = "https://raw.githubusercontent.com/monte-rs/monte-datasets/main/phoneme/phoneme.json"
)]
pub struct PhonemeRecord {
    id: i32,
    #[serde(alias = "V1")]
    v1: Option<f32>,
    #[serde(alias = "V2")]
    v2: Option<f32>,
    #[serde(alias = "V3")]
    v3: Option<f32>,
    #[serde(alias = "V4")]
    v4: Option<f32>,
    #[serde(alias = "V5")]
    v5: Option<f32>,
    #[serde(alias = "Class")]
    class: i32,
}
