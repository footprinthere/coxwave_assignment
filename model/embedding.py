from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from .client import OPENAI_API_KEY, openai_client
from .model_name import ModelName


def embed(inputs: list[str], model: ModelName) -> list[list[float]]:
    response = openai_client.embeddings.create(input=inputs, model=model)
    return [e.embedding for e in response.data]


def get_chroma_embedding_function(model: ModelName) -> OpenAIEmbeddingFunction:
    return OpenAIEmbeddingFunction(model_name=model, api_key=OPENAI_API_KEY)
