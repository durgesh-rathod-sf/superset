# The `OpenAIGPT35TurboText2SqlStrategy` class is a text-to-SQL strategy that uses the OpenAI GPT-3.5
# Turbo model to convert natural language queries into SQL queries.
import os
from haystack.nodes import PromptNode
from superset.sqllab.utils import json_file_to_dict

current_dir = os.path.dirname(__file__)


CONFIG = json_file_to_dict(os.path.join(current_dir, "prompt-openai-config.json"))


class OpenAIText2SqlStrategy:
    _model = CONFIG["model"]

    def __init__(self):
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        self._prompt_node = PromptNode(
            model_name_or_path=self._model,
            api_key=openai_api_key,
            model_kwargs={"generation_kwargs": {"do_sample": True, "temperature": 0.1}},
        )

    def execute(
        self, prompt_text: str, db_dump: str, db_type: str, db_version: str
    ) -> str:
        if prompt_text is None:
            raise ValueError(CONFIG["messages"]["empty_error_message"])
        system_message_content = CONFIG["messages"]["user_message"].format(
            dbdump=str(db_dump), db_type=db_type, db_version=db_version
        )
        _system_messages = [
            {
                "role": "system",
                "content": system_message_content,
            }
        ]
        converstion = _system_messages[:]
        converstion.append({"role": "user", "content": prompt_text})
        answer = self._prompt_node(converstion)

        converstion = []  # required??
        return answer[0].replace("\n", " ")
