use download_into_dataframe::DownloadIntoDataframe;
use polars::prelude::*;
use serde::Deserialize;

#[derive(Deserialize, Debug, DownloadIntoDataframe)]
#[download_into_dataframe(
    url = "https://raw.githubusercontent.com/monte-rs/monte-datasets/main/ilpd/ilpd.json"
)]
pub struct ILPDRecord {
    id: i32,
    #[serde(alias = "V1")]
    v1: Option<f32>,
    #[serde(alias = "V2")]
    v2: Option<String>,
    #[serde(alias = "V3")]
    v3: Option<f32>,
    #[serde(alias = "V4")]
    v4: Option<f32>,
    #[serde(alias = "V5")]
    v5: Option<f32>,
    #[serde(alias = "V6")]
    v6: Option<f32>,
    #[serde(alias = "V7")]
    v7: Option<f32>,
    #[serde(alias = "V8")]
    v8: Option<f32>,
    #[serde(alias = "V9")]
    v9: Option<f32>,
    #[serde(alias = "V10")]
    v10: Option<f32>,
    #[serde(alias = "Class")]
    class: i32,
}