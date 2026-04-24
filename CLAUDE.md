# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Simulation

```bash
python main.py
```

This starts a Flask web server at `http://127.0.0.1:5000` and opens it in the browser automatically. Fill in layer sizes and component counts, then click "Start Simulation" to view the interactive supply chain graph.

**Running individual test files:**
```bash
python test/product_test.py
python test/composites_test.py
python test/argdicttest.py
```

Tests are git-ignored and not part of a test framework — they are standalone scripts with manual `test1()`, `test2()` calls.

**Dependencies:** `networkx`, `flask`, plus standard library only.

## Architecture

The simulation models a three-layer supply chain economy:

```
GlobalMaterial (layer 0)  — Energy, Labour (not yet active)
RawMaterial    (layer 1)  — base inputs
ProcessedMaterial (layer 2) — made from RawMaterials (Composite)
ConsumerProduct   (layer 3) — made from ProcessedMaterials (Composite)
```

`Economy` ([market/economy.py](market/economy.py)) is the top-level orchestrator. It creates all product instances, organizes them into `Layer` objects, then calls `connectAllLayers()` which runs `SymmetricalConnection` between adjacent layers. The resulting `Graph` is stored as `self.graph` for the web layer to consume.

`SymmetricalConnection` ([market/products/structs/layer_connection.py](market/products/structs/layer_connection.py)) enforces that every parent-layer product appears in at least one child's components, and that each child has approximately `num_preferred_components` parents. It randomly assigns connections while tracking frequency to stay balanced.

`ComponentDict` ([market/products/structs/components.py](market/products/structs/components.py)) stores composition as absolute (non-normalized) weights internally. Call `getNormalisedWeights()` for analysis — normalization is deferred to avoid floating-point accumulation in the simulation.

`ConsumerProduct.deriveRawMaterialComposition()` ([market/products/consumer_goods.py](market/products/consumer_goods.py)) recursively walks the two-level hierarchy to compute a normalized flat mapping of raw materials → proportional contribution.

## Configuration Flow

`main.py` calls `web.app.start()`. The Flask app at [web/app.py](web/app.py) serves a parameter form at `/`, collects user input, and POSTs to `/run` which instantiates `Economy` and redirects to `/simulation`.

Each `ArgDict` subclass (in [market/input/sim_args.py](market/input/sim_args.py)) holds a `DEFAULTS` dict. User input is merged with `|` (Python 3.9+), so any unset field falls back to its default. The web form auto-generates fields from the type of each default value (bool → checkbox, int/float → number input, list → select, str → text). Help text is loaded from [util/arg_info.txt](util/arg_info.txt) and shown as hover tooltips.

**Multi-run state:** Product subclasses accumulate instances in class-level `_existing` lists. `_reset_products()` in `web/app.py` clears these and resets `Product.total_created` before each run so IDs restart cleanly.

## Web Layer (`web/`)

Flask routes:
- `GET /` — parameter form (renders `index.html` with sections built from `ARG_CLASSES`)
- `POST /run` — runs the simulation, stores `_graph_json` and `_node_map` as module globals, redirects to `/simulation`
- `GET /simulation` — graph viewer page (`simulation.html`)
- `GET /api/graph` — returns vis.js-compatible JSON (`{nodes, edges}`)
- `GET /api/node/<id>` — returns node attributes: `name`, `layer`, `id`, `unit_cost`; plus `units_avail` for Raw, `num_components`/`components` for Composites, `raw_composition` for Consumer

`_serialize_graph()` maps each product to a vis.js node using `product.getDisplayName()` as the string ID (format: `"LayerName: {_id}"`). Level is `4 - LAYER_NUM` so consumers appear at the top of the hierarchical layout.

## Visualization

`Graph` ([market/graph.py](market/graph.py)) builds a NetworkX `DiGraph` by traversing product components. Nodes are product instances; edges go child→parent.

The web UI (`simulation.html`) uses **vis.js Network** (CDN) with a hierarchical top-down layout. Clicking a node highlights its edges (incoming=blue, outgoing=green) and populates the sidebar with a Properties section (id, unit_cost, units_avail for Raw) and composition bar charts. Toolbar provides Reset View and Export PNG.

## Known Incomplete Features

- `use_globals` / `GlobalMaterial` is not yet wired into `connectAllLayers()`.
- `units_avail` on `RawMaterial` is stored but not set from `class_args` at construction time (instances always start at 0).
- The old Tkinter UI files (`market/input/setup.py`, `market/input/runtime_ui.py`) are now unused.
