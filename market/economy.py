
import copy

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
from market.analytics.snapshot import EconomySnapshot


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
        self.name = self.sim_args["economy_name"]
        self.layers = Economy.LAYER_ARGS.copy()
        self.num_products = 0
        self.current_time_step: int = 0
        self.change_log: list = []
        self.id : int = None #assigned by Simulation when registered
        self.parent_id : int = None #set by fork() on the clone; stays None for root economies
        self.creation_step : int = None #set by fork() on the clone; stays None for root economies
        #TODO handle args for abstract product types (if even needed)

        self.createLayers(arg_dicts)
        self.connectAllLayers()

        self.layers : dict[AnyProduct, Layer]
        self.snapshots : dict[int,EconomySnapshot] = {}

    def createLayers(self, node_args : dict[str,ArgDict]) -> None:
        """
        Create all instances of products and organise into layers based on what type of Product they are.
        Layers represent essentially 1 step of production in the economy.
        """
        for material_type, arg_key in Economy.LAYER_ARGS.items():
            material_type : AnyProduct
            abstract_product_args = node_args["product_args"].conts
            node_args[arg_key].joinConts(abstract_product_args)
            material_args = node_args[arg_key].conts
            layer_size = material_args["layer_size"]
            layer_members : list[AnyProduct] = [] 
            #print("{} given args : {}".format(material_type, material_args)) #DEBUG

            for i in range(layer_size):
                layer_name : str = material_type.getLayerName()
                material_args.update({"name" : f"{layer_name}{i}"}) 
                layer_members.append(material_type(**material_args)) #mutable type constructor call. Feels sketchy
                self.num_products += 1

            #Replace values stored in class attr. so it stores created Layer objs.
            layer : Layer = Layer(layer_name, layer_members.copy())
            layer.wireMembers() #gives each an id unique to other members in their layer
            self.layers.update({material_type : layer})


    def connectAllLayers(self) -> None:
        """
        Assigns material composition of composite products to make a supply chain. 
        This 'connects' various products from different layers with each other directly.
        Causes indirect connections within a layer through competition over supply and/or customers.
        """
        consumer_layer : Layer = self.layers[ConsumerProduct]
        processed_layer : Layer = self.layers[ProcessedMaterial]
        raw_layer : Layer = self.layers[RawMaterial]
        global_layer : Layer = self.layers[GlobalMaterial]

        consumer_layer.connect(processed_layer)
        processed_layer.connect(raw_layer)

        if self.sim_args["use_globals"]:
            global_materials = global_layer.products
            for product_type, layer in self.layers.items():
                if product_type is not GlobalMaterial:
                    layer.wireGlobals(global_materials)

        self.graph = Graph(consumer_layer)


    def runNextTimeStep(self) -> None:
        """Runs the next time step of the economy. Each layer makes decisions and transactions sequentially."""
        self.current_time_step += 1
        #for supply side time-steps, run layers in creation order. For demand side time-steps, run layers in reverse creation order. For now, only supply side time-steps are implemented.
        for layer in self.layers.values():
            if isinstance(layer.products[0], GlobalMaterial):
                continue #globals aren't 'intelligent' and don't ever make 'decisions'.
            layer.makeDecisions()
    
    def snapshot(self) -> EconomySnapshot:
        """
        Returns a snapshot of economy analytics at the current time step.   
        """
        snapshot = EconomySnapshot(self,self.current_time_step)
        self.snapshots.update({self.current_time_step : snapshot})
        return snapshot
    
    def fork(self, new_name : str = None) -> 'Economy':
        """
        Make a clone of an existing economy at current time-step using deepcopy().
        """
        clone = copy.deepcopy(self)
        clone.id = None
        clone.parent_id = self.id
        clone.creation_step = self.current_time_step
        if new_name is None:
            clone.name = f"{self.name} fork @t{clone.creation_step}"
        else:
            clone.name = new_name
        return clone