use monte::datasets::{download_dataset, DownloadableDataset};
// use polars::prelude::*;
use std::error::Error;

fn main() -> Result<(), Box<dyn Error>> {
    let df = download_dataset(DownloadableDataset::EEG)?;

    dbg!(df);

    Ok(())
}
