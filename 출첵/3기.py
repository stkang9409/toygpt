from datetime import datetime
from kakao import conversations, utils
from domains.일지 import required_report_num


def save_reports_of(person, messages):
    reports = utils.get_reports_of(person, messages)
    with open(f"./reports/3기/{person}.md", "w") as f:
        f.write("\n\n---------------------------\n\n".join(reports))


def save_attendance(messages):
    start_date = datetime(2023, 4, 24, 8)
    with open("./conversations/3기_출석.csv", "w") as csvfile:
        csv = utils.출석체크_엑셀(messages, required_report_num(start_date, datetime.now()), start_date)
        csvfile.write(csv)


if __name__ == "__main__":
    filename = "./conversations/3기.txt"
    if filename.endswith(".csv"):
        processor = conversations.preprocess_csv
    elif filename.endswith(".txt"):
        processor = conversations.preprocess

    with open(filename) as csvfile:
        messages = processor(csvfile)
        save_attendance(messages)
        # save_reports_of("송예은", messages)
    

        

        
    

