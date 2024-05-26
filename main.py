from market.economy import Economy
from market.input.sim_args import *

if __name__ == "__main__":

    #all arg dicts to be filled by user input
    null_args = {}
    sim_args = SimArgs(null_args)
    node_args = {
        "product_args" : ProductArgs(null_args),
        "composite_args" : CompositeArgs(null_args),
        "global_args" : GlobalsArgs(null_args),
        "raw_args" : RawArgs(null_args),
        "processed_args" : ProcessedArgs(null_args),
        "consumer_args" : ConsumerArgs(null_args)
    }
    app = Economy(sim_args, node_args)