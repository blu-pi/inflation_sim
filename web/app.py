import json
import os
import sys
import threading
import webbrowser

from flask import Flask, jsonify, redirect, render_template, request, url_for

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from market.analytics.events import AttributeChange, ChangeEvent, ChangeEventType, GraphStructureChange
from market.analytics.snapshot import EconomySnapshot
from market.economy import Economy
from market.graph import Graph
from market.input.sim_args import (
    CompositeArgs, ConsumerArgs, GlobalsArgs,
    ProcessedArgs, ProductArgs, RawArgs, SimArgs,
)
from market.products.base import Product
from market.products.consumer_goods import ConsumerProduct
from market.products.globals import GlobalMaterial
from market.products.raw_materials import RawMaterial
from market.simulation import Simulation

app = Flask(__name__)

_simulation: Simulation = Simulation()
# per-economy serialised graph caches
_graph_cache: dict[int, tuple[str, dict]] = {}

ARG_CLASSES: list[tuple] = [
    ('sim_args',       SimArgs),
    ('product_args',   ProductArgs),
    ('composite_args', CompositeArgs),
    ('global_args',    GlobalsArgs),
    ('raw_args',       RawArgs),
    ('processed_args', ProcessedArgs),
    ('consumer_args',  ConsumerArgs),
]


def _load_arg_info() -> dict:
    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'util', 'arg_info.txt',
    )
    info: dict = {}
    with open(path) as f:
        section = None
        for line in f:
            line = line.strip()
            if '#section' in line:
                section = line.split()[-1]
                info[section] = {}
            elif '#argument' in line and section:
                parts = line.replace('#argument', '').strip().split(':', 1)
                if len(parts) == 2:
                    info[section][parts[0].strip()] = parts[1].strip()
    return info


ARG_INFO = _load_arg_info()


def _serialize_graph(graph: Graph, global_products: list = None) -> tuple[str, dict]:
    node_map: dict = {}
    nodes: list = []
    edges: list = []
    layer_groups = {0: 'global', 1: 'raw', 2: 'processed', 3: 'consumer'}

    for product in graph.nxg.nodes():
        nid = product.getDisplayName()
        node_map[nid] = product
        nodes.append({
            'id': nid,
            'label': nid,
            'group': layer_groups.get(product.LAYER_NUM, 'unknown'),
            'level': product.LAYER_NUM,
        })

    for src, dst in graph.nxg.edges():
        sid, did = src.getDisplayName(), dst.getDisplayName()
        edges.append({'id': f'{sid}->{did}', 'from': sid, 'to': did})

    if global_products:
        for product in global_products:
            nid = product.getDisplayName()
            node_map[nid] = product
            nodes.append({
                'id': nid,
                'label': nid,
                'group': 'global',
                'level': 0,
            })

    return json.dumps({'nodes': nodes, 'edges': edges}), node_map


def _cache_graph(economy: Economy) -> None:
    use_globals = economy.sim_args.get("use_globals", False)
    global_products = economy.layers[GlobalMaterial].getMembers() if use_globals else []
    _graph_cache[economy.id] = _serialize_graph(economy.graph, global_products)


def _coerce(val: str, default):
    target = type(default)
    try:
        return target(val)
    except (ValueError, TypeError):
        return default


def _get_economy_or_404(economy_id: int):
    economy = _simulation.getEconomyById(economy_id)
    if economy is None:
        return None, (jsonify({'error': 'Economy not found'}), 404)
    return economy, None


def _get_group_or_404(group_id: int):
    group = _simulation.getGroupById(group_id)
    if group is None:
        return None, (jsonify({'error': 'Group not found'}), 404)
    return group, None


def _node_map_for(economy_id: int) -> dict:
    cached = _graph_cache.get(economy_id)
    return cached[1] if cached else {}


def _serialize_change_event(event: ChangeEvent) -> dict:
    payload = {
        'timestamp': event.timestamp,
        'event_type': event.event_type.value,
        'product_name': event.product_name,
        'layer_name': event.layer_name,
    }
    if isinstance(event, AttributeChange):
        payload['old_value'] = event.old_value
        payload['new_value'] = event.new_value
        payload['component_name'] = event.component_name
    elif isinstance(event, GraphStructureChange):
        payload['other_product'] = event.other_product
        payload['other_layer'] = event.other_layer
    return payload


