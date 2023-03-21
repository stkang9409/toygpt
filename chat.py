import json
import random
import requests

import my_ai
import repo
import chat_ko as ko

customer_schema = """
name: "opponent's name",
line: "reaction line of opponent",
angry_score: "number(0~100) on how angry is this person"
"""

opponent_schema = """
name: "opponent's name it should not be changed. it is must required",
character: "What kind of personality does opponent have? it is must required",
angry_score: "number(0~100) on how angry is this person right now?"
"""

def generate_situation_prompt(topic=None, count=5):
    if topic is None:
        topic = "workplace"

    return f"""I want to create my own assignment to practice nonviolent communication. I need a good situation to practice nonviolent communication. I want to give you {count} situations like the example below, and I want them to be arrays of data structures like the example.

Instead, the situations should be {topic}.

The situations should be based on asking for a favor, empathizing, expressing feelings, resolving conflict, expressing gratitude, and offering help.

{{"situation": "I'm having dinner with an old friend and he suddenly asks to borrow money. I don't want to lend him money, but I don't want to hurt his feelings. I want to get out of this situation without hurting his feelings",
     "myObjective": "To politely decline the request while maintaining the friendship."}}"""


def first_prompt(situation):
    return f"""

in this situation: {situation['situation']}

what i want is {situation['myObjective']}

imagine an opponent like real person i should deal with and give me a response.

I will keep talking to him.
"""


def following_prompt(opponent, answer):
    return f"""I told like this 
    {answer}

    to {opponent['name']}

please let me know how {opponent['name']} will react.
reaction should related to {opponent['name']}'s character

response schema should be json like below
{customer_schema}

please give me only json without any other characters.
"""

def feedback_request():
    feedback_schema = """

total_score: A score on the overall conversation.
humor_score: A score on how funny the answer was.
appropriateness_score: how appropriate the words you chose were
empathy_score: "how empathetic I was in this conversation.",
reason_score: "how well I explained my reasoning.",
angry_score: "how angry I was in this conversation.",
sexy_score: "how sexy I was in this conversation.",
politeness_score: "how polite I was in this conversation."
feedback: feedback on conversation.
suggestions: Text about how you can have a better conversation.
 """

    return f"""Please give me feedback.

I want to be evaluated in terms of how well I accomplished my goals.
And from a nonviolent dialog perspective

The data should be json like below.
{feedback_schema}

let me explain additional information.

All scores are from 0 to 100. 0 means worst and 100 means best.
and it's very hard to get score over 50.

feedback and suggestions should be very detailed.
"""


def get_initial_opponent(precondition, lang='ko'):
    if lang == 'ko':
        prompt = ko.first_prompt(precondition)
    else:   
        prompt = first_prompt(precondition)
        
    opponent = repo.get_opponent(lang)
    return prompt, opponent


def response_to_customer(opponent, answer, history, retry=0, lang='ko'):
    if retry > 3:
        raise Exception("failed to get valid opponent")

    if lang == 'ko':
        input_prompt = ko.following_prompt(opponent, answer)
    else:
        input_prompt = following_prompt(opponent, answer)

    return input_prompt, my_ai.require_json(following_prompt(opponent, answer), history)


def evaluate_conversation(history, lang='ko'):
    if lang == 'ko':
        return my_ai.require_json(ko.feedback_request(), history)

    return my_ai.require_json(feedback_request(), history)


def get_situation(topic=None, lang='ko'):
    if lang == 'ko':
        prompt = ko.generate_situation_prompt(topic)
    else:
        prompt = generate_situation_prompt(topic)

    if topic in repo.defined_topics(lang):
        situations = repo.get_situations(topic, lang)
    else:
        situations = my_ai.require_json(prompt)

    random_index = random.randint(0, len(situations) - 1)
    return prompt, situations[random_index]
