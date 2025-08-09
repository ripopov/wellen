# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Wellen is a fast VCD and FST library for waveform viewers written in Rust. It provides a common interface to read both FST and VCD waveform files, optimized for use-cases where only a subset of signals need to be accessed.

## Workspace Structure

This is a Cargo workspace with two main crates:
- `wellen/` - Core Rust library for reading waveform files
- `pywellen/` - Python bindings using PyO3/maturin

## Common Commands

### Rust Development
```bash
# Build the core library
cargo build
cargo build --release

# Run tests
cargo test
cargo test --release

# Run specific test
cargo test test_name

# Check code without building
cargo check

# Run benchmarks
cargo bench

# Clippy linting
cargo clippy
cargo clippy --all-targets --all-features
```

### Python Bindings Development
```bash
# Navigate to Python bindings
cd pywellen

# Install dependencies (requires Python virtual environment)
make deps

# Build and install for development
make develop

# Build wheel
make wheel

# Run Python tests
make test
# or directly: pytest tests/
```

### Testing
- Rust tests: `cargo test` from workspace root
- Python tests: `pytest tests/` from `pywellen/` directory
- Extensive test inputs available in `wellen/inputs/` for various waveform formats

## Code Architecture

### Core Components

1. **Hierarchy Management** (`wellen/src/hierarchy.rs`)
   - Central `Hierarchy` struct containing design metadata
   - Scopes (`Scope`) and variables (`Var`) organized in hierarchical tree
   - Reference types: `ScopeRef`, `VarRef`, `SignalRef` for efficient indexing
   - Support for VCD, FST, and GHW file format metadata

2. **Signal Processing** (`wellen/src/signals.rs`)
   - `Signal` struct for waveform data storage
   - `SignalValue` enum supporting binary, four-value, nine-value, string, and real signals
   - Compressed signal representation with time tables
   - Signal slicing capabilities for extracting bit ranges

3. **Format Parsers**
   - VCD parser (`wellen/src/vcd.rs`)
   - FST parser (`wellen/src/fst.rs`) 
   - GHW parser (`wellen/src/ghw/`)
   - Multi-threaded VCD parsing support

4. **Memory Management** (`wellen/src/wavemem.rs`)
   - Efficient memory representation for large waveform files
   - Compressed time tables and signal data

### Key Design Patterns

- Uses `NonZero*` types for space-efficient optional references
- Hierarchical string interning system for memory efficiency
- Iterator-based APIs for traversing hierarchy and signal changes
- Builder patterns for constructing hierarchies during parsing

### File Format Support

- **VCD**: Variable Change Dump files with multi-threaded parsing
- **FST**: Fast Signal Trace files with compression support
- **GHW**: GHDL waveform files for VHDL designs

## Development Notes

- Minimum Rust version: 1.81.0
- Uses `rayon` for parallel processing
- Memory-mapped file I/O with `memmap2`
- Supports both 2-state and 4-state signal values
- Extensive test coverage with real-world waveform files

## Linting and Quality

Run `cargo clippy` to check for Rust idioms and potential issues. The project maintains high code quality standards and follows Rust best practices.