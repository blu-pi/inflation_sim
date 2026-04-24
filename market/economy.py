
from typing import TYPE_CHECKING

from market.graph import Graph
from market.products.base import Product
from market.products.composites import Composite
from market.products.consumer_goods import ConsumerProduct
from market.products.globals import GlobalMaterial
from market.products.processed import ProcessedMaterial
from market.products.product_layer import Layer
from market.products.raw_materials import RawMaterial

if TYPE_CHECKING:
   from market.input.sim_args import ArgDict


class Economy:
    """
    Economy is synonym for Simulation. Responsible for top-level simulation management.
    """
    #layer creation order: Globals, Raw, Processed, Consumer
    #consider renaming
    LAYER_ARGS = {
        GlobalMaterial : "global_args",
        RawMaterial : "raw_args",
        ProcessedMaterial : "processed_args",
        ConsumerProduct : "consumer_args"
    }
    #Dictionaries don't preserve ordering for keys anymore so this doesn't actually hardcode creation order.

    layers = LAYER_ARGS.copy()

    def __init__(self, arg_dicts : dict['ArgDict']) -> None:
        self.sim_args = arg_dicts["sim_args"].conts
        #setting args for abstracts
        Product.class_args = arg_dicts["product_args"].conts
        Composite.class_args = arg_dicts["composite_args"].conts
        self.createLayers(arg_dicts)
        self.connectAllLayers()

    def createLayers(self, node_args) -> None:
        """
        Create all instances of products and organise into layers based on what type of Product they are.
        Layers represent essentially 1 step of production in the economy.
        """
        for material_type, arg_key in Economy.LAYER_ARGS.items():
            material_args = node_args[arg_key].conts
            layer_size = material_args["layer_size"]
            material_type.class_args = material_args
            #print("{} given args : {}".format(material_type, material_args)) #DEBUG
            for x in range(layer_size):
                material_type() #mutable type constructor call. Feels sketchy
            Economy.layers.update({material_type : Layer(material_type.getLayerName(), material_type.getAll())})
            #Replace values stored in class attr. so it stores created Layer objs.

    def connectAllLayers(self) -> None:
        """
        Assigns material composition of composite products to make a supply chain. 
        This 'connects' various products from different layers with each other directly.
        Causes indirect connections within a layer through competition over supply and/or customers.
        """
        consumer_layer : Layer = Economy.layers[ConsumerProduct]
        processed_layer : Layer = Economy.layers[ProcessedMaterial]
        raw_layer : Layer = Economy.layers[RawMaterial]

        consumer_layer.connect(processed_layer)
        processed_layer.connect(raw_layer)

        self.graph = Graph(consumer_layer)

    @staticmethod
    def show_simulation_graph(consumer_layer):
        """Display the graph in a Tkinter window"""
        import tkinter as tk
        # Create the graph
        graph = Graph(consumer_layer)
        
        # Create a Tkinter window
        window = tk.Tk()
        window.title("Product Layer Graph - Interactive View")
        window.geometry("1200x800")
        
        # Create the interactive display
        display = graph.get_interactive_display(window)
        
        # Add a status bar (optional)
        status_bar = tk.Label(
            window, 
            text="Click on any node to see details. Use toolbar to zoom/pan.",
            bd=1, relief=tk.SUNKEN, anchor=tk.W
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Cleanup on window close
        def on_closing():
            display.cleanup()
            window.destroy()
        
        window.protocol("WM_DELETE_WINDOW", on_closing)
        window.mainloop()

    @staticmethod
    def compositionTest():
        """Basic analysis of consumer material composition. Will eventually be integrated with UI."""
        #TODO low prio, .format is deprecated change to 'f keys'.
        while True:
            consumer_num = int(input("Enter the number of a consumer to explore it's raw material composition: "))
            if consumer_num > len(ConsumerProduct._existing):
                print("Consumer number {} is bigger than possible ({}), using consumer0 instead!".format(consumer_num, len(ConsumerProduct._existing)))
                consumer_num = 0
            consumer : ConsumerProduct = ConsumerProduct._existing[consumer_num]
            raw_comp = consumer.deriveRawMaterialComposition()
            print(raw_comp)
            print("Product composed of {} unique raw materials".format(len(raw_comp.keys())))
            print("Total weight adds up to {}. (Should always be 1 or at least very close)".format(sum(raw_comp.values())))
