import json
import random
import requests

import my_ai
import chat_ko as ko

customer_schema = """
flat json format
name: "opponent's name it should not be changed. it is must required",
character: "What kind of personality does opponent have? it is must required",
line: "reaction line of opponent when I say something. it is must required",
angry_score: "number(0~100) on how angry is this person right now? it is must required"
"""

opponent_schema = """
flat json format
name: "opponent's name it should not be changed. it is must required",
character: "What kind of personality does opponent have? it is must required",
angry_score: "number(0~100) on how angry is this person right now? it is must required"
"""

def generate_situation_prompt(topic=None, count=5):
    if topic is None:
        topic = "workplace"

    return f"""Give me {count} situations like the example below, I want it to be an array of the same data structure as the example.

Instead, the situation should be related to {topic}.

{{"situation": "I'm having dinner with an old friend and he suddenly asks me to borrow money. I don't want to lend him money, but I don't want to hurt his feelings. I want to get out of this situation without hurting his feelings.",
     "myObjective": "Politely decline the request while preserving the friendship"}}"""


def first_prompt(situation):
    return f""" please give me required data in json format.
{situation['situation']} 

what i want is {situation['myObjective']}


imagine an opponent like real person i should deal with and give me a response.

the data should be json like below.
{opponent_schema}

This person you created and I keep talking.

the data must be in the form of a single json object.
"""


def following_prompt(opponent, answer):
    return f"""I told like this 
    {answer}

    to {opponent['name']}

please let me know how {opponent['name']} will react.

{opponent['name']}'s reaction should be in line field. it should be updated after each conversation and there should not be same reaction twice.

response schema should be json like below
{customer_schema}

please give me only json without any other characters.
"""

def feedback_request():
    feedback_schema = """

totol_score: A score from 0 to 100 on the overall conversation.
humor_score: A number from 0 to 100 about how funny the answer was.
appropriateness_score: A number from 0 to 100 on how appropriate the words you chose were
empathy_score: "A number from 0 to 100 on how empathetic I was in this conversation.",
reason_score: "A number from 0 to 100 on how well I explained my reasoning.",
angry_score: "A number from 0 to 100 on how angry I was in this conversation.",
sexy_score: "A number from 0 to 100 on how sexy I was in this conversation.",
rationale: The rationale for your score
feedback: Text from the perspective of how well this was said to accomplish the goal and how appropriate it was from the perspective of nonviolent dialog.
suggestions: Text about how you can have a better conversation.
politeness_score: "A number from 0 to 100 on how polite I was in this conversation.",

data must be only one json object item and no other than above
 
 """

    return f"""Please give me feedback.

I want to know what you think about this conversation.
if you have any suggestion, please let me know.

I want to be evaluated in terms of how well I accomplished my goals.
And from a nonviolent dialog perspective, I'd also like to include in the evaluation criteria whether I've spoken in a way that the other person is receptive to what I'm saying.

The data should be json like below.
{feedback_schema}
"""

def get_initial_opponent(precondition, retry=0, lang='ko'):
    if retry > 3:
        raise Exception("failed to get valid opponent")

    if lang == 'ko':
        prompt = ko.first_prompt(precondition)
    else:   
        prompt = first_prompt(precondition)
        
    opponent = my_ai.require_json(prompt)
    try:
        if not opponent["name"]:
            raise Exception("name is required")
        return prompt, opponent
    except Exception as e:
        print(f"response is not valid json: {opponent}")
        return get_initial_opponent(precondition, retry + 1)


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
        
    situations = my_ai.require_json(prompt)
    random_index = random.randint(0, len(situations) - 1)
    return prompt, situations[random_index]


def main():
    topic = "workplace"
    prompt, situation = get_situation(topic)
    print(f"situation: {situation['situation']}")
    print(f"objective: {situation['myObjective']}")

    prompt, opponent = get_initial_opponent(situation)
    history = [{"role": "user", "content": first_prompt(situation)}]
    history.append({"role": "assistant", "content": json.dumps(opponent)})
    print(f'{opponent["name"]}의 정보입니다: {opponent}')

    answer = input("첫 대화를 입력해주세요: ")

    count = 0
    while True:
        input_prompt, opponent = response_to_customer(opponent, answer, history)

        history.append({"role": "user", "content": f"{answer}"})
        history.append({"role": "assistant", "content": json.dumps(opponent)})

        print(f'{opponent.get("name", "철수")}({opponent["angry_score"]}): {opponent["line"]}')

        count += 1
        # every 5 turns, evaluate conversation
        if count % 5 == 0:
            feedback = evaluate_conversation(history)
            print(f"feedback: {str(feedback)}")
            if feedback["total_score"] > 80:
                break

        answer = input("대답을 입력해주세요: ")
        

if __name__ == "__main__":
    main()
