mod diabetes;
mod eeg;
mod ilpd;
mod pc4;
mod phoneme;

use monte_core::traits::DownloadIntoDataframe;
use polars::frame::DataFrame;
use std::error::Error;

pub enum Downloadable {
    Diabetes,
    EEG,
    ILPD,
    PC4,
    Phoneme,
}

pub fn download_dataset(dataset: Downloadable) -> Result<DataFrame, Box<dyn Error>> {
    match dataset {
        Downloadable::Diabetes => diabetes::DiabetesRecord::download_into_df(),
        Downloadable::EEG => eeg::EEGRecord::download_into_df(),
        Downloadable::ILPD => ilpd::ILPDRecord::download_into_df(),
        Downloadable::PC4 => pc4::PC4Record::download_into_df(),
        Downloadable::Phoneme => phoneme::PhonemeRecord::download_into_df(),
    }
}
