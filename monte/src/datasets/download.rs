mod diabetes;

use polars::frame::DataFrame;
use std::error::Error;

pub enum Dataset {
    Diabetes,
    EEG,
    ILPD,
    PC4,
    Phoneme,
}

// TODO: should this be a method or a separate function?
pub fn get(dataset: Dataset) -> Result<DataFrame, Box<dyn Error>> {
    match dataset {
        Dataset::Diabetes => diabetes::get_as_dataframe(),
        _ => todo!(),
    }
}
