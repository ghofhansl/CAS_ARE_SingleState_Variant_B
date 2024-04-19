import os
from flask import Flask, jsonify, render_template, request, send_file

from chatbot.chatbot import Chatbot

PYTHONANYWHERE_USERNAME = "carvice"
PYTHONANYWHERE_WEBAPPNAME = "mysite"

app = Flask(__name__)

my_type_role = """
Imagine you are a chatbot designed to help users retrieve lost memories. 
Begin the conversation by warmly greeting the user and expressing your readiness to assist. 
Ask the user detailed questions to gather as much information as possible about the memory they are trying to recall. 
This could include when the event might have occurred, who was present, where it took place, or any sensations associated with it. 
Use this information to suggest potential memories, ask clarifying questions, and guide the user in reconstructing their memory. 
Remember to be empathetic and patient, offering reassurances as they attempt to remember.
"""

my_instance_context = """
Additionally, integrate closed questions to narrow down possibilities and confirm details about the memory. 
Use yes-no questions or choices to help the user make decisions about specific aspects of the memory. 
For instance, you could ask: 'Did this event happen during a special occasion like a birthday or a holiday?', 
'Were you indoors or outdoors when this occurred?', or 
'Is there a specific person you remember being there?' 
These targeted questions can help clarify the details and confirm elements of the memory, 
aiding in the reconstruction process. Ensure that your tone remains encouraging and patient as you help the user focus and specify their recollections.
"""

my_instance_starter = """
Hello there!
I'm here to help you uncover and piece together memories that seem a bit fuzzy right now. Don't worry if you can't remember everything clearly—just share whatever bits and pieces come to mind, and together, we'll try to make sense of them. How about we start with what you remember, no matter how small? I’m here to help every step of the way!
"""

bot = Chatbot(
    database_file="database/chatbot.db", 
    type_id="coach",
    user_id="daniel",
    type_name="Memory finder",
    type_role=my_type_role,
    instance_context=my_instance_context,
    instance_starter=my_instance_starter
)

bot.start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/mockups.pdf', methods=['GET'])
def get_first_pdf():
    script_directory = os.path.dirname(os.path.realpath(__file__))
    files = [f for f in os.listdir(script_directory) if os.path.isfile(os.path.join(script_directory, f))]
    pdf_files = [f for f in files if f.lower().endswith('.pdf')]
    if pdf_files:
        # Get the path to the first PDF file
        pdf_path = os.path.join(script_directory, pdf_files[0])

        # Send the PDF file as a response
        return send_file(pdf_path, as_attachment=True)

    return "No PDF file found in the root folder."

@app.route("/<type_id>/<user_id>/chat")
def chatbot(type_id: str, user_id: str):
    return render_template("chat.html")


@app.route("/<type_id>/<user_id>/info")
def info_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: dict[str, str] = bot.info_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/conversation")
def conversation_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: list[dict[str, str]] = bot.conversation_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/response_for", methods=["POST"])
def response_for(type_id: str, user_id: str):
    user_says = None
    # content_type = request.headers.get('Content-Type')
    # if (content_type == 'application/json; charset=utf-8'):
    user_says = request.json
    # else:
    #    return jsonify('/response_for request must have content_type == application/json')

    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    assistant_says_list: list[str] = bot.respond(user_says)
    response: dict[str, str] = {
        "user_says": user_says,
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)


@app.route("/<type_id>/<user_id>/reset", methods=["DELETE"])
def reset(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    bot.reset()
    assistant_says_list: list[str] = bot.start()
    response: dict[str, str] = {
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)
