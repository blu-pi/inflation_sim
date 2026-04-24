# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Simulation

```bash
python main.py
```

This opens a Tkinter parameter window. Fill in layer sizes and component counts, then click "Start Simulation!" to launch the interactive supply chain graph.

**Running individual test files:**
```bash
python test/product_test.py
python test/composites_test.py
python test/argdicttest.py
```

Tests are git-ignored and not part of a test framework — they are standalone scripts with manual `test1()`, `test2()` calls.

**Dependencies:** `networkx`, `matplotlib`, plus standard library `tkinter`.

## Architecture

The simulation models a three-layer supply chain economy:

```
GlobalMaterial (layer 0)  — Energy, Labour (not yet active)
RawMaterial    (layer 1)  — base inputs
ProcessedMaterial (layer 2) — made from RawMaterials (Composite)
ConsumerProduct   (layer 3) — made from ProcessedMaterials (Composite)
```

`Economy` ([market/economy.py](market/economy.py)) is the top-level orchestrator. It creates all product instances, organizes them into `Layer` objects, then calls `connectAllLayers()` which runs `SymmetricalConnection` between adjacent layers.

`SymmetricalConnection` ([market/products/structs/layer_connection.py](market/products/structs/layer_connection.py)) enforces that every parent-layer product appears in at least one child's components, and that each child has approximately `num_preferred_components` parents. It randomly assigns connections while tracking frequency to stay balanced.

`ComponentDict` ([market/products/structs/components.py](market/products/structs/components.py)) stores composition as absolute (non-normalized) weights internally. Call `getNormalisedWeights()` for analysis — normalization is deferred to avoid floating-point accumulation in the simulation.

`ConsumerProduct.deriveRawMaterialComposition()` ([market/products/consumer_goods.py](market/products/consumer_goods.py)) recursively walks the two-level hierarchy to compute a normalized flat mapping of raw materials → proportional contribution.

## Configuration Flow

`main.py` defines `ArgDict` subclass instances (one per product type), passes them all to `App` (Tkinter UI in [market/input/setup.py](market/input/setup.py)), which collects user input and calls `Economy(arg_dicts)`.

Each `ArgDict` subclass holds a `DEFAULTS` dict. User input is merged with `|` (Python 3.9+), so any unset field falls back to its default. The `Section` widget in `setup.py` auto-generates input fields from the type annotations of each ArgDict field (int → `entry_field`, bool → `tick_box`, list → `drop_down`).

Help text for each parameter is loaded from [util/arg_info.txt](util/arg_info.txt) and shown via info buttons in the UI.

## Visualization

`Graph` ([market/graph.py](market/graph.py)) builds a NetworkX `DiGraph` by traversing product components. Nodes are product instances; edges go child→parent. `InteractiveGraphDisplay` ([market/input/runtime_ui.py](market/input/runtime_ui.py)) embeds this in a Tkinter window with clickable nodes (shows component details in a sidebar), pan/zoom, and PNG export.

## Known Incomplete Features

- `use_globals` / `GlobalMaterial` is not yet wired into `connectAllLayers()`.
- `units_avail` on `RawMaterial` is stored but not enforced.
- "Load simulation config" button in the UI is a stub.
