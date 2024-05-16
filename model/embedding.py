from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from .client import OPENAI_API_KEY, openai_client
from .model_name import ModelName


def get_chroma_embedding_function(model: ModelName) -> OpenAIEmbeddingFunction:
    return OpenAIEmbeddingFunction(model_name=model, api_key=OPENAI_API_KEY)
