# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Simulation

```bash
python main.py
```

This starts a Flask web server at `http://127.0.0.1:5000` and opens it in the browser automatically. The landing page (`/`) is a parameter form for creating an economy. After submission the user is redirected to `/sim_view`, a timeline showing every economy that has been created in this session organised into `EconomyGroup` lanes. Clicking a group's latest-step node opens that economy's interactive supply chain graph.

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

`Economy` ([market/economy.py](market/economy.py)) is the top-level orchestrator for a single economy. It creates all product instances, organizes them into `Layer` objects, then calls `connectAllLayers()` which runs `SymmetricalConnection` between adjacent layers and (when `use_globals` is enabled) calls `layer.wireGlobals()` on every non-Global layer. The resulting `Graph` is stored as `self.graph` for the web layer to consume. Each `Economy` carries its own `current_time_step`, `change_log` (list of `ChangeEvent`), and `snapshots` (`dict[step, EconomySnapshot]`). `Economy.runNextTimeStep()` advances all non-Global layers sequentially and increments `current_time_step`; GlobalMaterial is always skipped. `Economy.snapshot()` captures current state into `self.snapshots[current_time_step]`. The `id` field is `None` until `Simulation.registerEconomy()` assigns one.

`Layer` ([market/products/product_layer.py](market/products/product_layer.py)) manages a collection of products. After creation, `Layer.wireMembers()` assigns each product its `_id` (unique within the layer) and a back-reference to the `Layer` instance via `product.layer`. When globals are active, `Layer.wireGlobals(global_materials)` calls `product.setGlobalMaterials()` on every member, giving each product its list of `GlobalMaterial` instances as an instance attribute. Products access their layer-mates via `self.layer.getMembers()`.

`SymmetricalConnection` ([market/products/structs/layer_connection.py](market/products/structs/layer_connection.py)) enforces that every parent-layer product appears in at least one child's components, and that each child has approximately `num_preferred_components` parents. It randomly assigns connections while tracking frequency to stay balanced.

`ComponentDict` ([market/products/structs/components.py](market/products/structs/components.py)) stores composition as absolute (non-normalized) weights internally. Call `getNormalisedWeights()` for analysis — normalization is deferred to avoid floating-point accumulation in the simulation. `getTotalPrice()` is the lightweight runtime method (linear lookup of cached `sale_price`); `getTotalCost()` is the expensive recursive alternative used only for analysis.

`ConsumerProduct.deriveRawMaterialComposition()` ([market/products/consumer_goods.py](market/products/consumer_goods.py)) recursively walks the two-level hierarchy to compute a normalized flat mapping of raw materials → proportional contribution.

### Behaviour & Strategy system

Each `Product` holds a `Strategy` instance assigned in `__init__`. The default is `SimpleSupplySideStrategy` ([market/products/behaviour/strategy.py](market/products/behaviour/strategy.py)), which wraps `SimpleSupply` and no demand behaviour. On each time step, `Layer.makeDecisions()` calls `product.applyStrategy()` → `strategy.apply()` → `supply_behaviour.calcSupplyPrice()` → `product.publishSalePrice(price)`.

- `SimpleSupply.calcSupplyPrice()` returns `product.findTotalCost()` — unit_cost + component prices + global material costs (summed via `findGlobalCost()`, which iterates `product.global_members`).
- `DemandBehaviour` / `SimpleDemand` exist but are not yet wired in (`makePurchaseDecision` is a stub).
- `AdaptiveStrategy` is a placeholder for future goal-oriented / learning behaviour.

### Simulation & EconomyGroup

`Simulation` ([market/simulation.py](market/simulation.py)) is a first-class controller that owns every `Economy` created in the current session. It assigns each economy a unique `id` via `registerEconomy()`, and exposes lookup helpers (`getEconomyById`, `getGroupById`, `getGroupForEconomy`). Use `Simulation.createEconomy(arg_dicts, group_id=...)` to create-and-register in one call; if `group_id` is omitted a fresh single-member group is created. `runNextGroupTimeStep(group)` advances every member of a group by one step.

`EconomyGroup` ([market/simulation.py](market/simulation.py)) bundles related economies together with a display `name` and `color` so the timeline UI can render them as a lane and step them as a unit. Default group colors cycle through `DEFAULT_GROUP_COLORS`. Groups support `setName`, `setColor`, `addMember`, and `absorbGroup` (merge two groups). The web layer holds a single module-level `_simulation = Simulation()` so state persists across requests.

