use monte::datasets::download;
// use polars::prelude::*;
use std::error::Error;

fn main() -> Result<(), Box<dyn Error>> {
    let df = download::get(download::Dataset::Diabetes)?;

    dbg!(df);

    Ok(())
}
