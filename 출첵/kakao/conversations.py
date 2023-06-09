import re
from datetime import datetime


def preprocess_csv(csv_file):
    messages = []
    for line in csv_file.split("\n"):
        if idx == 0:
            continue

        if not line:
            continue

        line = line.strip()
        line = line.strip("\n")
        line = line.strip("﻿")

        # 2023-04-22 14:10:25,"강민규","강민규님이 들어왔습니다."
        is_start_with_date = re.match(
            r"\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}", line
        )
        if is_start_with_date:
            if messages:
                messages[-1]["text"] = messages[-1]["text"].strip("\n").strip()

            date = is_start_with_date.group()

            rest_of_line = line.split(date)[-1].strip()

            date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

            if not rest_of_line:
                messages.append({"date": date, "name": "시스템", "text": ""})
                continue

            rest_of_line = rest_of_line.strip(",")

            has_name = re.match(r".+,.+", rest_of_line)
            if not has_name:
                messages.append(
                    {"date": date, "name": "시스템", "text": rest_of_line.strip('"')}
                )
                continue

            name = rest_of_line.split(",")[0]
            text = ",".join(rest_of_line.split(",")[1:])
            messages.append(
                {
                    "date": date,
                    "name": name.strip('"'),
                    "text": text.strip('"').strip("\n"),
                }
            )
        else:
            if not messages:
                messages.append({
                    "date": datetime.now(),
                    "name": "시스템",
                    "text": ""
                })
            messages[-1]["text"] += "\n" + line.strip('"\n')

    return messages


def preprocess(text):
    messages = []
    for line in text.split("\n"):
        if not line:
            continue
        line = line.strip()
        line = line.strip("\n")
        line = line.strip("﻿")

        # 2023년 4월 22일 오전 11:08, 2023년 3월 11일 오후 5:48, 2023년 4월 22일 오후 2:10
        is_start_with_date = re.match(
            r"\d{4}년 \d{1,2}월 \d{1,2}일 (오전|오후) \d{1,2}:\d{1,2}", line
        )
        if is_start_with_date:
            if messages:
                messages[-1]["text"] = messages[-1]["text"].strip("\n").strip()

            date = is_start_with_date.group()

            rest_of_line = line.split(date)[-1].strip()

            date = date.replace("오전", "AM").replace("오후", "PM")
            date = datetime.strptime(date, "%Y년 %m월 %d일 %p %I:%M")

            if not rest_of_line:
                messages.append({"date": date, "name": "시스템", "text": ""})
                continue

            rest_of_line = rest_of_line.strip(", ")
            import sys
            has_name = re.match(r".+ : *", rest_of_line)
            if not has_name:
                messages.append(
                    {"date": date, "name": "시스템", "text": rest_of_line.strip()}
                )
                continue

            name = rest_of_line.split(" :")[0].strip()
            text = rest_of_line.split(" :")[1].strip()
            messages.append({"date": date, "name": name.strip(), "text": text.strip()})
        else:
            if not messages:
                messages.append({
                    "date": datetime.now(),
                    "name": "시스템",
                    "text": ""
                })
            messages[-1]["text"] += "\n" + line
    return messages
