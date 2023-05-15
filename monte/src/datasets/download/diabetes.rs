use download_into_dataframe::DownloadIntoDataframe;
use polars::prelude::*;
use serde::Deserialize;

#[derive(Deserialize, Debug, DownloadIntoDataframe)]
#[download_into_dataframe(
    url = "https://raw.githubusercontent.com/monte-rs/monte-datasets/main/diabetes/diabetes.json"
)]
pub struct DiabetesRecord {
    id: i32,
    preg: Option<i32>,
    plas: Option<i32>,
    pres: Option<i32>,
    skin: Option<i32>,
    insu: Option<i32>,
    mass: Option<f32>,
    pedi: Option<f32>,
    age: Option<i32>,
    class: Option<i32>,
}
