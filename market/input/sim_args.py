from abc import ABC, abstractmethod

#not really necessary 
class ArgDict(ABC):

    DEFAULTS = {}

    def __init__(self, args : dict):
        self.conts = self.DEFAULTS.copy() | args


class SimArgs(ArgDict):
    """Arguments to alter simulation environment"""

    DEFAULTS = {
        "use_globals" : True
    }

    def __init__(self, args: dict):
        super().__init__(args)


class ProductArgs(ArgDict):
    """Arguments applied to all Products that are created"""

    DEFAULTS = {

    }

    def __init__(self, args: dict):
        super().__init__(args)


class GlobalsArgs(ArgDict):
    """Arguments applied only to 'GlobalMaterials'."""

    DEFAULTS = {
        "layer_size" : 2
    }

    def __init__(self, args: dict):
        super().__init__(args)


class RawArgs(ArgDict):
    """Arguments applied only to 'RawMaterials'."""

    DEFAULTS = {
        "layer_size" : 20,
        "units_avail" : 100
    }

    def __init__(self, args: dict):
        super().__init__(args)


class CompositeArgs(ArgDict):
    """Arguments applied to all products that inherit from 'Composite' as a product."""

    DEFAULTS = {
        "num_preferred_components" : 4
    }

    def __init__(self, args: dict):
        super().__init__(args)


class ProcessedArgs(ArgDict):
    """Arguments applied only to 'ProcessedMaterials'."""

    DEFAULTS = {
        "layer_size" : 20
    }

    def __init__(self, args: dict):
        super().__init__(args)


class ConsumerArgs(ArgDict):
    """Arguments applied only to 'ConsumerMaterials'."""

    DEFAULTS = {
        "layer_size" : 20
    }

    def __init__(self, args: dict):
        super().__init__(args)
