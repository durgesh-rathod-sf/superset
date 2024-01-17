import os
import boto3
import json

from superset.sqllab.utils import json_file_to_dict


current_dir = os.path.dirname(__file__)


CONFIG = json_file_to_dict(os.path.join(current_dir, "prompt-claude-config.json"))


class BedRockClaudeText2SqlStrategy:
    _model = CONFIG["model"]

    def __init__(self):
        aws_access_key = os.environ.get("AWS_ACCESS_KEY")
        aws_secret_key = os.environ.get("AWS_SECRET_KEY")
        aws_region = os.environ.get("AWS_REGION")
        self.client = boto3.client(
            service_name="bedrock-runtime",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region,
        )

    def execute(
        self,
        prompt_text: str,
        db_dump: str,
        db_type: str = "postgres",
        db_version: str = "8",
    ) -> str:
        if prompt_text is None:
            raise ValueError(CONFIG["messages"]["empty_error_message"])
        output_tag_name = "sql-query"
        system_message_content = CONFIG["messages"]["user_message"].format(
            dbdump=str(db_dump),
            db_type=db_type,
            db_version=db_version,
            output_tag_name=output_tag_name,
        )
        prompt_text = f"{system_message_content} <prompt>{prompt_text}</prompt>"

        body = (
            '{"prompt":"Human: \\n\\nHuman: '
            + prompt_text
            + '\\n\\nAssistant:","max_tokens_to_sample":3000,"temperature":0.1,"top_k":250,"top_p":0.999,"stop_sequences":["\\n\\nHuman:"],"anthropic_version":"bedrock-2023-05-31"}'
        )

        answer = self.client.invoke_model(
            modelId=CONFIG["model"],
            contentType="application/json",
            accept="*/*",
            body=body,
        )
        answer = answer["body"].read().decode("utf-8")
        answer = json.loads(answer)
        answer = answer["completion"].replace("\n", " ")

        return self.extract_content_between_tags(text=answer, start_tag=output_tag_name)

    def extract_content_between_tags(self, text, start_tag):
        """
        Extracts content between the specified start and end tags.

        Parameters:
            text (str): The text containing the content between tags.
            start_tag (str): The start tag.

        Returns:
            str: The content between the specified start and end tags.
        """

        end_tag = f"</{start_tag}>"
        start_tag = f"<{start_tag}>"

        start_index = text.find(start_tag)
        end_index = text.find(end_tag)

        if start_index != -1 and end_index != -1:
            return text[start_index + len(start_tag) : end_index].strip()
        else:
            return text
