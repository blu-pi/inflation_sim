import json
import os
import sys
import threading
import webbrowser

from flask import Flask, jsonify, redirect, render_template, request, url_for

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from market.analytics.events import AttributeChange, ChangeEventType
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

app = Flask(__name__)

_graph_json: str | None = None
_node_map: dict = {}
_economy: Economy | None = None
_step_count: int = 0
_use_globals: bool = False

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
            'level': product.LAYER_NUM,  # raw→top (1), consumer→bottom (3)
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


def _reset_products() -> None:
    global _economy, _step_count, _use_globals
    Product.total_created = 0
    Economy.layers = Economy.LAYER_ARGS.copy()
    _economy = None
    _step_count = 0
    _use_globals = False


def _coerce(val: str, default):
    target = type(default)
    try:
        return target(val)
    except (ValueError, TypeError):
        return default


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
    return render_template('index.html', sections=sections)


@app.route('/run', methods=['POST'])
def run_simulation():
    global _graph_json, _node_map, _use_globals
    _reset_products()

    form = request.form
    arg_dicts: dict = {}
    for key, cls in ARG_CLASSES:
        defaults = cls({}).conts
        user_input: dict = {}
        for field, default in defaults.items():
            form_key = f'{key}.{field}'
            if type(default) is bool:
                user_input[field] = form_key in form  # checkbox: present=True, absent=False
            elif form_key in form and form[form_key] != '':
                user_input[field] = _coerce(form[form_key], default)
        arg_dicts[key] = cls(user_input)

    global _economy
    _economy = Economy(arg_dicts)
    _use_globals = arg_dicts["sim_args"].conts.get("use_globals", False)
    global_products = _economy.layers[GlobalMaterial].getMembers() if _use_globals else []
    _graph_json, _node_map = _serialize_graph(_economy.graph, global_products)
    return redirect(url_for('simulation'))


@app.route('/simulation')
def simulation():
    if _graph_json is None:
        return redirect(url_for('index'))
    return render_template('simulation.html')


@app.route('/api/graph')
def api_graph():
    if _graph_json is None:
        return jsonify({'error': 'No simulation running'}), 404
    return _graph_json, 200, {'Content-Type': 'application/json'}


@app.route('/api/timestep', methods=['POST'])
def api_timestep():
    global _step_count
    if _economy is None:
        return jsonify({'error': 'No simulation running'}), 404
    _economy.runNextTimeStep()
    _step_count += 1
    prices = {nid: product.sale_price for nid, product in _node_map.items()}
    return jsonify({'prices': prices, 'step': _step_count})


@app.route('/api/node/<path:node_id>/weights', methods=['POST'])
def update_weights(node_id):
    product = _node_map.get(node_id)
    if product is None:
        return jsonify({'error': 'Not found'}), 404
    if not product.hasComponents():
        return jsonify({'error': 'Product has no components'}), 400

    data = request.get_json(silent=True) or {}
    new_weights: dict = data.get('weights', {})

    updates = {}
    for comp_name, weight in new_weights.items():
        comp_product = _node_map.get(comp_name)
        if comp_product is not None and product.components.contains(comp_product):
            w = float(weight)
            if w > 0:
                updates[comp_product] = w

    if not updates:
        return jsonify({'error': 'No valid component weights provided'}), 400

    old_weights = {comp: product.components.getWeight(comp) for comp in updates}
    product.components.updateWeights(updates)

    for comp, new_w in updates.items():
        _economy.change_log.append(
            AttributeChange(_economy.current_time_step, ChangeEventType.WEIGHT_CHANGED,
                            product.name, product.layer.layer_name,
                            old_weights[comp], new_w, comp.name)
        )

    weights = product.components.getNormalisedWeights()
    return jsonify({'components': {c.getDisplayName(): round(w, 4) for c, w in weights.items()}})


@app.route('/api/node/<path:node_id>')
def api_node(node_id):
    product = _node_map.get(node_id)
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
        info['components'] = {
            c.getDisplayName(): round(w, 4) for c, w in weights.items()
        }
        info['components_abs'] = {
            c.getDisplayName(): round(w, 6) for c, w in abs_weights.items()
        }

    if isinstance(product, ConsumerProduct):
        raw_comp = product.deriveRawMaterialComposition()
        info['raw_composition'] = {
            c.getDisplayName(): round(w, 4) for c, w in raw_comp.items()
        }

    return jsonify(info)


@app.route('/api/globals')
def api_globals():
    if not _use_globals:
        return jsonify({'active': False, 'globals': []})
    return jsonify({
        'active': True,
        'globals': [
            {'id': g.getDisplayName(), 'name': g.name, 'unit_cost': g.unit_cost}
            for g in _economy.layers[GlobalMaterial].getMembers()
        ]
    })


def start(host='127.0.0.1', port=5000):
    print(f'Starting simulation server at http://{host}:{port}')
    threading.Timer(1.0, lambda: webbrowser.open(f'http://{host}:{port}')).start()
    app.run(host=host, port=port, debug=False, use_reloader=False)
