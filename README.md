# SmartStore FAQ Chatbot

## Preparations
* Install pip packages listed in `requirements.txt`.
* Prepare the FAQ dataset file (.pkl).
* Create `.env` file in the main directory and store your OpenAI API key in it.

    ```
    OPENAI_API_KEY=[your api key]
    ```

## Usage
* Run `main.py` to start the chatbot. For example:

    ```shell
    PYTHONPATH=`pwd` python main.py --source_path="dataset/faq_data.pkl"
    ```

**Program Arguments**
* `source_path: str`: Path to the FAQ dataset file (.pkl).
* `collection_name: str`: Name of the ChromaDB collection to use. The database will be stored in `chromadb/` directory. Default is "faq".
* `max_retry: int`: Maximum number of times a user can retry the same question. Default is 3.
* `max_history: int`: Maximum number of chat history to keep. Default is 5.
* `debug: store_true`: Enable debug mode.
