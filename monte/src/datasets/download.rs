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

// impl Dataset {
//     fn get_url(&self) -> String {
//         match self {
//             Dataset::Diabetes => "https://raw.githubusercontent.com/monte-rs/monte-datasets/main/diabetes/diabetes.csv".to_owned(),
//             Dataset::EEG => "https://raw.githubusercontent.com/monte-rs/monte-datasets/main/eeg/eeg.csv".to_owned(),
//             Dataset::ILPD => "https://raw.githubusercontent.com/monte-rs/monte-datasets/main/ilpd/ilpd.csv".to_owned(),
//             Dataset::PC4 => "https://raw.githubusercontent.com/monte-rs/monte-datasets/main/pc4/pc4.csv".to_owned(),
//             Dataset::Phoneme => "https://raw.githubusercontent.com/monte-rs/monte-datasets/main/phoneme/phoneme.csv".to_owned(),
//         }
//     }
// }

// TODO: should this be a method or a separate function?
pub fn get(dataset: Dataset) -> Result<DataFrame, Box<dyn Error>> {
    match dataset {
        Dataset::Diabetes => diabetes::get_as_dataframe(),
        _ => todo!(),
    }
}
