use darling::FromDeriveInput;
use quote::quote;
use syn::{parse_macro_input, Data, DataStruct, DeriveInput, Fields};

#[derive(Debug, FromDeriveInput)]
#[darling(attributes(download_into_dataframe))]
struct DownloadIntoDataframeOpts {
    url: String,
}

#[proc_macro_derive(DownloadIntoDataframe, attributes(download_into_dataframe))]
pub fn download_into_dataframe(input: proc_macro::TokenStream) -> proc_macro::TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    let opts = DownloadIntoDataframeOpts::from_derive_input(&input).expect("Wrong options"); // TODO: err msg

    let url = opts.url;
    let url = quote! { #url };

    let struct_name = &input.ident;

    let fields = match &input.data {
        Data::Struct(DataStruct {
            fields: Fields::Named(fields),
            ..
        }) => &fields.named,
        _ => panic!("Expected a struct with named fields"),
    };

    let column_vec_declarations = fields.iter().map(|field| {
        let ident = &field.ident;
        let ty = &field.ty;

        quote! { let mut #ident = Vec::<#ty>::new(); }
    });

    let push_json_data_into_column_vecs = fields.iter().map(|field| {
        let ident = &field.ident;

        quote! { #ident.push(record.#ident); }
    });

    let convert_column_vecs_to_series = fields.iter().map(|field| {
        let ident = &field.ident;

        quote! { let #ident = ::polars::series::Series::new(stringify!(#ident), #ident); }
    });

    let series_names = fields.iter().map(|field| {
        let ident = &field.ident;

        quote! { #ident }
    });

    // Final trait implementation
    quote! {
        impl ::monte_core::traits::DownloadIntoDataframe for #struct_name {
            fn download_into_df() -> Result<::polars::frame::DataFrame, Box<dyn std::error::Error>> {
                let response = ::reqwest::blocking::get(#url)?.text()?;

                let json_record_data: Vec<#struct_name> = ::serde_json::from_str(&response)?;

                #(#column_vec_declarations)*

                for record in json_record_data.into_iter() {
                    #(#push_json_data_into_column_vecs)*
                }

                #(#convert_column_vecs_to_series)*

                let df = ::polars::frame::DataFrame::new(vec![
                    #(#series_names),*
                ])?;

                Ok(df)
            }
        }
    }
    .into()
}
