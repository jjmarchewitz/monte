#![doc = include_str!("../../../../datasets/airfoil_noise/README.md")]

use download_into_dataframe::DownloadIntoDataframe;
use polars::prelude::*;
use serde::Deserialize;

#[derive(Deserialize, Debug, DownloadIntoDataframe)]
#[download_into_dataframe(
    url = "https://raw.githubusercontent.com/monte-rs/monte-datasets/main/airfoil_noise/airfoil_noise.json"
)]
pub struct AirfoilNoiseRecord {
    freq: Option<i32>,
    angle: Option<f32>,
    chord_length: Option<f32>,
    vel: Option<f32>,
    disp: Option<f32>,
    target: Option<f32>,
}
