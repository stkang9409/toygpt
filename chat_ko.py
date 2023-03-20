import json
import random
import requests

import my_ai

customer_schema = """
플랫 JSON 형식
name: "상대방의 이름은 변경해서는 안됩니다. 반드시 필요합니다",
character: "상대방은 어떤 성격을 가지고 있습니까? 반드시 필요합니다",
line: "내가 무언가를 말할 때 상대의 반응 라인. 그것은 반드시 필요합니다",
angry_score: "이 사람이 지금 얼마나 화가 났는지에 대한 숫자(0~100)? 반드시 필요합니다."
"""

opponent_schema = """
플랫 JSON 형식
name: "상대방의 이름은 변경해서는 안됩니다. 반드시 필요합니다",
character: "상대방은 어떤 성격을 가지고 있습니까? 반드시 필요합니다",
angry_score: "이 사람이 지금 얼마나 화가 났는지에 대한 숫자(0~100)? 반드시 필요합니다."
"""

def generate_situation_prompt(topic=None, count=5):
    if topic is None:
        topic = "workplace"

    return f"""아래 예제와 같은 {count} 상황을 제공하면 예제와 동일한 데이터 구조의 배열이 되기를 원합니다.

대신 상황은 {topic}과 관련되어 있어야 합니다.

{{"situation": "오랜 친구와 저녁을 먹고 있는데 친구가 갑자기 돈을 빌려달라고 합니다. 돈을 빌려주고 싶지는 않지만 친구의 기분을 상하게 하고 싶지 않습니다. 그의 감정을 상하게 하지 않고 이 상황에서 벗어나고 싶습니다.",
     "myObjective": "우정을 유지하면서 정중하게 요청을 거절한다"}}"""


def first_prompt(situation):
    return f""" 필요한 데이터를 json 형식으로 제공해 주세요.
{situation['situation']} 

내가 원하는 것은 {situation['myObjective']}입니다.


내가 상대해야 할 실제 사람과 같은 상대를 상상하고 응답을 제공해주세요.

데이터는 아래와 같은 JSON이어야 합니다.
{opponent_schema}

내가 만든 이 사람과 내가 계속 대화합니다. 그래서 이 사람의 이름은 반드시 필요합니다.
"""


def following_prompt(opponent, answer):
    return f"""{opponent['name']}에게 다음과 같이 말했습니다. 
    {answer}

{opponent['name']}이 어떻게 반응하는지 알려주세요.

{opponent['name']}의 반응은 line 필드에 입력해야 하며, 대화가 끝날 때마다 업데이트되어야 하고 같은 반응이 두 번 나오지 않아야 합니다.

응답 스키마는 아래와 같은 JSON이어야 합니다.
{customer_schema}

다른 문자는 제외하고 json만 입력해주세요.
"""


def feedback_request():
    feedback_schema = """

totol_score: 전체 대화에 대한 0~100점 사이의 점수입니다.
humor_score: 답변이 얼마나 웃겼는지에 대한 0~100 사이의 수치입니다.
appropriateness_score: 선택한 단어가 얼마나 적절했는지에 대한 0~100 사이의 점수입니다.
empathy_score: "이 대화에서 내가 얼마나 공감했는지에 대한 0~100 사이의 숫자",
reason_score: "내 추론을 얼마나 잘 설명했는지에 대한 0~100 사이의 숫자",
angry_score: "이 대화에서 내가 얼마나 화가 났는지를 0에서 100까지의 숫자로 표시합니다.",
sexy_score: "이 대화에서 내가 얼마나 섹시했는지를 0에서 100까지의 숫자로 표시합니다.", "이 대화에서 내가 얼마나 섹시했는지를 0에서 100까지의 숫자로 표시합니다.",
rationale: 점수의 근거입니다.
feedback: 목표를 달성하기 위해 얼마나 잘 말했는지, 비폭력 대화의 관점에서 얼마나 적절했는지에 대한 관점에서의 텍스트입니다.
suggestions: 더 나은 대화를 할 수 있는 방법에 대한 텍스트입니다.
politeness_score: "이 대화에서 내가 얼마나 공손했는지에 대한 0에서 100까지의 숫자.",
"""

    return f"""피드백을 보내주세요.

이 대화에 대해 어떻게 생각하는지 알고 싶습니다.
제안 사항이 있으면 알려주세요.

저는 목표를 얼마나 잘 달성했는지에 대한 평가를 받고 싶습니다.
그리고 비폭력 대화의 관점에서 상대방이 제 말을 잘 받아들일 수 있는 방식으로 대화했는지 여부도 평가 기준에 포함시키고 싶습니다.

데이터는 아래와 같은 json이어야 합니다.
{feedback_schema}
"""