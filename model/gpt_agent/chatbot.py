from typing import Optional
from collections import deque

from chromadb import Collection

from log import log
from ..exceptions import EmptyMessageError, ParsingError
from ..model_name import ModelName
from .prompts import CHATBOT_ANSWER
from .base import BaseGPTAgent
from .rephrase import QuestionRephraseAgent


class ChatbotAgent(BaseGPTAgent):

    prompt = CHATBOT_ANSWER

    def __init__(self, model: ModelName, db_collection: Collection, max_history: int):
        super().__init__(model=model)
        self.db_collections = db_collection
        self.max_history = max_history

        self._question_history: deque[str] = deque()
        self._last_answer: Optional[str] = None
        self._rephrase_agent = QuestionRephraseAgent(model=model)

    def answer(
        self,
        question: Optional[str] = None,
        n_retrievals: int = 1,
        verbose: bool = False,
    ) -> str:
        if question is not None:
            self.add_history(question)
        rephrased_question = self._rephrase_history(verbose=verbose)
        if verbose:
            log(f"--- Rephrased Question ---\n{rephrased_question}")

        retrieved = self.retrieve_info(
            question=rephrased_question, n_results=n_retrievals
        )
        message = ChatbotAgent.prompt.format(
            question=rephrased_question, retrieved=retrieved
        )
        if verbose:
            log(f"--- Retrieved Information ---\n{retrieved}")
            log(f"--- Prompt ---\n{message}")

        self._clear_messages()
        self._add_message(role="user", content=message)
        answer = self._call_api(temperature=0.1)
        if verbose:
            log(f"--- Model Answer ---\n{answer}")

        self._last_answer = answer
        return ChatbotAgent._process_answer(answer)

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
        self._last_answer = None

    def _rephrase_history(
        self,
        max_retry: int = 3,
        verbose: bool = False,
    ) -> str:
        if len(self._question_history) == 0:
            raise EmptyMessageError("Question history is empty")
        if len(self._question_history) == 1:
            return self._question_history[-1]
        if self._last_answer is None:
            raise ValueError("Last answer is not set")

        for _ in range(max_retry):
            try:
                rephrased = self._rephrase_agent.answer(
                    question_history=list(self._question_history)[:-1],
                    last_answer=self._last_answer,
                    new_question=self._question_history[-1],
                    verbose=verbose,
                )
            except ParsingError as e:
                continue
            else:
                break
        else:
            raise ParsingError(f"Failed to rephrase question after {max_retry} trials")

        if rephrased is not None:
            return rephrased
        else:
            return self._question_history[-1]  # use the last question

    @staticmethod
    def _process_answer(answer: str) -> str:
        answer = answer.strip()

        # Truncate after the last period
        p_idx = answer.rfind(".")
        if p_idx > 0:
            answer = answer[: p_idx + 1]

        return answer
