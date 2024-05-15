from typing import Literal

from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam

from ..client import openai_client
from ..exceptions import EmptyMessageError, ModelError
from ..model_name import ModelName


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
