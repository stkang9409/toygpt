import re
from datetime import datetime

from domains.일지 import required_report_num

def get_mentioned_count(messages):
    name_count = {}
    for message in messages:
        if message["name"] == "강민규":
            # 내용 중 @이름 형태의 문자열을 찾아서 이름을 추출, 몇번 나왔는지 세기
            # @김연정, @김연정, @김연정
            # @김연정, @김연정, @김연정

            regex = r"@(\w+)"
            names = re.findall(regex, message["text"])
            for name in names:
                if name not in name_count:
                    name_count[name] = 0
                name_count[name] += 1
    
    # 이름이 많이 나온 순서대로 출력, 이름: 횟수 형태
    # 김연정: 3
    result = []
    for name, count in sorted(name_count.items(), key=lambda x: x[1], reverse=True):
        result.append(f"{name}: {count}")
    return "\n".join(iterable=result)


def get_person_said(messages, person):
    result = []
    for message in messages:
        if message["name"] == person:
            result.append(message)
    return result


def get_invited_people(messages):
    people = set()

    for message in messages:
        if message["text"].endswith(f"님이 들어왔습니다."):
            name = message["text"].split("님이 들어왔습니다.")[0]
            people.add(name)
        
        if message["text"].endswith(f"님이 나갔습니다."):
            name = message["text"].split("님이 나갔습니다.")[0]
            people.remove(name)

    if "오픈채팅봇" in people:
        people.remove("오픈채팅봇")
    
    if "강민규" in people:
        people.remove("강민규")
    
    for message in messages:
        for person in people.copy():
            if message["text"].startswith(f"{person}님을 내보냈습니다."):
                people.remove(person)

    return people


def count_reports_in_dict(messages, start_date=None):
    if start_date is None:
        start_date = datetime(2019, 8, 5)

    count_dict = {}
    for message in messages:
        all_messages = []
        # \d+일차가 여러개 있으면 분리한다. -> 1일차 하이 2일차 노노 -> ["1일차 하이", "2일차 노노"]
        has_multiple_days = re.findall(r"\d+일차", message["text"])
        if has_multiple_days:
            remainder = message["text"]
            for i, day in enumerate(has_multiple_days):
                num, _ = day.split("일차")
                # split by first num + 1일차 in remainder
                splited = remainder.split(f"{int(num) + 1}일차")
                message_for_day = splited[0]
                if i != len(has_multiple_days) - 1:
                    remainder = f"{int(num) + 1}일차" + "".join(splited[1:])

                all_messages.append({
                    **message,
                    "text": message_for_day,
                })
        else:
            all_messages = [message]

        for message in all_messages:
            # 1일차, 2일차... 가 포함되어 있는지 확인
            is_report = re.search(r"\d+일차", message["text"])

            if is_report:
                # 몇 일차인지 추출
                day = int(re.search(r"\d+", message["text"]).group())

                # {이름: set([1, 2, 3...])} 형태
                if message["name"] not in count_dict:
                    count_dict[message["name"]] = set()
                submitted_date = message["date"]
                required = required_report_num(start_date, submitted_date)
                count_dict[message["name"]].add((day, "지각" if day < required else "출석"))
    return count_dict


def count_reports_submitted(messages):
    count_dict = count_reports_in_dict(messages)
    # {이름: 제출한 일차 수} 형태로 변환
    for name, (days, _) in count_dict.items():
        count_dict[name] = len(days)

    return count_dict


def 출석체크_엑셀(messages, required_num, start_date=None, limit=None):
    if start_date is None:
        start_date = datetime(2020, 4, 20)

    people = get_invited_people(messages)
    print(people)
    count_dict = count_reports_in_dict(messages, start_date)
    people_attend = {name: [] for name in people}

    for i in range(1, required_num + 1):
        for person in people:
            if person not in count_dict:
                count_dict[person] = set()

            if (i, "출석") in count_dict[person]:
                people_attend[person].append("출석")
            elif (i, "지각") in count_dict[person]:
                people_attend[person].append("지각")
            else:
                people_attend[person].append("결석")

    if limit is not None:
        result = ["이름, 출석, 지각, 결석," + ", ".join([f"{i}일차" for i in range(1, required_num + 1)][-limit:])]
    else:
        result = ["이름, 출석, 지각, 결석, " + ", ".join([f"{i}일차" for i in range(1, required_num + 1)])]

    for name, attend in people_attend.items():
        count_출석 = f"{attend.count('출석')}"
        count_지각 = f"{attend.count('지각')}"
        count_결석 = f"{attend.count('결석')}"
        if limit is not None:
            result.append(", ".join([name, count_출석, count_지각, count_결석] + attend[-limit:]))
        else:
            result.append(", ".join([name, count_출석, count_지각, count_결석] + attend))
    
    return "\n".join(result)


def 독서일지만_추출(messages):
    """ 독서일지는 1일차, 2일차, 3일차 ~ 48일차로 시작하는 메시지
    """
    result = []
    for message in messages:
        if re.match(r"\d+일차", message["text"]):
            result.append(message)
    return result


def 메시지_사람별로_그루핑(messages):
    result = {}
    for message in messages:
        if message["name"] not in result:
            result[message["name"]] = []
        result[message["name"]].append(message)
    return result


def get_reports_of(person, messages):
    reports = 독서일지만_추출(messages)
    person_messages = 메시지_사람별로_그루핑(reports)[person]
    return [message["text"] for message in person_messages]
