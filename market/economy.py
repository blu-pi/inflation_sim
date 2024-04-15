from market.products.consumer_goods import ConsumerProduct
from market.products.globals import GlobalMaterial
from market.products.processed import ProcessedMaterial
from market.products.product_layer import Layer
from market.products.raw_materials import RawMaterial


class Economy:
    #layer creation order: Globals, Raw, Processed, Consumer
    LAYER_ARGS = {
        GlobalMaterial : "global_args",
        RawMaterial : "raw_args",
        ProcessedMaterial : "processed_args",
        ConsumerProduct : "consumer_args"
    }

    layers = []

    def __init__(self, sim_args, node_args) -> None:
        
        self.sim_args = sim_args.conts

        for material, arg_key in Economy.LAYER_ARGS.items():
            material_args = node_args[arg_key]
            layer_size = material_args["layer_size"]
            for x in range(layer_size):
                material.__init__()
            Economy.layers.append(Layer(material.getLayerName(), material.getAll()))
        #MAKE PRODUCT OBJS
        #CREATE LAYER FOR OBJS
        #RUN SIM
        pass