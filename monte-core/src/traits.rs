use polars::frame::DataFrame;
use std::error::Error;

pub trait DownloadUrl {
    fn get_url() -> &'static str;
}

pub trait DownloadIntoDataframe: DownloadUrl {
    fn get_as_dataframe() -> Result<DataFrame, Box<dyn Error>>;
}
