# rag/workflow/intent_types.py

from enum import Enum


class Intent(Enum):
    SMALL_TALK = "small_talk"
    PRODUCT_SEARCH = "product_search"
    STORE_INFO = "store_info"
    MATERIAL_KNOWLEDGE = "material_knowledge"


