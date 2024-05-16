import os
import argparse

from data import prepare_db, TitleOnlySourceProcessor
from model import (
    get_chroma_embedding_function,
    ChatbotAgent,
    ModelName,
    EmptyMessageError,
)
from tools import log, ChatbotCycleResult


class Main:

    agent: ChatbotAgent
    args: argparse.Namespace

    @classmethod
    def main(cls):
        cls.args = cls._parse_args()

        cls.agent = cls._prepare_agent()

        # Ready to start
        log("Preparation process done. Press ENTER to launch the chatbot.")
        input()
        if os.name == "nt":
            os.system("cls")  # Windows
        else:
            os.system("clear")

        # Print starting message
        print(cls.START_MESSAGE)

        # Run chatbot
        retry_count = 0
        while True:
            user_input = input("\033[36m>>>\033[0m ").strip()
            result = cls._cycle(user_input, retry_count)
            if cls.args.debug:
                log(f"Cycle result: {result}")

            if result == ChatbotCycleResult.OK:
                retry_count = 0
            elif result == ChatbotCycleResult.RETRY:
                retry_count += 1
            elif result == ChatbotCycleResult.EXIT:
                break

    @classmethod
    def _parse_args(cls) -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument("--source_path", type=str, required=True)
        parser.add_argument("--collection_name", type=str, required=True)
        parser.add_argument("--max_retry", type=int, default=3)
        parser.add_argument("--max_history", type=int, default=5)
        parser.add_argument("--debug", action="store_true")

        return parser.parse_args()

    @classmethod
    def _prepare_agent(cls) -> ChatbotAgent:
        log("Preparing information database ...")
        db_collection = prepare_db(
            collection_name=cls.args.collection_name,
            processor=TitleOnlySourceProcessor(data_path=cls.args.source_path),
            embedding_function=get_chroma_embedding_function(ModelName.EMBEDDING_ADA),
        )

        # Prepare GPT agent
        log("Preparing GPT agent ...")
        agent = ChatbotAgent(
            model=ModelName.GPT_3_5_1106,
            db_collection=db_collection,
            max_history=cls.args.max_history,
        )
        return agent

    @classmethod
    def _cycle(cls, user_input: str, retry_count: int) -> ChatbotCycleResult:
        if user_input == "":
            return ChatbotCycleResult.INVALID
        if user_input == "!종료":
            return ChatbotCycleResult.EXIT
        if user_input.startswith("!") and user_input != "!재시도":
            print("잘못된 명령어입니다.")
            return ChatbotCycleResult.INVALID

        if user_input == "!재시도":
            if retry_count >= cls.args.max_retry:
                print("최대 횟수를 초과해 더 이상 재시도할 수 없습니다.")
                return ChatbotCycleResult.INVALID
            try:
                answer = cls.agent.answer(
                    n_retrievals=2 * retry_count + 3,
                    verbose=cls.args.debug,
                )
            except EmptyMessageError:
                print("입력된 질문이 없어 재시도할 수 없습니다.")
                return ChatbotCycleResult.INVALID
            else:
                result = ChatbotCycleResult.RETRY
        else:
            answer = cls.agent.answer(
                question=user_input,
                n_retrievals=2 * retry_count + 1,  # 1, 3, 5, ...
                verbose=cls.args.debug,
            )
            result = ChatbotCycleResult.OK

        if answer.upper().startswith("X"):
            print(
                "죄송합니다. 스마트스토어와 관련이 없는 질문에는 답변해드릴 수 없어요."
            )
            cls.agent.clear_history()
            return ChatbotCycleResult.UNRELATED
        else:
            print(f"\033[36m-->\033[0m {answer}\n")
            return result

    START_MESSAGE = (
        "스마트스토어 챗봇을 시작합니다. 스마트스토어에 관한 질문을 입력하시면 FAQ 기록을 바탕으로 답변해드립니다.\n"
        "만약 만족스러운 답변을 얻지 못했다면 \033[91m'!재시도'\033[0m를 입력해 좀 더 나은 답변을 받아볼 수 있습니다.\n"
        "챗봇을 종료하려면 \033[91m'!종료'\033[0m를 입력해주세요.\n\n"
        "[사용 예시]\n>>> 미성년자도 판매 회원 등록이 가능한가요?\n\n"
        "---------------------------------------------------\n"
    )


if __name__ == "__main__":
    Main.main()
