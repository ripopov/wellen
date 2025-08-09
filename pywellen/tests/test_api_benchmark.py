#!/usr/bin/env python3
"""
Simplified VCD generator for benchmark testing.
Generates 4 types of signals:
1. 1-bit clock with specified frequency
2. 1-bit clock with frequency changing by sinewave function
3. Random 32-bit wire signal with specified change rate
4. Sinewave signal (real) with specified amplitude, frequency and sampling rate
"""

import math
import os
import random
import sys
import string
from datetime import datetime


def encode_id(n):
    """Encode signal ID using VCD format."""
    chars = "!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
    if n < len(chars):
        return chars[n]
    else:
        return chars[n % len(chars)] + encode_id(n // len(chars))


def generate_random_scope_name(prefix="scope", length=8):
    """Generate a random scope name."""
    # Use combination of letters and numbers for readability
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    return f"{prefix}_{suffix}"


class VCDGenerator:
    def __init__(self, filename="benchmark_signals.vcd"):
        self.filename = filename
        self.file = None
        self.signals = []

    def open_file(self):
        self.file = open(self.filename, 'w')

    def close_file(self):
        if self.file:
            self.file.close()

    def write_line(self, line=""):
        self.file.write(line + "\n")

    def write_header(self):
        """Write VCD header."""
        self.write_line("$date")
        self.write_line(f"    {datetime.now().strftime('%a %b %d %H:%M:%S %Y')}")
        self.write_line("$end")
        self.write_line("$version")
        self.write_line("    Python Simplified VCD Generator")
        self.write_line("$end")
        self.write_line("$timescale")
        self.write_line("    1ps")
        self.write_line("$end")

    def define_signals(self):
        """Define the 4 required signal types with hierarchical scopes."""
        # Start with top-level scope
        self.write_line("$scope module top $end")

        # Signal configurations for the 4 required types
        signal_configs = [
            # 1-bit clock with specified frequency (100 kHz)
            {
                "name": "clk_fixed_100khz",
                "type": "fixed_clock",
                "frequency": 100_000,
                "bitwidth": 1,
                "var_type": "wire"
            },
            {
                "name": "clk_fixed_1ghz",
                "type": "fixed_clock",
                "frequency": 1_000_000_000,
                "bitwidth": 1,
                "var_type": "wire"
            },
            {
                "name": "clk_fixed_10ghz",
                "type": "fixed_clock",
                "frequency": 10_000_000_000,
                "bitwidth": 1,
                "var_type": "wire"
            },
            # 1-bit clock with frequency changing by sinewave function
            {
                "name": "clk_sine_mod",
                "type": "sine_modulated_clock",
                "mod_freq": 1000,  # 1 kHz modulation frequency
                "freq_low": 1_000_000,  # 1Mhz kHz low frequency
                "freq_high": 100_000_000,  # 100 MHz high frequency
                "bitwidth": 1,
                "var_type": "wire"
            },
            # Random 32-bit wire signal with specified change rate
            {
                "name": "random_32bit_25mhz",
                "type": "random_wire",
                "change_rate": 25_000_000,  # 25 MHz change rate
                "bitwidth": 32,
                "var_type": "wire"
            },
            # Sinewave signal (real) with specified amplitude, frequency and sampling rate
            {
                "name": "sine_real_10Mhz",
                "type": "real_sine",
                "frequency": 10_000_000,  # 10 MHz
                "amplitude_min": -2.5,
                "amplitude_max": 2.5,
                "sampling_rate": 1_000_000_000,  # 1 GHz sampling rate
                "bitwidth": 64,
                "var_type": "real"
            },
            {
                "name": "sine_real_100Mhz",
                "type": "real_sine",
                "frequency": 100_000_000,  # 10 MHz
                "amplitude_min": -2.5,
                "amplitude_max": 2.5,
                "sampling_rate": 1_000_000_000,  # 1 GHz sampling rate
                "bitwidth": 64,
                "var_type": "real"
            },
            {
                "name": "sine_real_1Ghz",
                "type": "real_sine",
                "frequency": 1_000_000_000,  # 10 MHz
                "amplitude_min": -2.5,
                "amplitude_max": 2.5,
                "sampling_rate": 1_000_000_000,  # 1 GHz sampling rate
                "bitwidth": 64,
                "var_type": "real"
            },
            {
                "name": "sine_real_2GHz",
                "type": "real_sine",
                "frequency": 2_000_000_000,  # 10 MHz
                "amplitude_min": -2.5,
                "amplitude_max": 2.5,
                "sampling_rate": 1_000_000_000,  # 1 GHz sampling rate
                "bitwidth": 64,
                "var_type": "real"
            }
        ]

        # First, define real signals in the top scope
        signal_ids = []
        for i, config in enumerate(signal_configs):
            signal_id = encode_id(i)
            signal_ids.append(signal_id)
            self.write_line(f"$var {config['var_type']} {config['bitwidth']} {signal_id} {config['name']} $end")

            # Store signal info for simulation
            signal_info = {
                "id": signal_id,
                "config": config,
                "last_value": None,
                "last_change_time": 0,
                "phase": 0,  # For sine waves
                "next_sample_time": 0
            }

            # Initialize type-specific fields
            if config["type"] == "fixed_clock":
                signal_info["current_state"] = 0
                signal_info["last_edge_time"] = 0
            elif config["type"] == "sine_modulated_clock":
                signal_info["last_edge_time"] = 0
                signal_info["current_state"] = 0
            elif config["type"] == "random_wire":
                signal_info["current_value"] = random.randint(0, 2**32 - 1)
                signal_info["last_change_time"] = 0
            elif config["type"] == "real_sine":
                signal_info["next_sample_time"] = 0  # Start sampling immediately

            self.signals.append(signal_info)

        # Create hierarchical tree structure with 10 children per level
        def create_scope_tree(parent_path, current_level, max_level):
            """Recursively create scope tree with 10 children per node."""
            if current_level > max_level:
                return
            
            # Create 10 child scopes at this level
            for child_idx in range(10):
                scope_name = generate_random_scope_name(f"l{current_level}_c{child_idx}")
                full_path = f"{parent_path}.{scope_name}" if parent_path else scope_name
                
                # Enter the scope
                self.write_line(f"$scope module {scope_name} $end")
                
                # Create aliases to all signals
                for i, (signal_id, config) in enumerate(zip(signal_ids, signal_configs)):
                    # Generate unique alias name based on path
                    alias_name = f"{config['name']}_l{current_level}_c{child_idx}"
                    self.write_line(f"$var {config['var_type']} {config['bitwidth']} {signal_id} {alias_name} $end")
                
                # Recursively create children
                create_scope_tree(full_path, current_level + 1, max_level)
                
                # Exit this scope
                self.write_line("$upscope $end")
        
        # Create the tree structure (5 levels deep, 10 children per level)
        create_scope_tree("", 1, 5)
        
        # Close top scope
        self.write_line("$upscope $end")
        self.write_line("$enddefinitions $end")

    def calculate_signal_value(self, signal, time_sec):
        """Calculate signal value at given time."""
        config = signal["config"]
        signal_type = config["type"]

        if signal_type == "fixed_clock":
            # Return the current state of the clock
            return signal["current_state"]

        elif signal_type == "sine_modulated_clock":
            # Return the current state of the sine modulated clock
            return signal["current_state"]

        elif signal_type == "random_wire":
            # Random 32-bit value that changes at specified rate
            change_period = 1.0 / config["change_rate"]
            if time_sec - signal["last_change_time"] >= change_period:
                signal["last_change_time"] = time_sec
                signal["current_value"] = random.randint(0, 2**32 - 1)
            return signal["current_value"]

        elif signal_type == "real_sine":
            # Real sine wave with specified amplitude and frequency
            freq = config["frequency"]
            amp_min = config["amplitude_min"]
            amp_max = config["amplitude_max"]
            
            # Calculate sine value (-1 to 1)
            sine_val = math.sin(2 * math.pi * freq * time_sec)
            
            # Map to amplitude range
            amplitude = amp_min + (sine_val + 1) / 2 * (amp_max - amp_min)
            return amplitude

        return 0

    def get_next_change_time(self, signal, current_time_ps):
        """Get the next time when this signal will change value."""
        config = signal["config"]
        signal_type = config["type"]
        current_time_sec = current_time_ps * 1e-12

        if signal_type == "fixed_clock":
            # Fixed frequency clock changes at regular intervals
            period_ps = int(1e12 / config["frequency"])
            half_period_ps = period_ps // 2
            
            # Calculate next edge time based on last edge
            time_since_last_edge = current_time_ps - signal["last_edge_time"]
            return signal["last_edge_time"] + half_period_ps

        elif signal_type == "sine_modulated_clock":
            # Calculate variable frequency based on sine modulation
            mod_freq = config["mod_freq"]
            freq_low = config["freq_low"]
            freq_high = config["freq_high"]
            
            # Calculate current frequency at current time
            sine_val = math.sin(2 * math.pi * mod_freq * current_time_sec)
            current_freq = freq_low + (sine_val + 1) / 2 * (freq_high - freq_low)
            
            # Calculate time to next edge based on current frequency
            period_ps = int(1e12 / current_freq)
            half_period_ps = period_ps // 2
            
            # Next edge is half period from last edge
            return signal["last_edge_time"] + half_period_ps

        elif signal_type == "random_wire":
            # Random wire changes at specified rate
            change_period_ps = int(1e12 / config["change_rate"])
            
            # Track last change time in picoseconds
            if "last_change_time_ps" not in signal:
                signal["last_change_time_ps"] = 0
            
            next_change = signal["last_change_time_ps"] + change_period_ps
            
            if next_change <= current_time_ps:
                # Time for next change
                return current_time_ps
            else:
                return next_change

        elif signal_type == "real_sine":
            # Sample at specified sampling rate
            sample_period_ps = int(1e12 / config["sampling_rate"])
            
            # Get the next sample time
            if "next_sample_time" not in signal:
                # First sample at time 0
                return 0 if current_time_ps == 0 else current_time_ps + sample_period_ps
            elif signal["next_sample_time"] <= current_time_ps:
                # We're at or past the scheduled sample time
                return current_time_ps
            else:
                # Return the scheduled sample time
                return signal["next_sample_time"]

        # Default fallback
        return current_time_ps + 1000  # 1ns


    def write_initial_values(self):
        """Write initial signal values at time 0."""
        self.write_line("#0")
        self.write_line("$dumpvars")

        for signal in self.signals:
            value = self.calculate_signal_value(signal, 0.0)
            signal["last_value"] = value

            # Format value based on signal type
            config = signal["config"]
            if config["var_type"] == "real":
                self.write_line(f"r{value:.16g} {signal['id']}")
            elif config["bitwidth"] == 1:
                self.write_line(f"{int(value)}{signal['id']}")
            else:
                # Multi-bit signals use binary format
                bin_str = format(int(value), f"0{config['bitwidth']}b")
                self.write_line(f"b{bin_str} {signal['id']}")

        self.write_line("$end")

    def simulate(self, duration_sec=0.001):
        """Simulate signals over specified duration."""
        duration_ps = int(duration_sec * 1e12)  # Convert to picoseconds
        
        current_time = 0
        
        # Special handling for time 0 - just after initial values
        # Check if any signals need updates at time 1ps
        first_iteration = True
        
        while current_time < duration_ps:
            time_sec = current_time * 1e-12  # Convert to seconds
            
            # Get next change time for all signals
            next_change_times = []
            for signal in self.signals:
                next_time = self.get_next_change_time(signal, current_time)
                next_change_times.append(next_time)
            
            # Find the earliest next change time
            next_time = min(next_change_times)
            
            # Don't go past the duration
            if next_time > duration_ps:
                next_time = duration_ps
            
            # For first iteration, advance at least 1ps to avoid time 0
            if first_iteration and next_time == 0:
                next_time = 1
                first_iteration = False
            
            # Advance to next change time
            current_time = next_time
            if current_time >= duration_ps:
                break
                
            time_sec = current_time * 1e-12
            
            # Check all signals at this time point and collect changes
            changes = []
            for i, signal in enumerate(self.signals):
                # Check if this signal should change at current time
                if next_change_times[i] == current_time:
                    config = signal["config"]
                    
                    if config["type"] == "fixed_clock" or config["type"] == "sine_modulated_clock":
                        # Toggle clock state
                        signal["current_state"] = 1 - signal["current_state"]
                        signal["last_edge_time"] = current_time
                        signal["last_value"] = signal["current_state"]
                        changes.append((signal, signal["current_state"]))
                    
                    elif config["type"] == "real_sine":
                        # For real signals, always record at sample points
                        new_value = self.calculate_signal_value(signal, time_sec)
                        signal["last_value"] = new_value
                        changes.append((signal, new_value))
                        signal["next_sample_time"] = current_time + int(1e12 / config["sampling_rate"])
                    
                    elif config["type"] == "random_wire":
                        # For random wire, generate new random value
                        signal["current_value"] = random.randint(0, 2**32 - 1)
                        signal["last_change_time"] = time_sec
                        signal["last_change_time_ps"] = current_time
                        signal["last_value"] = signal["current_value"]
                        changes.append((signal, signal["current_value"]))
                    
                    else:
                        # For other signals, calculate new value
                        new_value = self.calculate_signal_value(signal, time_sec)
                        if new_value != signal["last_value"]:
                            signal["last_value"] = new_value
                            changes.append((signal, new_value))

            # Write changes if any occurred
            if changes:
                self.write_line(f"#{current_time}")
                for signal, value in changes:
                    config = signal["config"]
                    if config["var_type"] == "real":
                        self.write_line(f"r{value:.16g} {signal['id']}")
                    elif config["bitwidth"] == 1:
                        self.write_line(f"{int(value)}{signal['id']}")
                    else:
                        # Multi-bit signals use binary format
                        bin_str = format(int(value), f"0{config['bitwidth']}b")
                        self.write_line(f"b{bin_str} {signal['id']}")

    def generate(self, duration_sec=0.001):
        """Generate the complete VCD file."""
        try:
            self.open_file()
            self.write_header()
            self.define_signals()
            self.write_initial_values()
            self.simulate(duration_sec)
            print(f"VCD file '{self.filename}' generated successfully!")
            print(f"Contains 4 signal types:")
            print(f"  - Fixed frequency clock")
            print(f"  - Sine-modulated frequency clock") 
            print(f"  - Random 32-bit wire")
            print(f"  - Real sine wave")
            print(f"Simulation duration: {duration_sec}s")
        finally:
            self.close_file()


def test_api_benchmark():
    """Test the API benchmark."""
    import time
    from pywellen import Waveform

    if not os.path.exists("benchmark_signals.vcd"):
        print("Generating VCD file (this may take a while)...")
        start_time = time.perf_counter()
        generator = VCDGenerator("benchmark_signals.vcd")
        generator.generate(duration_sec=0.001)
        load_time = time.perf_counter() - start_time
        print(f"Generation took {load_time * 1000:.2f}ms")
    
    print("\nStarting API benchmarks...")
    
    vcd_path = "benchmark_signals.vcd"
    
    # Benchmark loading approaches and get waves object
    waves = benchmark_loading_approaches(vcd_path)
    
    # Get hierarchy and root variables
    h = waves.hierarchy
    root_vars = get_root_vars(h)
    
    # Run benchmarks
    benchmark_var_iteration(h, root_vars)
    benchmark_time_table_access(waves, h)
    
    # Benchmark signal loading methods
    signals_1 = benchmark_get_signal(waves, root_vars, h)
    waves.unload_signals(signals_1)
    
    signals_2 = benchmark_load_signals(waves, root_vars, h)
    waves.unload_signals(signals_2)
    
    signals_3 = benchmark_load_signals_multithreaded(waves, root_vars, h)
    
    # Benchmark signal operations
    benchmark_value_at_time(waves, signals_3, h)
    benchmark_query_signal(waves, signals_3, h)
    benchmark_all_changes(signals_3)
    
    print("\nBenchmark complete!")


def benchmark_loading_approaches(vcd_path):
    """Benchmark different loading approaches and return waves object for later use"""
    # Single shot loading
    waves_single, time_single = load_waveform_single_shot(vcd_path)
    del waves_single  # Free memory
    
    # Lazy loading
    waves, time_lazy = load_waveform_lazy(vcd_path)
    
    # Compare loading results
    print("\nLoading comparison:")
    print(f"   Single shot: {time_single * 1000:.2f}ms")
    print(f"   Lazy loading: {time_lazy * 1000:.2f}ms")
    print(f"   Overhead: {(time_lazy - time_single) * 1000:.2f}ms ({((time_lazy - time_single) / time_single * 100):.1f}%)")
    
    return waves


def load_waveform_single_shot(path):
    """Load waveform with header and body in one call"""
    import time
    from pywellen import Waveform
    
    print("\n1. Loading waveform in single shot:")
    start_time = time.perf_counter()
    waves = Waveform(path=path)
    total_time = time.perf_counter() - start_time
    print(f"   Total loading time: {total_time * 1000:.2f}ms")
    print(f"   Body loaded: {waves.body_loaded()}")
    return waves, total_time


def load_waveform_lazy(path):
    """Load waveform header first, then body separately"""
    import time
    from pywellen import Waveform
    
    print("\n2. Loading waveform with lazy body loading:")
    
    # Load header only
    print("   a) Loading header only:")
    start_time = time.perf_counter()
    waves = Waveform(path=path, load_body=False)
    header_time = time.perf_counter() - start_time
    print(f"      Header loading time: {header_time * 1000:.2f}ms")
    print(f"      Body loaded: {waves.body_loaded()}")
    
    # Load body
    print("   b) Loading body:")
    start_time = time.perf_counter()
    waves.load_body()
    body_time = time.perf_counter() - start_time
    print(f"      Body loading time: {body_time * 1000:.2f}ms")
    print(f"      Body loaded: {waves.body_loaded()}")
    
    total_time = header_time + body_time
    print(f"   Total loading time: {total_time * 1000:.2f}ms")
    return waves, total_time


def get_root_vars(h):
    """Get all variables in root scope"""
    root_vars = []
    for scope in h.top_scopes():
        for var in scope.vars(h):
            root_vars.append(var)
    return root_vars


def benchmark_var_iteration(h, root_vars):
    """Benchmark variable iteration operations"""
    import time
    
    print("\nVar iteration benchmarks:")
    
    # Benchmark iterating first 100 elements in all_vars
    start_time = time.perf_counter()
    first_100_vars = []
    for i, var in enumerate(h.all_vars()):
        first_100_vars.append(var)
        if i >= 99:  # Stop after 100 elements (0-99)
            break
    all_vars_time = time.perf_counter() - start_time
    print(f"   Iterating first 100 vars from all_vars(): {all_vars_time * 1000:.2f}ms")
    
    # Report root vars collection time
    start_time = time.perf_counter()
    test_root_vars = get_root_vars(h)
    root_vars_time = time.perf_counter() - start_time
    print(f"   Found {len(test_root_vars)} vars in root scope: {root_vars_time * 1000:.2f}ms")


def benchmark_time_table_access(waves, h):
    """Benchmark time table access operations"""
    import time
    
    print("\nTime table benchmark:")
    
    # Get timescale for units
    timescale = h.timescale()
    if timescale:
        unit_str = str(timescale.unit)
        print(f"   Timescale: {timescale.factor}{unit_str}")
    else:
        unit_str = "units"
    
    # Ensure we have time table
    if waves.time_table is None:
        print("   Time table not available (body not loaded)")
        return
    
    start_time = time.perf_counter()
    first_timestamp = waves.time_table[0]
    first_time = time.perf_counter() - start_time
    print(f"   Getting first timestamp: {first_time * 1000:.2f}ms (value: {first_timestamp} {unit_str})")
    
    start_time = time.perf_counter()
    time_table_len = len(waves.time_table)
    len_time = time.perf_counter() - start_time
    print(f"   Getting time_table length: {len_time * 1000:.2f}ms (length: {time_table_len})")
    
    # Get middle timestamp
    middle_idx = time_table_len // 2
    start_time = time.perf_counter()
    middle_timestamp = waves.time_table[middle_idx]
    middle_time = time.perf_counter() - start_time
    print(f"   Getting middle timestamp: {middle_time * 1000:.2f}ms (index: {middle_idx}, value: {middle_timestamp} {unit_str})")


def benchmark_get_signal(waves, vars, h):
    """Benchmark using get_signal for each var individually"""
    import time
    
    print("\n get_signal benchmark (individual calls):")
    start_time = time.perf_counter()
    signals = []
    for var in vars:
        sig_start_time = time.perf_counter()
        sig = waves.get_signal(var)
        signals.append(sig)
        sig_time = time.perf_counter() - sig_start_time
        print(f"   get_signal for {var.name(h)} took {sig_time * 1000:.2f}ms")
    
    total_time = time.perf_counter() - start_time
    print(f"   get_signal total time for {len(vars)} signals: {total_time * 1000:.2f}ms")
    print(f"   Average per signal: {total_time / len(vars) * 1000:.2f}ms")
    return signals


def benchmark_load_signals(waves, vars, h):
    """Benchmark using load_signals for batch loading"""
    import time
    
    print("\n load_signals benchmark (batch single-threaded):")
    start_time = time.perf_counter()
    signals = waves.load_signals(vars)
    total_time = time.perf_counter() - start_time
    print(f"   load_signals total time for {len(vars)} signals: {total_time * 1000:.2f}ms")
    print(f"   Average per signal: {total_time / len(vars) * 1000:.2f}ms")
    return signals


def benchmark_load_signals_multithreaded(waves, vars, h):
    """Benchmark using load_signals_multithreaded for batch loading with multiple threads"""
    import time
    
    print("\n load_signals_multithreaded benchmark (batch multi-threaded):")
    start_time = time.perf_counter()
    signals = waves.load_signals_multithreaded(vars)
    total_time = time.perf_counter() - start_time
    print(f"   load_signals_multithreaded total time for {len(vars)} signals: {total_time * 1000:.2f}ms")
    print(f"   Average per signal: {total_time / len(vars) * 1000:.2f}ms")
    return signals


def benchmark_value_at_time(waves, signals, h):
    """Benchmark value_at_time operations"""
    import time
    
    print("\n value_at_time benchmark:")
    
    # Get timescale for units
    timescale = h.timescale()
    unit_str = str(timescale.unit) if timescale else "units"
    
    # Calculate test times based on waveform duration
    # Note: time_table is guaranteed to exist here because signals were loaded
    start_time_val = waves.time_table[0]
    end_time_val = waves.time_table[-1]
    duration = end_time_val - start_time_val
    num_samples = 4096
    delta = duration / (num_samples - 1)  # Divide duration by (samples - 1) for inclusive range
    
    # Generate 4096 test points evenly distributed across duration
    test_times = [int(start_time_val + i * delta) for i in range(num_samples)]
    # Ensure last point is exactly the end time
    test_times[-1] = end_time_val
    
    print(f"   Waveform duration: {duration} {unit_str} (from {start_time_val} to {end_time_val})")
    print(f"   Sampling delta: {delta:.2f} {unit_str}")
    print(f"   Test times: {len(test_times)} points")
    
    total_ops = 0
    start_time = time.perf_counter()
    for sig in signals:
        for test_time in test_times:
            _ = sig.value_at_time(test_time)
            total_ops += 1
    value_at_time_total = time.perf_counter() - start_time
    print(f"   value_at_time total time for {total_ops} operations: {value_at_time_total * 1000:.2f}ms")
    print(f"   Average per operation: {value_at_time_total / total_ops * 1000:.2f}ms")


def benchmark_query_signal(waves, signals, h):
    """Benchmark query_signal operations using same test points as value_at_time"""
    import time
    
    print("\n query_signal benchmark:")
    
    # Get timescale for units
    timescale = h.timescale()
    unit_str = str(timescale.unit) if timescale else "units"
    
    # Calculate test times based on waveform duration (same as value_at_time)
    start_time_val = waves.time_table[0]
    end_time_val = waves.time_table[-1]
    duration = end_time_val - start_time_val
    num_samples = 4096
    delta = duration / (num_samples - 1)
    
    # Generate same test points as value_at_time benchmark
    test_times = [int(start_time_val + i * delta) for i in range(num_samples)]
    test_times[-1] = end_time_val
    
    print(f"   Using same test configuration as value_at_time:")
    print(f"   Waveform duration: {duration} {unit_str} (from {start_time_val} to {end_time_val})")
    print(f"   Test times: {len(test_times)} points")
    
    # Benchmark query_signal
    total_ops = 0
    transitions_found = 0
    start_time = time.perf_counter()
    
    for sig in signals:
        for test_time in test_times:
            result = sig.query_signal(test_time)
            total_ops += 1
            # Count transitions found (where next_time is set and different from current)
            if result.next_time is not None and result.actual_time != result.next_time:
                transitions_found += 1
    
    query_signal_total = time.perf_counter() - start_time
    print(f"   query_signal total time for {total_ops} operations: {query_signal_total * 1000:.2f}ms")
    print(f"   Average per operation: {query_signal_total / total_ops * 1000:.2f}ms")
    print(f"   Transitions found: {transitions_found} ({transitions_found / total_ops * 100:.1f}% of queries)")
    
    # Additional statistics
    print("\n   Additional query_signal statistics:")
    
    # Sample a few queries to show the kind of data returned
    sample_signal = signals[0] if signals else None
    if sample_signal:
        print("   Sample queries (first signal):")
        sample_times = [test_times[0], test_times[len(test_times)//4], test_times[len(test_times)//2], test_times[-1]]
        for i, t in enumerate(sample_times):
            result = sample_signal.query_signal(t)
            print(f"     Query {i+1} at {t}: value={result.value}, actual_time={result.actual_time}, "
                  f"next_time={result.next_time}")


def benchmark_all_changes(signals):
    """Benchmark all_changes operations"""
    import time
    
    print("\n all_changes benchmark:")
    total_changes = 0
    start_time = time.perf_counter()
    for sig in signals:
        changes = list(sig.all_changes())
        total_changes += len(changes)
    all_changes_total = time.perf_counter() - start_time
    print(f"   all_changes total time for {len(signals)} signals: {all_changes_total * 1000:.2f}ms")
    print(f"   Average per signal: {all_changes_total / len(signals) * 1000:.2f}ms")
    print(f"   Total changes processed: {total_changes}")


if __name__ == "__main__":
    test_api_benchmark()
