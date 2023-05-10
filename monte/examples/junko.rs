use monte::datasets::{download_dataset, Downloadable};
// use polars::prelude::*;
use std::error::Error;

fn main() -> Result<(), Box<dyn Error>> {
    let df = download_dataset(Downloadable::EEG)?;

    dbg!(df);

    Ok(())
}
