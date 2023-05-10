use download_into_dataframe::DownloadIntoDataframe;
use polars::prelude::*;
use serde::Deserialize;

#[derive(Deserialize, Debug, DownloadIntoDataframe)]
#[download_url(url = "https://raw.githubusercontent.com/monte-rs/monte-datasets/main/pc4/pc4.json")]
pub struct PC4Record {
    id: i32,
    #[serde(alias = "LOC_BLANK")]
    loc_blank: Option<i32>,
    #[serde(alias = "BRANCH_COUNT")]
    branch_count: Option<i32>,
    #[serde(alias = "CALL_PAIRS")]
    call_pairs: Option<i32>,
    #[serde(alias = "LOC_CODE_AND_COMMENT")]
    loc_code_and_comment: Option<i32>,
    #[serde(alias = "LOC_COMMENTS")]
    loc_comments: Option<i32>,
    #[serde(alias = "CONDITION_COUNT")]
    condition_count: Option<i32>,
    #[serde(alias = "CYCLOMATIC_COMPLEXITY")]
    cyclomatic_complexity: Option<f32>,
    #[serde(alias = "CYCLOMATIC_DENSITY")]
    cyclomatic_density: Option<f32>,
    #[serde(alias = "DECISION_COUNT")]
    decision_count: Option<i32>,
    #[serde(alias = "DECISION_DENSITY")]
    decision_density: Option<f32>,
    #[serde(alias = "DESIGN_COMPLEXITY")]
    design_complexity: Option<i32>,
    #[serde(alias = "DESIGN_DENSITY")]
    design_density: Option<f32>,
    #[serde(alias = "EDGE_COUNT")]
    edge_count: Option<i32>,
    #[serde(alias = "ESSENTIAL_COMPLEXITY")]
    essential_complexity: Option<f32>,
    #[serde(alias = "ESSENTIAL_DENSITY")]
    essential_density: Option<f32>,
    #[serde(alias = "LOC_EXECUTABLE")]
    loc_executable: Option<i32>,
    #[serde(alias = "PARAMETER_COUNT")]
    parameter_count: Option<i32>,
    #[serde(alias = "HALSTEAD_CONTENT")]
    halstead_content: Option<f32>,
    #[serde(alias = "HALSTEAD_DIFFICULTY")]
    halstead_difficulty: Option<f32>,
    #[serde(alias = "HALSTEAD_EFFORT")]
    halstead_effort: Option<f32>,
    #[serde(alias = "HALSTEAD_ERROR_EST")]
    halstead_error_est: Option<f32>,
    #[serde(alias = "HALSTEAD_LENGTH")]
    halstead_length: Option<f32>,
    #[serde(alias = "HALSTEAD_LEVEL")]
    halstead_level: Option<f32>,
    #[serde(alias = "HALSTEAD_PROG_TIME")]
    halstead_prog_time: Option<f32>,
    #[serde(alias = "HALSTEAD_VOLUME")]
    halstead_volume: Option<f32>,
    #[serde(alias = "MAINTENANCE_SEVERITY")]
    maintenance_severity: Option<f32>,
    #[serde(alias = "MODIFIED_CONDITION_COUNT")]
    modified_condition_count: Option<i32>,
    #[serde(alias = "MULTIPLE_CONDITION_COUNT")]
    multiple_condition_count: Option<i32>,
    #[serde(alias = "NODE_COUNT")]
    node_count: Option<i32>,
    #[serde(alias = "NORMALIZED_CYLOMATIC_COMPLEXITY")]
    normalized_cylomatic_complexity: Option<f32>,
    #[serde(alias = "NUM_OPERANDS")]
    num_operands: Option<i32>,
    #[serde(alias = "NUM_OPERATORS")]
    num_operators: Option<i32>,
    #[serde(alias = "NUM_UNIQUE_OPERANDS")]
    num_unique_operands: Option<i32>,
    #[serde(alias = "NUM_UNIQUE_OPERATORS")]
    num_unique_operators: Option<i32>,
    #[serde(alias = "NUMBER_OF_LINES")]
    number_of_lines: Option<i32>,
    #[serde(alias = "PERCENT_COMMENTS")]
    percent_comments: Option<f32>,
    #[serde(alias = "LOC_TOTAL")]
    loc_total: Option<i32>,
    c: Option<String>,
}
