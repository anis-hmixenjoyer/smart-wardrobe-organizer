import os
import google.generativeai as genai
import json
import requests
from dotenv import load_dotenv


load_dotenv()


GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")


try:
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
except Exception as e:
    print(f"Error configuring Google API: {e}. Make sure GOOGLE_API_KEY is set.")


def clean_json_response(response_text):
    """
    Helper function to clean and extract JSON from Gemini's response.
    Handles markdown code blocks like ```json ... ``` or ``` ... ```.
    """
    response_text = response_text.strip()
    if response_text.startswith("```json") and response_text.endswith("```"):
        return response_text[7:-3].strip()  
    elif response_text.startswith("```") and response_text.endswith("```"):
        return response_text[3:-3].strip()  
    else:
        return response_text  


def get_weather_data(city_name):
    """Fetches temperature and weather conditions from OpenWeatherMap."""
   
    if not OPENWEATHER_API_KEY:
        print("OPENWEATHER_API_KEY not found. Using default weather.")
        return "Unknown, default to pleasant weather (25°C, Clear)"
       
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city_name,
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric',
        'lang': 'en'      
    }


    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
       
        temperature = data['main']['temp']
        description = data['weather'][0]['description'].capitalize()
       
        weather_string = f"Temperature: {temperature}°C, Condition: {description}."
       
        if temperature > 30:
            weather_string += " It's very hot and sunny."
        elif temperature < 15:
            weather_string += " It's cold. Layering is needed."
           
        return weather_string
       
    except requests.exceptions.RequestException as e:


        print(f"Error fetching weather data for city '{city_name}': {e}")
        return "Unknown, default to pleasant weather (25°C, Clear)"


def get_ootd_feedback(item_list, current_weather):
    """
    Sends a list of items (as dict/json) to Google Gemini
    to get fashion feedback.
    """
   
    items_json_string = json.dumps(item_list, indent=2)
   
    model = genai.GenerativeModel('gemini-2.5-flash')
   
    prompt = (
        "You are the 'OOTD Oracle', a friendly and supportive AI fashion stylist.\n"
        "Your task is to evaluate the compatibility of the following clothing combination, provided in JSON format:\n"
        f"{items_json_string}\n\n"
       
        f"The current weather condition is: {current_weather}\n"
        "Please CONSIDER this weather in your assessment (e.g., don't recommend a thick jacket in hot weather).\n"


        "Based on the input AND THE WEATHER, provide an assessment for a 'Casual' event.\n"
        "Provide the response ONLY in the following valid JSON format, with no additional text outside the JSON:\n"
        "{\n"
        "  \"rating\": (a number 1-10),\n"
        "  \"feedback\": \"(A brief comment, e.g., 'This combination works well!' or 'Hmm, this doesn't quite match.')\",\n"
        "  \"saran\": \"(One sentence of advice for improvement OR a compliment related to the weather, e.g., 'Your linen choice is perfect for the hot weather!' or 'This might be too warm for the current conditions.')\"\n"
        "}\n"
    )


   
    try:
        response = model.generate_content(prompt)
       
        ai_output = clean_json_response(response.text)
       
        parsed_json = json.loads(ai_output)
       
        required_keys = {"rating", "feedback", "saran"}
        if not required_keys.issubset(parsed_json.keys()):


            raise ValueError("AI response is missing the expected JSON format.")
       
        return parsed_json


    except json.JSONDecodeError as e:


        print(f"Error parsing JSON from AI: {e}")
        ai_output = response.text
        print(f"Raw output from AI: {ai_output}")
        return {
            "rating": 0,
            "feedback": "Error: AI response was not valid JSON.",
            "saran": f"Error detail: {str(e)}"
        }
    except Exception as e:


        print(f"Error getting OOTD feedback (Gemini): {e}")
        ai_output = getattr(response, 'text', 'No response') if 'response' in locals() else 'No response'
        print(f"Raw output from AI: {ai_output}")
        return {
            "rating": 0,
            "feedback": "Error: A problem occurred while contacting the AI.",
            "saran": str(e)
        }


if __name__ == "__main__":
    print("--- Starting Styling Logic Test (with Weather) ---")
   
    TEST_CITY = "Depok"


    current_weather = get_weather_data(TEST_CITY)
    print(f"Weather in {TEST_CITY}: {current_weather}")
   
    selected_outfit_items = [
        {'type': 'Top', 'color': 'White', 'style': 'Thin Linen Shirt'},
        {'type': 'Bottom', 'color': 'Light Blue', 'style': 'Short Chinos'}
    ]
   
    print("\nItems Under Test:")
    for item in selected_outfit_items:


        print(f" - {item['style']} ({item['color']})")


    hasil_feedback = get_ootd_feedback(selected_outfit_items, current_weather)
   
    if hasil_feedback and hasil_feedback.get('rating', 0) > 0:
        print("\n[OK] AI Feedback Result (Printed to Terminal):")
        print(json.dumps(hasil_feedback, indent=2))
       
        print(f"\nRating: {hasil_feedback.get('rating')}/10")
        print(f"Feedback: {hasil_feedback.get('feedback')}")
        print(f"Suggestion: {hasil_feedback.get('saran')}")
    else:
        print("\n[FAILED] Failed to get valid feedback.")
        print("Details:", json.dumps(hasil_feedback, indent=2))
       
    print("\n--- Test Complete ---")

