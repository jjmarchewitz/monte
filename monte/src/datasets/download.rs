mod diabetes;
mod eeg;
mod ilpd;
mod pc4;
mod phoneme;

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

pub fn download_dataset(dataset: DownloadableDataset) -> Result<DataFrame, Box<dyn Error>> {
    match dataset {
        DownloadableDataset::Diabetes => diabetes::DiabetesRecord::download_into_df(),
        DownloadableDataset::EEG => eeg::EEGRecord::download_into_df(),
        DownloadableDataset::ILPD => ilpd::ILPDRecord::download_into_df(),
        DownloadableDataset::PC4 => pc4::PC4Record::download_into_df(),
        DownloadableDataset::Phoneme => phoneme::PhonemeRecord::download_into_df(),
    }
}
