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
GlobalMaterial    (layer 0)  — Energy, Labour (implicit cost shared by every product)
RawMaterial       (layer 1)  — base inputs
ProcessedMaterial (layer 2)  — made from RawMaterials (Composite)
ConsumerProduct   (layer 3)  — made from ProcessedMaterials (Composite)
```

`GlobalMaterial` instances are deliberately not connected to other nodes by edges — they are not direct components of any specific product. Instead, every non-Global product pays their combined `unit_cost` as an implicit processing cost via `findGlobalCost()`. GlobalMaterials have no `Strategy` and never make decisions, but they influence the decisions of all other products by raising their total cost.

`Economy` ([market/economy.py](market/economy.py)) is the top-level orchestrator. It creates all product instances, organizes them into `Layer` objects, then calls `connectAllLayers()` which runs `SymmetricalConnection` between adjacent layers and (when `use_globals` is enabled) calls `layer.wireGlobals()` on every non-Global layer. The resulting `Graph` is stored as `self.graph` for the web layer to consume. `Economy.runNextTimeStep()` advances all non-Global layers sequentially; GlobalMaterial is always skipped.

`Layer` ([market/products/product_layer.py](market/products/product_layer.py)) manages a collection of products. After creation, `Layer.wireMembers()` assigns each product its `_id` (unique within the layer) and a back-reference to the `Layer` instance via `product.layer`. When globals are active, `Layer.wireGlobals(global_materials)` calls `product.setGlobalMaterials()` on every member, giving each product its list of `GlobalMaterial` instances as an instance attribute. Products access their layer-mates via `self.layer.getMembers()`.

`SymmetricalConnection` ([market/products/structs/layer_connection.py](market/products/structs/layer_connection.py)) enforces that every parent-layer product appears in at least one child's components, and that each child has approximately `num_preferred_components` parents. It randomly assigns connections while tracking frequency to stay balanced.

`ComponentDict` ([market/products/structs/components.py](market/products/structs/components.py)) stores composition as absolute (non-normalized) weights internally. Call `getNormalisedWeights()` for analysis — normalization is deferred to avoid floating-point accumulation in the simulation. `getTotalPrice()` is the lightweight runtime method (linear lookup of cached `sale_price`); `getTotalCost()` is the expensive recursive alternative used only for analysis.

`ConsumerProduct.deriveRawMaterialComposition()` ([market/products/consumer_goods.py](market/products/consumer_goods.py)) recursively walks the two-level hierarchy to compute a normalized flat mapping of raw materials → proportional contribution.

### Behaviour & Strategy system

Each `Product` holds a `Strategy` instance assigned in `__init__`. The default is `SimpleSupplySideStrategy` ([market/products/behaviour/strategy.py](market/products/behaviour/strategy.py)), which wraps `SimpleSupply` and no demand behaviour. On each time step, `Layer.makeDecisions()` calls `product.applyStrategy()` → `strategy.apply()` → `supply_behaviour.calcSupplyPrice()` → `product.publishSalePrice(price)`.

- `SimpleSupply.calcSupplyPrice()` returns `product.findTotalCost()` — unit_cost + component prices + global material costs (summed via `findGlobalCost()`, which iterates `product.global_members`).
- `DemandBehaviour` / `SimpleDemand` exist but are not yet wired in (`makePurchaseDecision` is a stub).
- `AdaptiveStrategy` is a placeholder for future goal-oriented / learning behaviour.

`Simulation` ([market/simulation.py](market/simulation.py)) is a thin wrapper around `Economy` that tracks `current_time_step`. The web layer currently calls `Economy.runNextTimeStep()` directly rather than going through `Simulation`.

## Configuration Flow

`main.py` calls `web.app.start()`. The Flask app at [web/app.py](web/app.py) serves a parameter form at `/`, collects user input, and POSTs to `/run` which instantiates `Economy` and redirects to `/simulation`.

Each `ArgDict` subclass (in [market/input/sim_args.py](market/input/sim_args.py)) holds a `DEFAULTS` dict. User input is merged with `|` (Python 3.9+), so any unset field falls back to its default. The web form auto-generates fields from the type of each default value (bool → checkbox, int/float → number input, list → select, str → text). Help text is loaded from [util/arg_info.txt](util/arg_info.txt) and shown as hover tooltips.

**Multi-run state:** Products no longer use class-level `_existing` lists; instances are tracked only within the `Layer` objects owned by `Economy`. `_reset_products()` in `web/app.py` resets `Product.total_created`, clears `Economy.layers` back to `LAYER_ARGS`, and nulls `_economy` / `_step_count` / `_use_globals` before each run so IDs restart cleanly.

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

`_serialize_graph()` maps each product to a vis.js node using `product.getDisplayName()` as the string ID (format: `"LayerName: {_id}"`). When `use_globals` is true, GlobalMaterial nodes are added at level 0 with no edges and registered in `_node_map`.

## Visualization

`Graph` ([market/graph.py](market/graph.py)) builds a NetworkX `DiGraph` by traversing product components. Nodes are product instances; edges go child→parent.

The web UI (`simulation.html`) uses **vis.js Network** (CDN) with a hierarchical top-down layout. Clicking a node highlights its edges (incoming=blue, outgoing=green) and populates the sidebar. The toolbar provides Reset View, Export PNG, and **Next Step** (calls `/api/timestep` and updates node labels with the new sale price).

The sidebar shows node properties, component weights (editable for Composites), raw material composition (Consumer only), and global material costs (when `use_globals` is active).

## In Progress

**Multiple economies / Simulation class**
The `Simulation` class is being promoted to a first-class controller that manages one or more `Economy` instances and exposes them to the user. Two state-capture mechanisms are planned:

- **Snapshot** — lightweight read of an economy's current state (prices, costs, layer composition). Used for metrics and comparison between points in time. Does not copy or duplicate the economy.
- **Checkpoint** — deep fork of an existing economy that produces an independent copy. The forked economy can then diverge over subsequent time steps, enabling side-by-side comparison of different intervention scenarios.

## Known Incomplete Features

- `units_avail` on `RawMaterial` is stored but not set from `class_args` at construction time (instances always start at 0).
- `DemandBehaviour` / `SimpleDemand` exist but `makePurchaseDecision` is a stub — demand-side time steps are not implemented.
- `AdaptiveStrategy` is a placeholder with no logic.
- The web layer still calls `Economy.runNextTimeStep()` directly; multi-economy control via `Simulation` is in progress (see above).
- The old Tkinter UI files (`market/input/setup.py`, `market/input/runtime_ui.py`) are now unused.
