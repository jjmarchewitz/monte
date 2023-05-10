use darling::FromDeriveInput;
// use proc_macro2::TokenStream;
use quote::quote;
use syn::{parse_macro_input, Data, DataStruct, DeriveInput, Fields};

#[derive(Debug, FromDeriveInput)]
#[darling(attributes(download_url))]
struct DownloadIntoDataframeOpts {
    url: String,
}

#[proc_macro_derive(DownloadIntoDataframe, attributes(download_url))]
pub fn download_into_dataframe(input: proc_macro::TokenStream) -> proc_macro::TokenStream {
    // let input = TokenStream::from(input);
    let input = parse_macro_input!(input as DeriveInput);

    //

    //

    //

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

    let field_vec_declarations = fields.iter().map(|field| {
        let ident = &field.ident;
        let ty = &field.ty;

        quote! { let mut #ident = Vec::<#ty>::new(); }
    });

    let push_into_field_vecs = fields.iter().map(|field| {
        let ident = &field.ident;

        quote! { #ident.push(record.#ident); }
    });

    let vec_to_series = fields.iter().map(|field| {
        let ident = &field.ident;

        quote! { let #ident = ::polars::prelude::Series::new(stringify!(#ident), #ident); }
    });

    let series_names = fields.iter().map(|field| {
        let ident = &field.ident;

        quote! { #ident }
    });

    quote! {
        impl ::monte_core::traits::DownloadIntoDataframe for #struct_name {

            type DataFrame = ::polars::frame::DataFrame;

            fn download_into_df() -> Result<Self::DataFrame, Box<dyn std::error::Error>> {
                let response = ::reqwest::blocking::get(#url)?.text()?;

                let record_data: Vec<#struct_name> = ::serde_json::from_str(&response)?;

                #(#field_vec_declarations)*

                for record in record_data.into_iter() {
                    #(#push_into_field_vecs)*
                }

                #(#vec_to_series)*

                let df = ::polars::prelude::DataFrame::new(vec![
                    #(#series_names),*
                ])?;

                Ok(df)
            }
        }
    }
    .into()
}
