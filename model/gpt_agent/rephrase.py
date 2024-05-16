from typing import Any, Optional
import json

from tools import log
from ..exceptions import ParsingError
from ..prompts import QUESTION_REPHRASE
from .base import BaseGPTAgent


class QuestionRephraseAgent(BaseGPTAgent):

    prompt = QUESTION_REPHRASE

    def answer(
        self,
        question_history: list[str],
        last_answer: str,
        new_question: str,
        verbose: bool = False,
    ) -> Optional[str]:
        if len(question_history) == 0:
            raise ValueError("Question history is empty")

        message = QuestionRephraseAgent.prompt.format(
            prev_questions=QuestionRephraseAgent._format_history(question_history),
            last_answer=last_answer,
            question=new_question,
        )
        if verbose:
            log(f"--- Prompt ---\n{message}")

        self._clear_messages()
        self._add_message(role="user", content=message)
        answer = self._call_api(temperature=0.1, json_mode=True)
        if verbose:
            log(f"--- Model Answer ---\n{answer}")

        parsed_answer = QuestionRephraseAgent._parse_json_output(
            output=answer,
            required_fields=["reason", "related", "rephrased"],
            verbose=verbose,
        )
        if parsed_answer["related"]:
            return parsed_answer["rephrased"]
        else:
            return None

    @staticmethod
    def _format_history(question_history: list[str]) -> str:
        # Bullet list format
        return "\n".join("* " + q for q in question_history)

    @staticmethod
    def _parse_json_output(
        output: str,
        required_fields: list[str],
        verbose: bool = False,
    ) -> dict[str, Any]:
        try:
            parsed = json.loads(output)
        except json.JSONDecodeError as e:
            if verbose:
                log(f"JSON decoding error: {e}")
            raise ParsingError("Error while parsing JSON output")

        for field in required_fields:
            if field not in parsed:
                if verbose:
                    log(f"Required field '{field}' not found in JSON output")
                raise ParsingError(f"Required field '{field}' not found in JSON output")

        return parsed
