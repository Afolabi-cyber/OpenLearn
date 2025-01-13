from flask import Flask, render_template, request, jsonify, Response
import os
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
import json

# Load environment variables
load_dotenv()  # Load the .env file for environment variables

# Initialize Flask app
app = Flask(__name__)

# Set up Gemini API configuration
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Ensure uploads directory exists
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set up Gemini Model
model = genai.GenerativeModel('gemini-1.5-flash')

# Function to get the Gemini response
def get_gemini_response(input_text, image=None):
    try:
        if image:
            response = model.generate_content([input_text, image])
        else:
            response = model.generate_content(input_text)
        return response.text  # Assuming the response contains a 'text' attribute
    except Exception as e:
        return f"Error: {str(e)}"

# Route for the homepage (uploads assignment and interacts with chatbot)
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        uploaded_file = request.files.get('assignment')
        if uploaded_file:
            file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
            uploaded_file.save(file_path)
            return jsonify({"success": True, "file_path": file_path}), 200
        else:
            return jsonify({"error": "No file uploaded"}), 400

    return render_template("home.html")

# Route for generating quiz
@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    questions = []
    topic = ""
    if request.method == "POST":
        topic = request.form.get("topic")
        if topic:
            response = get_gemini_response(topic)
            questions = response.split('\n')  # Assuming the response is a list of questions
    return render_template("quiz.html", questions=questions, topic=topic)

# Route for interacting with the chatbot
@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    if request.method == "POST":
        data = request.get_json()
        user_message = data.get("message", "")

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        try:
            response = get_gemini_response(user_message)
            return jsonify({"response": response})
        except Exception as e:
            return jsonify({"error": f"Failed to get response: {str(e)}"}), 500

    return render_template("chatbot.html")

# Route for handling image-based questions
@app.route("/ask_image_question", methods=["POST"])
def ask_image_question():
    data = request.json
    question = data.get('question')
    file_path = data.get('file_path')

    if not question:
        return jsonify({"error": "No question provided"}), 400

    if not file_path:
        return jsonify({"error": "No image uploaded"}), 400

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 400

    try:
        image = Image.open(file_path)
        response = get_gemini_response(question, image)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": f"Failed to process image: {str(e)}"}), 500

# Route for dashboard
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)
