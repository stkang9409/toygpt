import openai
import os
import json
import yaml
import re

from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")
MAX_RETRY = 3


def require_json(prompt, messages_before=None, retry=0):
    """asfd"""
    if retry > MAX_RETRY:
        raise Exception("failed to get valid json")

    json_required_prompt = f"{prompt}\nIMPORTANT: Please provide the answer in JSON format only, without any additional text, whitespace or characters."
    response = generate_response(json_required_prompt, messages_before)
    response = response.strip()
    if response.startswith("```") and response.endswith("```"):
        response = response[3:-3].strip()

    try:
        obj = json.loads(response)
        return obj
    except Exception:
        print(f"response is not valid json: {response}")
        if retry == 3:
            print(f"response is not valid json: {response}")
        return require_json(prompt, messages_before, retry + 1)


def schema_dumps(obj, indent=0):
    rows = [""]

    if isinstance(obj, list):
        return f"[{{{schema_dumps(obj[0], indent=indent+1)}\n{' '*indent}}}, ...]"

    if isinstance(obj, str):
        return obj

    if isinstance(obj, int):
        return str(obj)

    for k, v in obj.items():
        if isinstance(v, dict):
            v = schema_dumps(v, indent=indent + 1)
        if isinstance(v, list):
            v = f"[{{{schema_dumps(v[0], indent=indent+1)}\n{' '*indent}}}, ...]"

        rows.append(f"{k}: {v}")
    return f"\n{' '*indent}".join(rows)


def catch_code_in_response(response):
    pattern = r"```(.*?)```"
    matches = re.search(pattern, response)

    if matches:
        response = matches.group(1)

    response = response.strip()
    if response.startswith("```") and response.endswith("```"):
        response = response[3:-3].strip()

    if response.startswith("json"):
        response = response[4:]

    return response


def require_json_v2(prompt, schema, messages_before=None):
    # dict to string like yaml
    json_required_prompt = f"""{prompt}

data format should follow the schema below:
{schema}

IMPORTANT: Please provide the answer in JSON format only, without any additional text, whitespace or characters."""
    response = generate_response(json_required_prompt, messages_before)
    response = catch_code_in_response(response)
    obj = {}
    try:
        obj = json.loads(response)
        if isinstance(obj, list):
            return json_required_prompt, obj[0]

        return json_required_prompt, obj
    except Exception as e:
        return require_json_v2(prompt, schema)


def require_array_of_json(prompt, schema, messages_before=None):
    # dict to string like yaml
    json_required_prompt = f"""{prompt}

response should be array of data of which format follow the schema below:
{schema}

IMPORTANT: Please provide the answer in array of JSON format only, without any additional text, whitespace or characters."""
    response = generate_response(json_required_prompt, messages_before)
    response = catch_code_in_response(response)
    obj = {}
    try:
        obj = json.loads(response)
        if isinstance(obj, list):
            return json_required_prompt, obj

        raise Exception("response is not array of json")
    except Exception as e:
        return require_json_v2(prompt, schema)


def generate_response(prompt, messages_before=None):
    if messages_before is None:
        messages_before = []

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "All the responses should be format of json.",
            },
            *messages_before,
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0]["message"]["content"]


class ContextStore:
    def __init__(self, context=None):
        if context is None:
            context = []
        self.context = context

    def get_context(self):
        return self.context

    def add_context(self, prompt, response):
        dialogue = [
            {"role": "user", "content": f"{prompt}"},
            {"role": "assistant", "content": f"{response}"},
        ]
        # return new contextStore
        return ContextStore(context=self.context + dialogue)
