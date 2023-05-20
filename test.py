import requests

base_url = "http://localhost:5000"
url = f"{base_url}/attendance"
reports_url = f"{base_url}/reports"

if __name__ == "__main__":
    # with open("./conversations/대화.txt") as f:
    #     messages = f.read()
    #     result = requests.post(url, json={
    #         "conversations": messages,
    #         "start_date": "2023-04-24 08:00:00"
    #     })
    #     print(result.status_code)
    #     print(result.json())

    with open("./conversations/대화.txt") as f:
        messages = f.read()
        result = requests.post(reports_url, json={
            "conversations": messages,
            "person": "리경"
        })
        print(result.status_code)
        print(result.json())