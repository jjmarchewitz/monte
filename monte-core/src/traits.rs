// use polars::prelude::DataFrame;
// use std::error::Error;

pub trait DownloadIntoDataframe {
    type DataFrame;
    fn download_into_df() -> Result<Self::DataFrame, Box<dyn std::error::Error>>;
}
