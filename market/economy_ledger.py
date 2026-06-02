

class EconomyLedger:
    """
    Stores per product indexed data histories.
    Might be used in future I guess...
    """

    def __init__(self):
        self.ledger = {}
        self.ledger : dict[str,dict[str,dict]]
        #shape ledger = {layer_name : {product_id : {data_name : data_val}}}
