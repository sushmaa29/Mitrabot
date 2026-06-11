import logging

from flask import jsonify
from flask import Blueprint, request
import json
from services.speech_service import speech_to_text
from agents.mental_health_agent import MentalHealthAIAgent
from utils.eliza import analyze

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ai_routes = Blueprint("ai", __name__)

@ai_routes.post("/ai/mental_health/welcome/<user_id>")
def get_mental_health_agent_welcome(user_id):
    print("AI ROUTE HIT")
    try:
        agent = MentalHealthAIAgent()
        response = agent.get_initial_greeting(user_id)
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Error in welcome: {str(e)}")
        response = {
            "message": "Welcome to your safe space! I'm here to listen. How are you feeling today?",
            "chat_id": 12345
        }
        return jsonify(response), 200

@ai_routes.post("/ai/mental_health/<user_id>/<chat_id>")
def run_mental_health_agent(user_id, chat_id):
    print("AI ROUTE HIT")

    body = request.get_json()
    prompt = body.get("prompt", "")
    turn_id = body.get("turn_id", 0)
    
    try:
        agent = MentalHealthAIAgent()
        if chat_id == "null":
            chat_id = agent.get_chat_id(user_id)
        response = agent.run(message=prompt, with_history=True, user_id=user_id, chat_id=int(chat_id), turn_id=turn_id)
        return jsonify({"response": response}), 200
    except Exception as e:
        logger.error(f"Error in agent run: {str(e)}")
        if "Environment variable GOOGLE_API_KEY is not set" in str(e):
            response = "I am currently running in limited mode. To receive personalized solutions, please add your GOOGLE_API_KEY to the server/.env file and restart the backend."
        else:
            response = f"An error occurred while connecting to the AI service: {str(e)}"

        return jsonify({
            "response": response
        }), 200

@ai_routes.patch("/ai/mental_health/finalize/<user_id>/<chat_id>")
def set_mental_health_end_state(user_id, chat_id):
    logger.info(f"Finalizing chat {chat_id} for user {user_id}")
    try:
        agent = MentalHealthAIAgent()
        agent.perform_final_processes(user_id, chat_id)
    except Exception as e:
        logger.error(f"Error in finalizing chat: {str(e)}")
    return jsonify({"message": "Chat session finalized successfully"}), 200
    

@ai_routes.post("/ai/mental_health/voice-to-text")
def handle_voice_input():
        # Check if the part 'audio' is present in files
        if 'audio' not in request.files:
            return jsonify({'error': 'Audio file is required'}), 400
        # Assume the voice data is sent as a file or binary data
        voice_data = request.files['audio']

        # Save the temporary audio file if needed or pass directly to the speech_to_text function
        text_output = speech_to_text(voice_data)
        
        if text_output:
            return jsonify({'message': text_output}), 200
        else:
            return jsonify({'error': 'Speech recognition failed'}), 400