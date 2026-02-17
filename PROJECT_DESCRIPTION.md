# Sheet Cut - CNC Feed Sequence Generator

A **Python-based GUI application** for generating cut feed sequences to cut metal sheets in specified patterns on CNC (Computer Numerical Control) machines. Built with Tkinter for the graphical interface and Matplotlib/Plotly for visualization.

---

## Overview

Sheet Cut is a desktop application designed for **transformer lamination manufacturing**. It automates the generation of CNC cutting programs for various sheet metal profiles, including:

- **Step-lap laminations** - Used in transformer core manufacturing
- **Central limb profiles** - Core sections of transformers
- **Side limb-yoke profiles** - Edge sections connecting yoke to limbs
- **Split yoke profiles** - Divided yoke sections

The application takes input parameters like sheet lengths, tool configurations, and step-lap counts, then generates Excel output files containing the precise feed distances and tool operations for the CNC machine.

---

## Application Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      Main Window (tkinter_v1.py)                │
├──────────────────┬──────────────────┬──────────────────┬────────┤
│     Create       │       Run        │   Parameters     │ Verify │
│   Cut Program    │    Execution     │    Update        │ Output │
└────────┬─────────┴────────┬─────────┴────────┬─────────┴────┬───┘
         │                  │                  │              │
         ▼                  ▼                  ▼              ▼
  Define tool       Execute cutting     Modify machine   Visualize
  sequence &        algorithms with     offset values    generated
  save to JSON      user inputs         & distances      Excel data
```

---

## Key Components

### GUI Module (`gui/`)

| File | Description |
|------|-------------|
| `tkinter_v1.py` | **Main entry point** - Launches the main window with navigation buttons |
| `create_cut_program.py` | Screen to define cutting programs with tool sequences, step-lap types, and configurations |
| `run_screen.py` | Execute cutting algorithms, input lengths/layers, and generate Excel output |
| `update_param.py` | Modify machine parameters (offsets, distances) stored in config |
| `verify_output_screen.py` | Visualize generated CNC output files to verify correctness |
| `visualize.py` | Matplotlib/Plotly visualization of CNC operations on sheet |
| `central_limb_v2.py` | Algorithm for central limb profile cutting patterns |

### Cutting Algorithms (`step_lap/`)

| File | Description |
|------|-------------|
| `step_lap_v4.py` | Latest step-lap algorithm implementation |
| `central_limb.py` | Central limb cutting pattern generator |
| `split_yoke.py` | Split yoke cutting patterns |
| `fishy_fish.py` | Specialized "fish" profile patterns |

### Shared Utilities (`shared/`)

| File | Description |
|------|-------------|
| `base_tools.py` | Tool classes (Hole, Vnotch, FullCut, Spear, etc.) with step-lap logic |
| `config.py` | Configuration loader with machine offsets and tool distance maps |
| `labels.py` | UI labels, constants, and message templates |
| `pandas_utils.py` | Pandas DataFrame utilities for Excel I/O |

---

## Cutting Tools Supported

| Tool Code | Tool Name | Description |
|-----------|-----------|-------------|
| `h` | Hole Punch | Creates holes at specified positions |
| `v` | V-Notch | Creates V-shaped notches with lateral shift capability |
| `fm45` | Full Cut -45° | Angled cut at -45 degrees |
| `fp45` | Full Cut +45° | Angled cut at +45 degrees |
| `f0` | Full Cut 0° | Straight perpendicular cut |
| `s` | Spear | Combined V-notch and full cut operation |
| `ys` | Yoke Splitter | Specialized yoke splitting tool |

---

## Step-Lap Types

The application supports multiple step-lap configurations for transformer laminations:

1. **No Step-Lap** - Single layer cutting
2. **Horizontal (Longitudinal)** - Steps along the feed direction
3. **Vertical (Lateral)** - Steps perpendicular to feed
4. **Skewed (Lateral)** - Angled lateral stepping

---

## Data Flow

```
JSON Program Definition     →    Algorithm Execution    →    Excel Output
(cut_program_input/*.json)  →    (step_lap/central_limb) →   (cut_program_output/*.xlsx)
                                       ↓
                            Visualization (verify_output_screen)
```

### Input Format
JSON files defining tool sequences with:
- Tool names and order
- Step-lap configuration (count, distance, type)
- Open/closed states for each tool

### Output Format
Excel files containing:
- Feed distances for each operation
- V-notch travel distances
- Tool numbers and operation indices
- Sheet counts and shape information

---

## Configuration

Machine-specific parameters in `gui/config.json`:

```json
{
    "OFFSET_V_LAT": 0.0,
    "OFFSET_F0": 0.0,
    "OFFSET_FP45": -1.665,
    "OFFSET_FM45": 0.865,
    "DISTANCE_HOLE_VNOTCH": 1250.0,
    "DISTANCE_SHEAR_VNOTCH": 4335.0,
    "COIL_LENGTH": 400000.0
}
```

---

## Running the Application

```bash
cd gui
python tkinter_v1.py
```

**Requirements:**
- Python 3.x
- Tkinter (usually included with Python)
- Pandas (for Excel I/O)
- Matplotlib (for visualization)
- Plotly (for interactive visualization)
- openpyxl (for Excel file handling)

---

## Project Structure

```
sheet_cut/
├── gui/                    # GUI application and algorithms
│   ├── tkinter_v1.py       # Main entry point
│   ├── create_cut_program.py
│   ├── run_screen.py
│   ├── update_param.py
│   ├── verify_output_screen.py
│   ├── visualize.py
│   ├── central_limb_v2.py
│   └── config.json
├── step_lap/               # Cutting algorithm implementations
│   ├── step_lap_v4.py
│   ├── central_limb.py
│   ├── split_yoke.py
│   └── fishy_fish.py
├── shared/                 # Shared utilities and constants
│   ├── base_tools.py
│   ├── config.py
│   ├── labels.py
│   └── pandas_utils.py
├── cut_program_input/      # JSON program definitions
├── cut_program_output/     # Generated Excel outputs
└── screenshots/            # Application screenshots
```

---

## Author

**Omkar** - Created April 2021
