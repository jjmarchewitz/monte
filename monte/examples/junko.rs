use monte::datasets::{get_dataset, DownloadableDataset};
// use polars::prelude::*;
use std::error::Error;

fn main() -> Result<(), Box<dyn Error>> {
    let df = get_dataset(DownloadableDataset::Concrete)?;

    dbg!(df);

    Ok(())
}
