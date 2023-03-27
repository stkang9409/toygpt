import openai
import os
import dotenv
import json
import subprocess

dotenv.load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")


def create_example(input, output):
    return {
        "prompt": input,
        "completion": output,
    }


def create_conversation(examples):
    """파인 튜닝 전 데이터 입력 시 정상 작동 여부 확인용"""
    conversation = []
    for example in examples:
        conversation.append({
            "role": "user",
            "content": example["prompt"],
        })
        conversation.append({
            "role": "assistant",
            "content": example["completion"],
        })
    return conversation


def save_examples(examples):
    with open("examples.json", "w") as f:
        for example in examples:
            f.write(json.dumps(example) + "\n")


def run_with_fine_model(model, prompt):
    return openai.Completion.create(model=model, prompt=prompt, max_tokens=2000)


# openai tools fine_tunes.prepare_data -f examples.json
# openai api fine_tunes.create -t "examples_prepared.jsonl" -m davinci
# openai api fine_tunes.follow -i ft-uEWTnG38aFWntDpuzCNC0sUp
# openai api fine_tunes.list
# openai api fine_tunes.delete -i ft-uEWTnG38aFWntDpuzCNC0sUp
# openai api fine_tunes.get -i ft-uEWTnG38aFWntDpuzCNC0sUp