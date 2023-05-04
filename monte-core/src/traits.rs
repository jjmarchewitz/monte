use polars::frame::DataFrame;
use std::error::Error;

pub trait Downloadable {
    fn get_url() -> &'static str;
}

pub trait DownloadAsDataframe {
    fn get_as_dataframe() -> Result<DataFrame, Box<dyn Error>>;
}
