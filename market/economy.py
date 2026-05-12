
from market.graph import Graph
from market.input.sim_args import ArgDict

from market.products.base import Product
from market.products.composites import Composite
from market.products.consumer_goods import ConsumerProduct
from market.products.globals import GlobalMaterial
from market.products.processed import ProcessedMaterial
from market.products.product_layer import Layer
from market.products.raw_materials import RawMaterial
from market.products.types import AnyComposite, AnyProduct


class Economy:
    """
    The creator and manager of the economy. Responsible for creating products, organising them into layers, and connecting them together to create a supply chain.
    """
    #layer creation order: Globals, Raw, Processed, Consumer
    #consider renaming
    LAYER_ARGS = {
        GlobalMaterial : "global_args",
        RawMaterial : "raw_args",
        ProcessedMaterial : "processed_args",
        ConsumerProduct : "consumer_args"
    }
    #Dictionaries do preserve insertion order so this is fine. Will be used to create layers in correct order and assign args to correct product types.


    def __init__(self, arg_dicts : dict[str,ArgDict]) -> None:
        self.sim_args = arg_dicts["sim_args"].conts
        self.layers = Economy.LAYER_ARGS.copy()
        self.num_products = 0
        #TODO handle args for abstract product types (if even needed)
        self.createLayers(arg_dicts)
        self.connectAllLayers()
        self.layers : dict[AnyProduct, Layer]

    def createLayers(self, node_args : dict[str,ArgDict]) -> None:
        """
        Create all instances of products and organise into layers based on what type of Product they are.
        Layers represent essentially 1 step of production in the economy.
        """
        for material_type, arg_key in Economy.LAYER_ARGS.items():
            material_type : AnyProduct
            material_args = node_args[arg_key].conts
            layer_size = material_args["layer_size"]
            material_type.class_args = material_args #is needed?
            layer_members : list[AnyProduct] = [] 
            #print("{} given args : {}".format(material_type, material_args)) #DEBUG

            for i in range(layer_size):
                layer_name : str = material_type.getLayerName()
                material_args.update({"name" : f"{layer_name}{i}"}) 
                layer_members.append(material_type(**material_args)) #mutable type constructor call. Feels sketchy
                self.num_products += 1

            #Replace values stored in class attr. so it stores created Layer objs.
            self.layers.update({material_type : Layer(layer_name, layer_members.copy())}) 


    def connectAllLayers(self) -> None:
        """
        Assigns material composition of composite products to make a supply chain. 
        This 'connects' various products from different layers with each other directly.
        Causes indirect connections within a layer through competition over supply and/or customers.
        """
        consumer_layer : Layer = self.layers[ConsumerProduct]
        processed_layer : Layer = self.layers[ProcessedMaterial]
        raw_layer : Layer = self.layers[RawMaterial]

        consumer_layer.connect(processed_layer)
        processed_layer.connect(raw_layer)
        if self.sim_args["use_globals"]:
            GlobalMaterial.publishGlobalProducts() 

        self.graph = Graph(consumer_layer)


    def runNextTimeStep(self) -> None:
        """Runs the next time step of the economy. Each layer makes decisions and transactions sequentially."""
        #for supply side time-steps, run layers in creation order. For demand side time-steps, run layers in reverse creation order. For now, only supply side time-steps are implemented.
        for layer in self.layers.values():
            if isinstance(layer.products[0], GlobalMaterial):
                continue #globals aren't 'intelligent' and don't ever make 'decisions'. 
            layer.makeDecisions()