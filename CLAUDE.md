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
GlobalMaterial    (layer 0)  — Energy, Labour (implicit processing cost)
RawMaterial       (layer 1)  — base inputs
ProcessedMaterial (layer 2)  — made from RawMaterials (Composite)
ConsumerProduct   (layer 3)  — made from ProcessedMaterials (Composite)
```

`Economy` ([market/economy.py](market/economy.py)) is the top-level orchestrator. It creates all product instances, organizes them into `Layer` objects, then calls `connectAllLayers()` which runs `SymmetricalConnection` between adjacent layers. The resulting `Graph` is stored as `self.graph` for the web layer to consume. `Economy.runNextTimeStep()` advances all non-Global layers sequentially; GlobalMaterial is always skipped.

`SymmetricalConnection` ([market/products/structs/layer_connection.py](market/products/structs/layer_connection.py)) enforces that every parent-layer product appears in at least one child's components, and that each child has approximately `num_preferred_components` parents. It randomly assigns connections while tracking frequency to stay balanced.

`ComponentDict` ([market/products/structs/components.py](market/products/structs/components.py)) stores composition as absolute (non-normalized) weights internally. Call `getNormalisedWeights()` for analysis — normalization is deferred to avoid floating-point accumulation in the simulation. `getTotalPrice()` is the lightweight runtime method (linear lookup of cached `sale_price`); `getTotalCost()` is the expensive recursive alternative used only for analysis.

`ConsumerProduct.deriveRawMaterialComposition()` ([market/products/consumer_goods.py](market/products/consumer_goods.py)) recursively walks the two-level hierarchy to compute a normalized flat mapping of raw materials → proportional contribution.

### Behaviour & Strategy system

Each `Product` holds a `Strategy` instance assigned in `__init__`. The default is `SimpleSupplySideStrategy` ([market/products/behaviour/strategy.py](market/products/behaviour/strategy.py)), which wraps `SimpleSupply` and no demand behaviour. On each time step, `Layer.makeDecisions()` calls `product.applyStrategy()` → `strategy.apply()` → `supply_behaviour.calcSupplyPrice()` → `product.publishSalePrice(price)`.

- `SimpleSupply.calcSupplyPrice()` returns `product.findTotalCost()` — unit_cost + component prices + global material costs.
- `DemandBehaviour` / `SimpleDemand` exist but are not yet wired in (`makePurchaseDecision` is a stub).
- `AdaptiveStrategy` is a placeholder for future goal-oriented / learning behaviour.

`Simulation` ([market/simulation.py](market/simulation.py)) is a thin wrapper around `Economy` that tracks `current_time_step`. The web layer currently calls `Economy.runNextTimeStep()` directly rather than going through `Simulation`.

## Configuration Flow

`main.py` calls `web.app.start()`. The Flask app at [web/app.py](web/app.py) serves a parameter form at `/`, collects user input, and POSTs to `/run` which instantiates `Economy` and redirects to `/simulation`.

Each `ArgDict` subclass (in [market/input/sim_args.py](market/input/sim_args.py)) holds a `DEFAULTS` dict. User input is merged with `|` (Python 3.9+), so any unset field falls back to its default. The web form auto-generates fields from the type of each default value (bool → checkbox, int/float → number input, list → select, str → text). Help text is loaded from [util/arg_info.txt](util/arg_info.txt) and shown as hover tooltips.

**Multi-run state:** Product subclasses accumulate instances in class-level `_existing` lists. `_reset_products()` in `web/app.py` clears these and resets `Product.total_created` and `_use_globals` before each run so IDs restart cleanly.

## Web Layer (`web/`)

Flask routes:
- `GET /` — parameter form (renders `index.html` with sections built from `ARG_CLASSES`)
- `POST /run` — runs the simulation, stores `_graph_json`, `_node_map`, and `_use_globals` as module globals, redirects to `/simulation`
- `GET /simulation` — graph viewer page (`simulation.html`)
- `GET /api/graph` — returns vis.js-compatible JSON (`{nodes, edges}`)
- `GET /api/node/<id>` — returns node attributes: `name`, `layer`, `id`, `unit_cost`, `sale_price`; plus `units_avail` for Raw, `num_components`/`components`/`components_abs` for Composites, `raw_composition` for Consumer
- `POST /api/node/<id>/weights` — updates component weights for a Composite; accepts `{weights: {displayName: value}}` and returns updated normalized weights
- `POST /api/timestep` — advances simulation one step; returns `{prices, step}` where `prices` maps every node ID to its new `sale_price`
- `GET /api/globals` — returns `{active: bool, globals: [{id, name, unit_cost}]}`; `active` is true only when `use_globals` was checked at run time

`_serialize_graph()` maps each product to a vis.js node using `product.getDisplayName()` as the string ID (format: `"LayerName: {_id}"`). Level is `product.LAYER_NUM` so raw (1) appears near the top and consumer (3) at the bottom of the hierarchical layout. When `use_globals` is true, GlobalMaterial nodes are added at level 0 (above raw) with no edges, and registered in `_node_map` so they can be fetched via `/api/node/<id>`.

## Visualization

`Graph` ([market/graph.py](market/graph.py)) builds a NetworkX `DiGraph` by traversing product components. Nodes are product instances; edges go child→parent.

The web UI (`simulation.html`) uses **vis.js Network** (CDN) with a hierarchical top-down layout. Clicking a node highlights its edges (incoming=blue, outgoing=green) and populates the sidebar. The toolbar provides Reset View, Export PNG, and **Next Step** (calls `/api/timestep` and updates node labels with the new sale price).

**Sidebar sections on node click:**
- *Properties* — id, unit_cost, sale_price, units_avail (Raw only), # Components (Composites only)
- *Components* — bar chart of normalized weights with editable pie chart (Composites only); weights can be changed in absolute or percentage mode and POSTed via `/api/node/<id>/weights`
- *Raw Material Composition* — read-only pie chart of derived raw-material proportions (Consumer only)
- *Global Materials* — shown for all non-Global products when `use_globals` is active; lists each GlobalMaterial by name and its `unit_cost`; clicking a name selects that node in the graph and loads its Properties panel

**Component weight editor (pie chart):**
- Toggle with the "Pie" button on any Composite's Components section
- Two input modes: absolute (A column) and percentage (% column); switching between them syncs the other automatically
- Percentage mode requires the sum to equal 100% (±0.5%) before Apply is accepted

## Known Incomplete Features

- `use_globals` wires `GlobalMaterial` costs into `findTotalCost()` for all products, but globals are not connected via graph edges and do not participate in supply/demand decisions.
- `units_avail` on `RawMaterial` is stored but not set from `class_args` at construction time (instances always start at 0).
- `DemandBehaviour` / `SimpleDemand` exist but `makePurchaseDecision` is a stub — demand-side time steps are not implemented.
- `AdaptiveStrategy` is a placeholder with no logic.
- `Simulation` class exists but the web layer calls `Economy.runNextTimeStep()` directly.
- The old Tkinter UI files (`market/input/setup.py`, `market/input/runtime_ui.py`) are now unused.
