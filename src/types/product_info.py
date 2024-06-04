from typing import TypedDict, Optional


class ProductInfo(TypedDict):
    brand_name: str
    model_name: str
    part_number: Optional[str]
