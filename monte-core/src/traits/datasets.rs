pub trait DownloadIntoDataframe {
    fn download_into_df() -> Result<::polars::frame::DataFrame, Box<dyn std::error::Error>>;
}