def _serialize_snapshot(snapshot: EconomySnapshot) -> dict:
    layer_insights = {}
    for layer_name, stats in snapshot.layer_insights.items():
        layer_insights[layer_name] = {
            'layer_name': stats.layer_name,
            'product_count': stats.product_count,
            'mean_price': stats.mean_price,
            'std_dev_price': stats.std_dev_price,
            'min_price': stats.min_price,
            'max_price': stats.max_price,
            'mean_unit_cost': stats.mean_unit_cost,
        }
    records = {}
    for layer_name, layer_records in snapshot.record_dict.items():
        records[layer_name] = [
            {
                'name': r.name,
                'layer_name': r.layer_name,
                'id': r.id,
                'sale_price': r.sale_price,
                'unit_cost': r.unit_cost,
                'component_weights': r.component_weights,
            }
            for r in layer_records
        ]
    return {
        'timestamp': snapshot.timestamp,
        'layer_insights': layer_insights,
        'records': records,
    }


def _prices_for(node_map: dict) -> dict:
    return {
        nid: product.sale_price
        for nid, product in node_map.items()
        if getattr(product, 'sale_price', None) is not None
    }


@app.route('/')
def index():
    sections = []
    for key, cls in ARG_CLASSES:
        instance = cls({})
        if not instance.conts:
            continue
        fields = []
        for field_name, default in instance.conts.items():
            fields.append({
                'name': field_name,
                'form_name': f'{key}.{field_name}',
                'default': default,
                'type': type(default).__name__,
                'tooltip': ARG_INFO.get(key, {}).get(field_name, ''),
            })
        sections.append({
            'key': key,
            'title': key.replace('_', ' ').title(),
            'fields': fields,
        })
    has_simulation = len(_simulation.economies) > 0
    group_id_raw = request.args.get('group_id', '').strip()
    attach_group = None
    if group_id_raw.isdigit():
        group = _simulation.getGroupById(int(group_id_raw))
        if group is not None:
            attach_group = {'id': group.id, 'name': group.name}
    return render_template('index.html', sections=sections,
                           has_simulation=has_simulation, attach_group=attach_group)


@app.route('/run', methods=['POST'])
def run_simulation():
    form = request.form
    arg_dicts: dict = {}
    for key, cls in ARG_CLASSES:
        defaults = cls({}).conts
        user_input: dict = {}
        for field, default in defaults.items():
            form_key = f'{key}.{field}'
            if type(default) is bool:
                user_input[field] = form_key in form
            elif form_key in form and form[form_key] != '':
                user_input[field] = _coerce(form[form_key], default)
        arg_dicts[key] = cls(user_input)

    group_id_raw = form.get('attach_to_group', '').strip()
    group_id = int(group_id_raw) if group_id_raw.isdigit() else None

    economy = _simulation.createEconomy(arg_dicts, group_id=group_id)
    _cache_graph(economy)
    return redirect(url_for('simulation_view'))


@app.route('/sim_view')
def simulation_view():
    return render_template('simulation_view.html')


@app.route('/economy/<int:economy_id>')
def economy_view(economy_id):
    economy, err = _get_economy_or_404(economy_id)
    if err:
        return redirect(url_for('simulation_view'))
    return render_template('simulation.html', economy_id=economy_id, economy_name=economy.name)


@app.route('/api/simulation')
def api_simulation():
    """Return the full simulation state: groups, their members, and timestep counts."""
    groups_payload = []
    for group in _simulation.economy_groups:
        members = []
        for economy in group.members:
            # On a fork, hide annotations <= creation_step — those are the
            # entries inherited from the parent via deepcopy, and we render
            # them only on the parent's lane to avoid duplication.
            fork_cutoff = economy.creation_step if economy.parent_id is not None else None
            change_counts: dict[int, int] = {}
            for event in economy.change_log:
                if fork_cutoff is not None and event.timestamp <= fork_cutoff:
                    continue
                change_counts[event.timestamp] = change_counts.get(event.timestamp, 0) + 1
            snapshot_steps = [
                step for step in sorted(economy.snapshots.keys())
                if fork_cutoff is None or step > fork_cutoff
            ]
            members.append({
                'id': economy.id,
                'name': economy.name,
                'current_step': economy.current_time_step,
                'use_globals': economy.sim_args.get('use_globals', False),
                'snapshot_steps': snapshot_steps,
                'change_counts': change_counts,
                'parent_id': economy.parent_id,
                'creation_step': economy.creation_step,
            })
        groups_payload.append({
            'id': group.id,
            'name': group.name,
            'color': group.color,
            'members': members,
        })
    return jsonify({'groups': groups_payload})


