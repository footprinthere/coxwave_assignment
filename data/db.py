import logging
from tqdm import tqdm

import chromadb

from .source import BaseSourceProcessor


db_client = chromadb.PersistentClient()


def prepare_db(
    collection_name: str,
    processor: BaseSourceProcessor,
    embedding_function: chromadb.EmbeddingFunction,
    chunk_size: int = 128,
) -> chromadb.Collection:

    # Check if the collection already exists
    if collection_name in [c.name for c in db_client.list_collections()]:
        logging.info("Specified collection already exists.")
        return db_client.get_collection(
            name=collection_name,
            embedding_function=embedding_function,
        )

    # Create a new collection
    collection = db_client.create_collection(
        name=collection_name,
        embedding_function=embedding_function,
    )

    data = processor.process_data()
    metadata = processor.parse_for_metadata()

    for i in tqdm(range(0, len(data), chunk_size), desc="Adding data to DB"):
        chunk_slice = slice(i, i + chunk_size)
        chunk_ids = [str(idx) for idx in range(*chunk_slice.indices(len(data)))]
        chunk_documents = data[chunk_slice]
        chunk_metadata = metadata[chunk_slice]
        collection.add(
            ids=chunk_ids,
            documents=chunk_documents,
            metadatas=chunk_metadata,  # type: ignore
        )

    return collection
