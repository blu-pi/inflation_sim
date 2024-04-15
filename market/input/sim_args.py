from abc import ABC, abstractmethod

#not really necessary 
class ArgDict(ABC):

    DEFAULTS = {}

    def __init__(self, args : dict):
        self.conts = self.DEFAULTS.copy() | args


class SimArgs(ArgDict):

    DEFAULTS = {

    }

    def __init__(self, args: dict):
        super().__init__(args)


class ProductArgs(ArgDict):

    DEFAULTS = {
        
    }

    def __init__(self, args: dict):
        super().__init__(args)


class GlobalsArgs(ArgDict):

    DEFAULTS = {
        "layer_size" : 2
    }

    def __init__(self, args: dict):
        super().__init__(args)


class RawArgs(ArgDict):

    DEFAULTS = {
        "layer_size" : 20,
        "units_avail" : 100
    }

    def __init__(self, args: dict):
        super().__init__(args)


class CompositeArgs(ArgDict):

    DEFAULTS = {

    }

    def __init__(self, args: dict):
        super().__init__(args)


class ProcessedArgs(ArgDict):

    DEFAULTS = {
        "layer_size" : 20
    }

    def __init__(self, args: dict):
        super().__init__(args)


class ConsumerArgs(ArgDict):

    DEFAULTS = {
        "layer_size" : 20
    }

    def __init__(self, args: dict):
        super().__init__(args)
