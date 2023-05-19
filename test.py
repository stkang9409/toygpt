import requests

url = " http://util.keysams.com:5000/attendance"

if __name__ == "__main__":
    with open("./conversations/대화.txt") as f:
        messages = f.read()
        result = requests.post(url, json={
            "conversations": messages,
            "start_date": "2023-04-24 08:00:00"
        })
        print(result.status_code)
        print(result.json())