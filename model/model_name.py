from enum import Enum


class ModelName(str, Enum):
    EMBEDDING_SMALL = "text-embedding-3-small"
    EMBEDDING_ADA = "text-embedding-ada-002"

    GPT_3_5_1106 = "gpt-3.5-turbo-1106"