@app.route('/api/economy/<int:economy_id>/graph')
def api_economy_graph(economy_id):
    economy, err = _get_economy_or_404(economy_id)
    if err:
        return err
    if economy_id not in _graph_cache:
        _cache_graph(economy)
    return _graph_cache[economy_id][0], 200, {'Content-Type': 'application/json'}


@app.route('/api/economy/<int:economy_id>/prices')
def api_economy_prices(economy_id):
    economy, err = _get_economy_or_404(economy_id)
    if err:
        return err
    node_map = _node_map_for(economy_id)
    return jsonify({'prices': _prices_for(node_map), 'step': economy.current_time_step})


@app.route('/api/economy/<int:economy_id>/timestep', methods=['POST'])
def api_economy_timestep(economy_id):
    economy, err = _get_economy_or_404(economy_id)
    if err:
        return err
    economy.runNextTimeStep()
    node_map = _node_map_for(economy_id)
    return jsonify({'prices': _prices_for(node_map), 'step': economy.current_time_step})


@app.route('/api/economy/<int:economy_id>/fork', methods=['POST'])
def api_economy_fork(economy_id):
    economy, err = _get_economy_or_404(economy_id)
    if err:
        return err
    clone = _simulation.forkEconomy(economy)
    _cache_graph(clone)
    return jsonify({
        'id': clone.id,
        'name': clone.name,
        'parent_id': clone.parent_id,
        'creation_step': clone.creation_step,
    })


@app.route('/api/economy/<int:economy_id>/snapshot', methods=['POST'])
def api_economy_create_snapshot(economy_id):
    economy, err = _get_economy_or_404(economy_id)
    if err:
        return err
    snapshot = economy.snapshot()
    return jsonify({'step': snapshot.timestamp})


@app.route('/api/economy/<int:economy_id>/snapshot/<int:step>')
def api_economy_read_snapshot(economy_id, step):
    economy, err = _get_economy_or_404(economy_id)
    if err:
        return err
    snapshot = economy.snapshots.get(step)
    if snapshot is None:
        return jsonify({'error': 'Snapshot not found'}), 404
    return jsonify(_serialize_snapshot(snapshot))


@app.route('/api/economy/<int:economy_id>/changelog')
def api_economy_changelog(economy_id):
    economy, err = _get_economy_or_404(economy_id)
    if err:
        return err
    step_filter = request.args.get('step', '').strip()
    events = economy.change_log
    if step_filter.isdigit():
        target = int(step_filter)
        events = [e for e in events if e.timestamp == target]
    return jsonify({'events': [_serialize_change_event(e) for e in events]})


@app.route('/api/economy/<int:economy_id>/node/<path:node_id>')
def api_economy_node(economy_id, node_id):
    economy, err = _get_economy_or_404(economy_id)
    if err:
        return err
    node_map = _node_map_for(economy_id)
    product = node_map.get(node_id)
    if product is None:
        return jsonify({'error': 'Not found'}), 404

    layer_names = {0: 'Global', 1: 'Raw Material', 2: 'Processed Material', 3: 'Consumer Product'}
    info = {
        'name': product.name,
        'layer': layer_names.get(product.LAYER_NUM, f'Layer {product.LAYER_NUM}'),
        'id': product.getId(),
        'unit_cost': product.unit_cost,
        'sale_price': product.sale_price,
    }

    if isinstance(product, RawMaterial):
        info['units_avail'] = product.units_avail

    if product.hasComponents():
        weights = product.components.getNormalisedWeights()
        abs_weights = product.components.getDict()
        info['num_components'] = len(weights)
        info['components'] = {c.getDisplayName(): round(w, 4) for c, w in weights.items()}
        info['components_abs'] = {c.getDisplayName(): round(w, 6) for c, w in abs_weights.items()}

    if isinstance(product, ConsumerProduct):
        raw_comp = product.deriveRawMaterialComposition()
        info['raw_composition'] = {c.getDisplayName(): round(w, 4) for c, w in raw_comp.items()}

    return jsonify(info)


