import os
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import chat as chat

from 출첵.kakao import utils, conversations
from 출첵.domains.일지 import required_report_num


app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def index():
    return "Hello World!"


@app.route("/get_situation", methods=["GET"])
def get_situation_route():
    topic = request.args.get("topic", "")
    lang = request.args.get("lang", "ko")
    prompt, situation = chat.get_situation(topic, lang)
    return jsonify(
        {
            "prompt": prompt,
            "situation": situation,
        }
    )


@app.route("/init_opponent", methods=["POST"])
def init_opponent_route():
    situation = request.get_json()
    lang = request.args.get("lang", "ko")

    prompt, opponent = chat.get_initial_opponent(situation, lang=lang)
    return jsonify({"opponent": opponent, "prompt": prompt})


@app.route("/response_to_customer", methods=["POST"])
def response_to_customer_route():
    data = request.get_json()
    opponent = data.get("opponent")
    answer = data.get("answer")
    history = data.get("history", [])
    lang = request.args.get("lang", "ko")

    logging.info(f"history: {history}")
    input_prompt, updated_opponent = chat.response_to_customer(
        opponent, 
        answer, 
        history,
        lang=lang
    )
    return jsonify({
        "opponent": updated_opponent,
        "inputPrompt": input_prompt,
    })


@app.route("/evaluate_conversation", methods=["POST"])
def evaluate_conversation_route():
    history = request.get_json()
    lang = request.args.get("lang", "ko")

    feedback = chat.evaluate_conversation(history, lang=lang)
    return jsonify(feedback)


@app.route("/attendance", methods=["POST"])
def attendance_route():
    body = request.get_json()
    _conversations = body.get("conversations")
    start_date = body.get("start_date")
    start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
    messages = conversations.preprocess(_conversations)

    text = utils.출석체크_엑셀(
        messages,
        required_report_num(
            start_date, datetime.now()
            ), start_date
    )
    # response content type must be 'text/csv'
    return jsonify({"csv": text})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
