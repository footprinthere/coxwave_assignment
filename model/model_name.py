from enum import Enum


class ModelName(str, Enum):
    EMBEDDING_SMALL = "text-embedding-3-small"
    EMBEDDING_ADA = "text-embedding-ada-002"
