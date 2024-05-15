from typing import Literal, Optional
from collections import deque

from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from chromadb import Collection

from tools import log
from .client import openai_client
from .model_name import ModelName
from .prompts import CHATBOT_ANSWER
from .exceptions import EmptyMessageError, ModelError


class BaseGPTAgent:

    def __init__(self, model: ModelName):
        self.model = model
        self._messages: list[ChatCompletionMessageParam] = []

    def _add_message(self, role: Literal["system", "user"], content: str) -> None:
        self._messages.append({"role": role, "content": content})  # type: ignore

    def _clear_messages(self) -> None:
        self._messages.clear()

    def _call_api(self, temperature: float) -> str:
        if len(self._messages) == 0:
            raise EmptyMessageError("Messages should be added before calling API")

        response = openai_client.chat.completions.create(
            model=self.model,
            messages=self._messages,
            temperature=temperature,
        )
        answer = response.choices[0].message.content
        if answer is None:
            raise ModelError("Model did not output any message")
        return answer


class ChatbotAgent(BaseGPTAgent):

    prompt = CHATBOT_ANSWER

    def __init__(self, model: ModelName, db_collection: Collection, max_history: int):
        super().__init__(model=model)
        self.db_collections = db_collection
        self.max_history = max_history

        self._question_history: deque[str] = deque()

    def answer(
        self,
        question: Optional[str] = None,
        n_retrievals: int = 1,
        verbose: bool = False,
    ) -> str:
        if question is not None:
            self.add_history(question)
        parsed_question = self.parse_history()

        retrieved = self.retrieve_info(question=parsed_question, n_results=n_retrievals)
        message = ChatbotAgent.prompt.format(
            question=parsed_question, retrieved=retrieved
        )
        if verbose:
            log(f"--- Retrieved Information ---\n{retrieved}")
            log(f"--- Prompt ---\n{message}")

        self._clear_messages()
        self._add_message(role="user", content=message)
        return self._call_api(temperature=0.1)

    def retrieve_info(self, question: str, n_results: int = 1) -> str:
        if question.strip() == "":
            raise EmptyMessageError("Query question is empty")

        result = self.db_collections.query(query_texts=[question], n_results=n_results)
        metadatas = result["metadatas"]
        assert metadatas is not None

        contents: list[str] = [m["content"] for m in metadatas[0]]  # type: ignore
        return "\n".join(contents)

    def add_history(self, question: str) -> None:
        self._question_history.append(question)
        if len(self._question_history) > self.max_history:
            self._question_history.popleft()

    def clear_history(self) -> None:
        self._question_history.clear()

    def parse_history(self) -> str:
        if len(self._question_history) == 0:
            raise EmptyMessageError("Question history is empty")
        return "\n".join(self._question_history)