@app.route('/api/economy/<int:economy_id>/node/<path:node_id>/weights', methods=['POST'])
def api_economy_update_weights(economy_id, node_id):
    economy, err = _get_economy_or_404(economy_id)
    if err:
        return err
    node_map = _node_map_for(economy_id)
    product = node_map.get(node_id)
    if product is None:
        return jsonify({'error': 'Not found'}), 404
    if not product.hasComponents():
        return jsonify({'error': 'Product has no components'}), 400

    data = request.get_json(silent=True) or {}
    new_weights: dict = data.get('weights', {})

    updates = {}
    for comp_name, weight in new_weights.items():
        comp_product = node_map.get(comp_name)
        if comp_product is not None and product.components.contains(comp_product):
            w = float(weight)
            if w > 0:
                updates[comp_product] = w

    if not updates:
        return jsonify({'error': 'No valid component weights provided'}), 400

    old_weights = {comp: product.components.getWeight(comp) for comp in updates}
    product.components.updateWeights(updates)

    for comp, new_w in updates.items():
        economy.change_log.append(
            AttributeChange(economy.current_time_step, ChangeEventType.WEIGHT_CHANGED,
                            product.name, product.layer.layer_name,
                            old_weights[comp], new_w, comp.name)
        )

    weights = product.components.getNormalisedWeights()
    return jsonify({'components': {c.getDisplayName(): round(w, 4) for c, w in weights.items()}})


@app.route('/api/economy/<int:economy_id>/node/<path:node_id>/unit_cost', methods=['POST'])
def api_economy_update_unit_cost(economy_id, node_id):
    economy, err = _get_economy_or_404(economy_id)
    if err:
        return err
    node_map = _node_map_for(economy_id)
    product = node_map.get(node_id)
    if product is None:
        return jsonify({'error': 'Not found'}), 404

    data = request.get_json(silent=True) or {}
    try:
        new_cost = float(data.get('unit_cost'))
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid unit_cost'}), 400
    if new_cost < 0:
        return jsonify({'error': 'Unit cost must be non-negative'}), 400

    old_cost = product.unit_cost
    product.setUnitCost(new_cost)

    economy.change_log.append(
        AttributeChange(economy.current_time_step, ChangeEventType.UNIT_COST_CHANGED,
                        product.name, product.layer.layer_name, old_cost, new_cost)
    )

    return jsonify({'unit_cost': product.unit_cost})


@app.route('/api/economy/<int:economy_id>/globals')
def api_economy_globals(economy_id):
    economy, err = _get_economy_or_404(economy_id)
    if err:
        return err
    use_globals = economy.sim_args.get('use_globals', False)
    if not use_globals:
        return jsonify({'active': False, 'globals': []})
    return jsonify({
        'active': True,
        'globals': [
            {'id': g.getDisplayName(), 'name': g.name, 'unit_cost': g.unit_cost}
            for g in economy.layers[GlobalMaterial].getMembers()
        ]
    })


@app.route('/api/group/<int:group_id>/timestep', methods=['POST'])
def api_group_timestep(group_id):
    group, err = _get_group_or_404(group_id)
    if err:
        return err
    _simulation.runNextGroupTimeStep(group)
    member_steps = {economy.id: economy.current_time_step for economy in group.members}
    return jsonify({'group_id': group_id, 'member_steps': member_steps})


@app.route('/api/group/<int:group_id>/color', methods=['POST'])
def api_group_color(group_id):
    group, err = _get_group_or_404(group_id)
    if err:
        return err
    data = request.get_json(silent=True) or {}
    color = data.get('color', '').strip()
    if not color:
        return jsonify({'error': 'Missing color'}), 400
    group.setColor(color)
    return jsonify({'group_id': group_id, 'color': group.color})


@app.route('/api/group/<int:group_id>/name', methods=['POST'])
def api_group_name(group_id):
    group, err = _get_group_or_404(group_id)
    if err:
        return err
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Missing name'}), 400
    group.setName(name)
    return jsonify({'group_id': group_id, 'name': group.name})


def start(host='127.0.0.1', port=5000):
    print(f'Starting simulation server at http://{host}:{port}')
    threading.Timer(1.0, lambda: webbrowser.open(f'http://{host}:{port}')).start()
    app.run(host=host, port=port, debug=False, use_reloader=False)
