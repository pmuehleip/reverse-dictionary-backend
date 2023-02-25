import os

import openai
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*")
openai.api_key = os.getenv("OPENAI_API_KEY")

ip_request_count = dict()

@app.route("/")
def hello_from_root():
    return jsonify(message='Hello from root!')


@app.route("/hello")
def hello():
    return jsonify(message='Hello from path!')

def parse_numbered_list(input_str):
    input_list = input_str.split("\n")  # split the input string into a list of strings by newline character
    output_list = []
    
    # loop through each string in the input list
    for item in input_list:
        # check if the string starts with a number and a period
        if item and item[0].isdigit() and item[1] == ".":
            # remove the number and period and add the remaining string to the output list
            output_list.append(item[2:].strip())
    # return the output list
    return output_list

@app.route("/search", methods=["POST"])
def search():
    definition = request.json.get('definition')

    if len(definition) > 100:
            return make_response(jsonify(error='definiton is limited to 100 characters'), 400)

    ip_request_count[request.remote_addr] = ip_request_count.get(request.remote_addr, 0) + 1
    if ip_request_count[request.remote_addr] > 10:
        return make_response(jsonify(error="You've exceeded your quota of 10 requests"), 429)

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=generate_prompt(definition),
        temperature=0.6,
        max_tokens=100
    )

    result = parse_numbered_list(response.choices[0].text)
    print(response)
    print(result)
    return jsonify(result), 201


def generate_prompt(definition):
    return """Given a definition, return the top 5 words that best describe that definition.

Definition: {}
Words:
""".format(
        definition.capitalize()
    )


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)