### Analytics

`market/analytics/events.py` defines the change-log event hierarchy:
- `ChangeEventType` — enum of `UNIT_COST_CHANGED`, `WEIGHT_CHANGED`, `VERTEX_ADDED`, `VERTEX_REMOVED`.
- `ChangeEvent` (base) — `timestamp`, `event_type`, `product_name`, `layer_name`.
- `AttributeChange` — adds `old_value`, `new_value`, `component_name` (used for weight / unit_cost edits).
- `GraphStructureChange` — adds `other_product`, `other_layer` (for future vertex add/remove events; not yet emitted).

Events are appended to `Economy.change_log` by the web routes that mutate state (currently `/weights` and `/unit_cost`). Products and `ComponentDict` have no reference to `Economy`, so events are emitted from the call site rather than from inside the mutation methods — programmatic changes made outside the web layer will not be logged.

`market/analytics/snapshot.py` provides read-only state capture:
- `ProductRecord` — per-product fields (`name`, `layer_name`, `id`, `sale_price`, `unit_cost`, optional `component_weights` keyed by product name with normalized values).
- `LayerStats` — per-layer aggregates (`product_count`, `mean_price`, `std_dev_price`, `min_price`, `max_price`, `mean_unit_cost`). `LayerStats.createFromList(records)` computes these from a list of records.
- `EconomySnapshot` — built from a live `Economy` plus a `timestamp`. Walks `economy.layers`, builds `ProductRecord`s per non-Global layer into `record_dict[layer_name]`, and computes `LayerStats` into `layer_insights[layer_name]`. The live economy reference is intentionally not retained.

Snapshots are read-only by design — no deep fork is performed. The deep-fork mechanism (a "checkpoint" that produces an independent diverging economy) is still planned, see *In Progress*.

## Configuration Flow

`main.py` calls `web.app.start()`. The Flask app at [web/app.py](web/app.py) serves a parameter form at `/`, collects user input, and POSTs to `/run` which calls `Simulation.createEconomy()` and redirects to `/sim_view`.

Each `ArgDict` subclass (in [market/input/sim_args.py](market/input/sim_args.py)) holds a `DEFAULTS` dict. User input is merged with `|` (Python 3.9+), so any unset field falls back to its default. The web form auto-generates fields from the type of each default value (bool → checkbox, int/float → number input, list → select, str → text). Help text is loaded from [util/arg_info.txt](util/arg_info.txt) and shown as hover tooltips.

`SimArgs` includes `economy_name` (display name shown in timeline lanes and modals) and `use_globals`. Each non-Globals layer args dict has its own `layer_size`; processed/consumer layers also expose `num_preferred_components`.

**Multi-run state:** Products do not use class-level instance lists; every product belongs to exactly one `Layer` owned by exactly one `Economy`. Multiple economies coexist independently within `Simulation.economies`. The web form's optional `attach_to_group` field (set via the `?group_id=` query param on `/`) lets a new economy attach to an existing group instead of starting a new lane.

## Web Layer (`web/`)

Flask routes (all economy-scoped routes use the integer `economy_id` assigned by `Simulation`):

Pages:
- `GET /` — parameter form (renders `index.html`). Optional `?group_id=N` pre-selects which group the new economy will attach to.
- `POST /run` — creates an Economy via `Simulation.createEconomy(...)`, caches its serialised graph in `_graph_cache[economy_id]`, redirects to `/sim_view`.
- `GET /sim_view` — top-level timeline of all groups/economies/steps (`simulation_view.html`).
- `GET /economy/<int:economy_id>` — interactive graph viewer for a specific economy (`simulation.html`).

Simulation-level API:
- `GET /api/simulation` — full state: `{groups: [{id, name, color, members: [{id, name, current_step, use_globals, snapshot_steps, change_counts}, ...]}, ...]}`.

