
from typing import TypeAlias
from market.products.globals import GlobalMaterial
from market.products.raw_materials import RawMaterial
from market.products.processed import ProcessedMaterial
from market.products.consumer_goods import ConsumerProduct

AnyProduct: TypeAlias = GlobalMaterial | RawMaterial | ProcessedMaterial | ConsumerProduct
ConnectedProduct: TypeAlias = RawMaterial | ProcessedMaterial | ConsumerProduct
AnyComposite: TypeAlias = ProcessedMaterial | ConsumerProduct

#For better type hints everywhere :)