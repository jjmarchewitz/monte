//! Constants
//! scipy constants https://docs.scipy.org/doc/scipy/reference/constants.html
//! a shitload of constants https://physics.nist.gov/cuu/Constants/index.html

pub mod double_precision;
mod single_precision;

// Re-export the single precision constants as default (f32)
pub use single_precision::*;
