# Standards for the monte project

## Development

* Performance is key
  * Use LRU caches when possible
  * Use rayon when possible
* Ease of use is key
  * All learning models need to automatically handle any number of input features
  * !!! All learning models only take in frames (keep this?)
  * Lean into the language you're using. The core library should use Rust idioms, and the APIs should use the idioms from their respective languages
* Use structs to handle functions having lots of options
  * The Python API can convert the provided args and kwargs into an options struct
* Custom error types
  * thiserror?
* Use good traits
  * Serde, Default, From, TryFrom, Clone/Copy
* Use features to toggle sections of the code base
  * Any non-rust language should enable all features since we're serving a precompiled binary

## Testing

* Research stuff
  * Proptest
  * Hypothesis

## Documentation

* API reference in every language
* One user guide with tabs for code examples in every language

## Releases

* Major versions should be the same across all languages
  * Minor versions may differ so that bug fixes/minor updates can be released for each language independently