Economy-scoped API (all prefixed `/api/economy/<id>/...`):
- `GET /graph` — vis.js-compatible JSON for the economy's supply chain.
- `GET /prices` — `{prices: {nodeId: sale_price}, step: current_time_step}`.
- `POST /timestep` — advances this economy one step; returns updated prices and step.
- `POST /snapshot` — captures the current state into `economy.snapshots[step]`; returns `{step}`.
- `GET /snapshot/<int:step>` — serialised snapshot (`timestamp`, `layer_insights`, `records`).
- `GET /changelog?step=<n>` — change-events for this economy; optional `step` filter.
- `GET /node/<node_id>` — node attributes (same shape as before: `name`, `layer`, `id`, `unit_cost`, `sale_price`; plus `units_avail` for Raw, `num_components`/`components`/`components_abs` for Composites, `raw_composition` for Consumer).
- `POST /node/<node_id>/weights` — updates component weights for a Composite and appends one `AttributeChange(WEIGHT_CHANGED)` per modified component to `economy.change_log`.
- `POST /node/<node_id>/unit_cost` — updates a product's `unit_cost` (via `product.setUnitCost`) and appends an `AttributeChange(UNIT_COST_CHANGED)` event.
- `GET /globals` — `{active: bool, globals: [{id, name, unit_cost}]}`.

Group-scoped API (`/api/group/<id>/...`):
- `POST /timestep` — calls `Simulation.runNextGroupTimeStep(group)`; returns `{group_id, member_steps}`.
- `POST /color` — `{color}` updates the group's display color.
- `POST /name` — `{name}` renames the group.

`_serialize_graph()` maps each product to a vis.js node using `product.getDisplayName()` as the string ID (format: `"LayerName: {_id}"`). When `use_globals` is true, GlobalMaterial nodes are added at level 0 with no edges and registered in `_node_map`. Serialised graphs are cached per-economy in `_graph_cache[economy_id] = (json_string, node_map)`.

`_serialize_change_event()` and `_serialize_snapshot()` convert their respective objects into JSON-friendly dicts for the API.

## Visualization

`Graph` ([market/graph.py](market/graph.py)) builds a NetworkX `DiGraph` by traversing product components. Nodes are product instances; edges go child→parent.

There are two viewer pages:

**`simulation_view.html`** — session-level timeline. Each `EconomyGroup` is a horizontal canvas (color-coded by the group's `color`), and each member economy is a lane within it. The x-axis is time steps. Each step is a node on the lane; the latest step is clickable and opens that economy's graph view. Above each lane, an annotation row marks `snapshot_steps` with diamond markers and steps that have entries in `change_counts` with an orange "N changes" pill. Clicking a snapshot marker opens a modal with a Chart.js bar/line chart of `layer_insights` plus a stats table; clicking a changes pill opens a list of `ChangeEvent`s at that step. The header lets the user step a whole group (`Step All`), rename a group, recolor it, or add another economy to it.

**`simulation.html`** — per-economy graph viewer using **vis.js Network** (CDN) with a hierarchical top-down layout. Clicking a node highlights its edges (incoming=blue, outgoing=green) and populates the sidebar. The sidebar shows node properties, component weights (editable for Composites), raw material composition (Consumer only), and global material costs (when `use_globals` is active). The toolbar provides Reset View, Export PNG, and **Next Step** (calls `/api/economy/<id>/timestep`).

## In Progress

**Checkpoint (deep economy fork)** — `EconomySnapshot` captures observable state for read-only comparison but does *not* duplicate the economy. A separate `Checkpoint` mechanism is planned that deep-forks an `Economy` so the copy can diverge over subsequent time steps, enabling side-by-side comparison of different intervention scenarios. The `EconomyGroup` lane structure already exists in part to display these comparisons once forks are wired in.

**`SnapshotComparison`** — a standalone class (planned `market/analytics/comparison.py`) that takes two snapshots, matches products by `(layer_name, product_name)`, and reports price/cost deltas, edge diffs (reconstructed from `component_weights`), and per-layer aggregate deltas. Not yet implemented.

**Vertex add/remove events** — `GraphStructureChange` and `ChangeEventType.VERTEX_ADDED` / `VERTEX_REMOVED` are defined but no code path emits them yet.

## Known Incomplete Features

- `units_avail` on `RawMaterial` is stored but not set from `class_args` at construction time (instances always start at 0).
- `DemandBehaviour` / `SimpleDemand` exist but `makePurchaseDecision` is a stub — demand-side time steps are not implemented.
- `AdaptiveStrategy` is a placeholder with no logic.
- Change events are emitted from the web route layer only; programmatic mutations made outside the web layer will not be logged.
- The old Tkinter UI files (`market/input/setup.py`, `market/input/runtime_ui.py`) are now unused.
