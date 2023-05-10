mod diabetes;
mod eeg;

use monte_core::traits::DownloadIntoDataframe;
use polars::frame::DataFrame;
use std::error::Error;

pub enum DownloadableDataset {
    Diabetes,
    EEG,
    ILPD,
    PC4,
    Phoneme,
}

// TODO: should this be a method or a separate function?
pub fn download_dataset(dataset: DownloadableDataset) -> Result<DataFrame, Box<dyn Error>> {
    match dataset {
        DownloadableDataset::Diabetes => diabetes::DiabetesRecord::download_into_df(),
        DownloadableDataset::EEG => eeg::EEGRecord::download_into_df(),
        _ => todo!(),
    }
}
