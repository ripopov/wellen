# PyWellen

PyWellen is a Python binding for the [wellen](https://github.com/ekiwi/wellen) library, providing fast VCD, FST, and GHW waveform file reading capabilities for Python applications.

## Features

- **Fast Performance**: Built on the Rust wellen library for high-speed waveform processing
- **Multiple Format Support**: Read VCD (Value Change Dump), FST (Fast Signal Trace), and GHW (GHDL Waveform) files
- **Memory Efficient**: Optimized for handling large waveform files
- **Easy-to-use API**: Pythonic interface for waveform analysis
- **Multi-threaded Loading**: Optional multi-threaded VCD parsing for improved performance

## Installation

```bash
pip install pywellen
```

### Development Installation

For development, you'll need:
- Python >= 3.9
- Rust toolchain
- [maturin](https://github.com/PyO3/maturin) for building Python extensions

```bash
# Clone the repository
git clone https://github.com/ekiwi/wellen.git
cd wellen/pywellen

# Create virtual environment
python -m venv dev
source dev/bin/activate  # On Windows: dev\Scripts\activate

# Install dependencies
make deps

# Build and install in development mode
make develop
```

## Quick Start

```python
from pywellen import Waveform

# Load a waveform file
waves = Waveform(path="path/to/your/waveform.vcd")

# Access hierarchy information
hierarchy = waves.hierarchy
print(f"Waveform format: {hierarchy.file_format()}")
print(f"Timescale: {hierarchy.timescale()}")

# Iterate through top-level scopes
for scope in hierarchy.top_scopes():
    print(f"Scope: {scope.name(hierarchy)}")
    
    # Get variables in this scope
    for var in scope.vars(hierarchy):
        print(f"  Variable: {var.full_name(hierarchy)}")
        print(f"    Type: {var.var_type()}")
        print(f"    Width: {var.bitwidth()} bits")

# Access signal data
for var in hierarchy.all_vars():
    if var.name(hierarchy) == "clk":
        signal = waves.get_signal(var)
        
        # Get value at specific time
        value = signal.value_at_time(1000)  # Time in simulation units
        print(f"Value at time 1000: {value}")
        
        # Iterate through all signal changes
        for time, value in signal.all_changes():
            print(f"Change at {time}: {value}")
```

## API Reference

### Waveform

The main entry point for loading waveform files.

```python
waves = Waveform(
    path="file.vcd",
    multi_threaded=True,  # Enable multi-threaded VCD parsing
    remove_scopes_with_empty_name=False
)
```

**Attributes:**
- `hierarchy`: Access to the design hierarchy
- `time_table`: Time points where signal changes occur

**Methods:**
- `get_signal(var)`: Get signal data for a variable
- `get_signal_from_path(path)`: Get signal by hierarchical path

### Hierarchy

Provides access to the design structure and metadata.

**Methods:**
- `all_vars()`: Iterator over all variables in the design
- `top_scopes()`: Iterator over top-level scopes
- `date()`: Simulation date from the file
- `version()`: File format version
- `timescale()`: Time scale information
- `file_format()`: Format type ("VCD", "FST", "GHW", or "Unknown")

### Scope

Represents a hierarchical scope (module, task, function, etc.).

**Methods:**
- `name(hierarchy)`: Scope name
- `full_name(hierarchy)`: Full hierarchical path
- `scope_type()`: Type of scope (e.g., "module", "task", "function")
- `vars(hierarchy)`: Iterator over variables in this scope
- `scopes(hierarchy)`: Iterator over child scopes

### Var

Represents a signal variable.

**Methods:**
- `name(hierarchy)`: Variable name
- `full_name(hierarchy)`: Full hierarchical path
- `bitwidth()`: Bit width of the signal
- `var_type()`: Variable type (e.g., "Wire", "Reg", "Integer")
- `direction()`: Signal direction ("Input", "Output", "InOut", etc.)
- `is_real()`: True if real-valued signal
- `is_string()`: True if string-valued signal
- `is_bit_vector()`: True if bit vector signal
- `is_1bit()`: True if single-bit signal

### Signal

Contains the actual waveform data for a variable.

**Methods:**
- `value_at_time(time)`: Get value at specific simulation time
- `value_at_idx(idx)`: Get value at specific index in time table
- `all_changes()`: Iterator over all (time, value) changes

## Examples

### Finding Specific Signals

```python
from pywellen import Waveform

waves = Waveform(path="design.vcd")
h = waves.hierarchy

# Find all clock signals
for var in h.all_vars():
    if "clk" in var.name(h).lower():
        signal = waves.get_signal(var)
        print(f"Found clock: {var.full_name(h)}")
```

### Analyzing Signal Statistics

```python
# Count signal transitions
signal = waves.get_signal(var)
transitions = 0
last_value = None

for time, value in signal.all_changes():
    if last_value is not None and value != last_value:
        transitions += 1
    last_value = value

print(f"Signal {var.name(h)} has {transitions} transitions")
```

### Working with Time Tables

```python
# Access simulation time points
time_table = waves.time_table
print(f"Simulation starts at: {time_table[0]}")
print(f"Simulation ends at: {time_table[-1]}")
print(f"Total time points: {len(time_table)}")
```

## Performance Tips

1. **Use Multi-threading**: Enable `multi_threaded=True` for VCD files to speed up loading
2. **Selective Signal Loading**: Only call `get_signal()` for signals you need to analyze
3. **Iterate Efficiently**: Use `all_changes()` iterator instead of checking every time point
4. **Memory Considerations**: For very large files, process signals one at a time rather than loading all at once

## License

PyWellen is distributed under the BSD-3-Clause license. See the LICENSE file in the repository for details.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests on the [GitHub repository](https://github.com/ekiwi/wellen).

## See Also

- [wellen](https://github.com/ekiwi/wellen) - The underlying Rust library
- [VCD Specification](https://ieeexplore.ieee.org/document/954909) - IEEE Standard for Verilog VCD
- [FST Format](https://github.com/gtkwave/gtkwave/tree/master/gtkwave4/src/helpers/fst) - GTKWave FST implementation