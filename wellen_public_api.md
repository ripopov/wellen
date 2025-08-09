# Wellen Crate Public API

The `wellen` crate is a Rust library for reading and processing waveform files (VCD, FST, GHW formats). Below is the complete public API exported from the crate.

## Constants

- `VERSION: &str` - Cargo.toml version of this library

## Core Types and Enums

### File Format and Loading
- `FileFormat` - Enum with variants: `Vcd`, `Fst`, `Ghw`, `Unknown`
- `LoadOptions` - Struct with options for loading waveforms:
  - `multi_thread: bool` - Use multiple threads if possible
  - `remove_scopes_with_empty_name: bool` - Remove scopes with empty names from hierarchy
- `WellenError` - Error enum for waveform loading failures
- `Result<T>` - Type alias for `std::result::Result<T, WellenError>`

### Time and Signal References
- `Time` - Type alias for `u64` representing time values
- `TimeTable` - Type alias for `Vec<Time>`
- `TimeTableIdx` - Type alias for `u32` for indexing into time tables
- `Real` - Type alias for `f64` for real number signal values

### Signal References and Encoding
- `SignalRef` - Reference to a signal in the hierarchy
- `SignalEncoding` - Enum describing signal encoding:
  - `String` - String signals
  - `Real` - Real number signals  
  - `BitVector(NonZeroU32)` - Bit vector signals with specified width

### Hierarchy Types
- `Hierarchy` - Main container for waveform hierarchy and metadata
- `Scope` - Represents a scope in the hierarchy
- `ScopeRef` - Reference to a scope
- `ScopeType` - Enum with scope types (Module, Task, Function, Begin, Fork, Generate, etc.)
- `ScopeOrVar<'a>` - Enum that can hold either a scope or variable reference
- `ScopeOrVarRef` - Reference version of ScopeOrVar
- `Var` - Represents a variable/signal in the hierarchy
- `VarRef` - Reference to a variable
- `VarType` - Enum with variable types (Event, Integer, Real, Reg, Wire, etc.)
- `VarDirection` - Enum with signal directions (Input, Output, InOut, etc.)
- `VarIndex` - Represents array indices for variables
- `Timescale` - Represents simulation timescale
- `TimescaleUnit` - Enum with time units (Seconds, MilliSeconds, etc.)

### Signal Data
- `Signal` - Contains actual signal data and change information
- `SignalValue<'a>` - Enum representing different signal value types:
  - `Binary(&'a [u8], u32)` - Binary signal data
  - `FourValue(&'a [u8], u32)` - Four-state logic data
  - `NineValue(&'a [u8], u32)` - Nine-state logic data
  - `String(&'a str)` - String signal data
  - `Real(Real)` - Real number signal data
- `SignalSource` - Source for loading signal data

### Compression
- `CompressedSignal` - Compressed version of a Signal
- `CompressedTimeTable` - Compressed version of a TimeTable
- `Compression` - Enum with compression types: `None`, `Lz4(usize)`

## Public Modules

### `simple` Module
High-level interface for batch processing of waveform files.

#### Functions
- `read<P: AsRef<std::path::Path>>(filename: P) -> Result<Waveform>` - Read waveform with default options
- `read_with_options<P: AsRef<std::path::Path>>(filename: P, options: &LoadOptions) -> Result<Waveform>` - Read waveform with custom options
- `read_from_reader<R: BufRead + Seek + Send + Sync + 'static>(input: R) -> Result<Waveform>` - Read from a reader instead of file

#### Types
- `Waveform` - Main waveform container with methods:
  - `hierarchy(&self) -> &Hierarchy` - Get hierarchy reference
  - `time_table(&self) -> &[Time]` - Get time table
  - `load_signals(&mut self, ids: &[SignalRef])` - Load signals (single-threaded)
  - `load_signals_multi_threaded(&mut self, ids: &[SignalRef])` - Load signals (multi-threaded)
  - `unload_signals(&mut self, ids: &[SignalRef])` - Unload signals from memory
  - `get_signal(&self, id: SignalRef) -> Option<&Signal>` - Get loaded signal
  - `print_backend_statistics(&self)` - Print backend statistics

### `viewers` Module
Lower-level interface for waveform viewers with granular control.

#### Types
- `HeaderResult<R: BufRead + Seek>` - Result of reading waveform header
- `ReadBodyContinuation<R: BufRead + Seek>` - Continuation for reading body
- `BodyResult` - Result of reading waveform body
- `ProgressCount` - Type alias for `std::sync::Arc<std::sync::atomic::AtomicU64>`

#### Functions
- `read_header_from_file<P: AsRef<std::path::Path>>(filename: P, options: &LoadOptions) -> Result<HeaderResult<std::io::BufReader<std::fs::File>>>` - Read header from file
- `read_header<R: BufRead + Seek>(input: R, options: &LoadOptions) -> Result<HeaderResult<R>>` - Read header from reader
- `read_body<R: BufRead + Seek + Sync + Send + 'static>(body: ReadBodyContinuation<R>, hierarchy: &Hierarchy, progress: Option<ProgressCount>) -> Result<BodyResult>` - Read waveform body
- `open_and_detect_file_format<P: AsRef<std::path::Path>>(filename: P) -> FileFormat` - Detect file format from file
- `detect_file_format(input: &mut (impl BufRead + Seek)) -> FileFormat` - Detect file format from reader

## Optional Features

### `serde1` Feature
When enabled, adds serde serialization support to:
- `FileFormat`
- `LoadOptions` 
- `CompressedSignal`
- `CompressedTimeTable`
- `Compression`

### `benchmark` Feature
When enabled, exposes additional internal functions for benchmarking:
- `check_states_pub` from the `wavemem` module

## Key Methods on Public Types

### `Signal` Methods
- `iter_changes(&self) -> SignalChangeIterator<'_>` - Iterator over signal changes
- `signal_ref(&self) -> SignalRef` - Get signal reference
- `signal_encoding(&self) -> SignalEncoding` - Get signal encoding
- `time_indices(&self) -> &[TimeTableIdx]` - Get time indices for changes

### `SignalValue` Methods
- `to_bit_string(&self) -> Option<String>` - Convert to bit string representation
- `bits(&self) -> Option<u32>` - Get number of bits
- `states(&self) -> Option<States>` - Get states per bit

### `Hierarchy` Methods
- `iter_vars(&self)` - Iterator over variables
- `iter_scopes(&self)` - Iterator over scopes
- `lookup_scope(&self, names: &[N]) -> Option<ScopeRef>` - Find scope by path
- `lookup_var(&self, path: &[N], name: &N) -> Option<VarRef>` - Find variable by path
- `timescale(&self) -> Option<Timescale>` - Get simulation timescale
- `file_format(&self) -> FileFormat` - Get original file format

### `CompressedSignal` Methods
- `compress(signal: &Signal) -> Self` - Compress a signal
- `compress_with_options(signal: &Signal, preserve_duplicates: bool) -> Self` - Compress with options
- `uncompress(&self) -> Signal` - Decompress back to signal

### `CompressedTimeTable` Methods
- `compress(table: &[Time]) -> Self` - Compress time table
- `uncompress(&self) -> Vec<Time>` - Decompress time table

This API provides both high-level (`simple` module) and low-level (`viewers` module) interfaces for working with waveform data, supporting multiple file formats (VCD, FST, GHW) with optional compression and serialization capabilities.