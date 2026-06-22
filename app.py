import os

from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types
imort os

app = Flask(__name__)

# 1. Initialize the Gemini Client
try:
    # PASTE YOUR ACTUAL API KEY HERE
    # Replace the line that has your actual key with this exact line:
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
except Exception as e:
    print(f"Failed to initialize client: {e}")

# 2. Define the AI's Brain (Triage Protocol)
system_instruction = """
You are a community health educator assisting NGO workers and local communities. 
Your primary goal is safety and accurate preliminary triage, not diagnosing.

STRICT INTERACTION RULES:
1. NEVER guess or assume. If a user states a vague symptom (e.g., "I have a fever" or "My stomach hurts"), DO NOT immediately offer remedies.
2. ALWAYS ask 1 to 2 clarifying follow-up questions first. Ask about:
   - Duration (How long has this been happening?)
   - Severity (Is the pain mild, moderate, or severe?)
   - Accompanying symptoms (Are there any other issues like nausea or dizziness?)
3. Ask only ONE simple question at a time so you do not overwhelm the user.
4. Once you have enough context, provide clear, accessible information on preventative care or standard first-aid.
5. If at any point the symptoms sound severe (e.g., high fever for days, chest pain, difficulty breathing), immediately stop asking questions and advise visiting the nearest Primary Health Center (PHC) or calling emergency services.

STRICT BOUNDARY: If the user asks a question NOT related to health, hygiene, sanitation, or first-aid, politely refuse to answer.

Respond in simple, easy-to-understand language.
"""

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    # Receive the entire chat history array from the frontend
    history = data.get("history", [])
    user_message = data.get("message")
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        # Format the history into the structure the Gemini SDK expects
        formatted_contents = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            formatted_contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg["content"])]
                )
            )
        
        # Append the latest user message to the end of the history sequence
        formatted_contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_message)]
            )
        )

        # Generate the response using the CORRECT model name
        response = client.models.generate_content(
            model="gemini-3.5-flash", # <--- CHANGE THIS BACK
            contents=formatted_contents, 
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2 
            )
        )
        return jsonify({"response": response.text})
        
    except Exception as e:
        # This will print the exact Google API error in your terminal if it fails
        print(f"🚨 GEMINI ERROR: {str(e)}") 
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)