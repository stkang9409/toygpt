import openai
import os
import json

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
    # strip whitespace and remove ``` from response
    response = response.strip()
    if response.startswith("```") and response.endswith("```"):
        response = response[3:-3]
    
    try:
        obj = json.loads(response)
        return obj
    except Exception:
        print(f"response is not valid json: {response}")
        if retry == 3:
            print(f"response is not valid json: {response}")
        return require_json(prompt, messages_before, retry + 1)


def generate_response(prompt, messages_before=None):
    if messages_before is None:
        messages_before = []
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "All the responses should have only format of json."},
            *messages_before,
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0]["message"]["content"]