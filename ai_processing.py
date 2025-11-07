import os
import google.generativeai as genai
from PIL import Image
import io
from rembg import remove
import json

try:
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
except Exception as e:
    print(f"Error configuring Google API: {e}. Make sure GOOGLE_API_KEY is set.")

def clean_json_response(response_text):
    """
    Helper function to clean and extract JSON from Gemini's response.
    Handles markdown code blocks like ```json ... ``` or ``` ... ```.
    (This function is kept consistent with styling_logic.py)
    """
    response_text = response_text.strip()
    if response_text.startswith("```json") and response_text.endswith("```"):
        return response_text[7:-3].strip()
    elif response_text.startswith("```") and response_text.endswith("```"):
        return response_text[3:-3].strip()
    else:
        return response_text

def remove_background(image_path):
    """
    Removes the background from an image and returns it
    as a PIL.Image object.
    """
    print(f"Starting background removal for: {image_path}")
    try:
        with open(image_path, "rb") as f:
            input_bytes = f.read()
        
        output_bytes = remove(input_bytes)
        
        processed_image = Image.open(io.BytesIO(output_bytes))
        print("Background removed successfully.")
        return processed_image
    
    except Exception as e:
        print(f"Error during background removal: {e}")
        return Image.open(image_path)

def classify_item(image_path):
    """Sends an image to the Google Gemini Vision API for classification."""
    try:
        img = Image.open(image_path)

        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = (
            "Classify the clothing item in this image. "
            "Provide the response ONLY in the following JSON format. "
            "IMPORTANT: All keys and values in the JSON must be in English:"
            "{'type': '...', 'color': '...', 'style': '...'}."
            "The 'type' must be one of: Top, Bottom, Outerwear, Dress, Shoes, Accessory. "
            "The 'style' must describe the model or material (e.g., 'Plain Shirt', 'Slim Fit Jeans')."
        )

        response = model.generate_content([prompt, img])
        ai_output = clean_json_response(response.text)
        
        parsed_json = json.loads(ai_output)
        
        required_keys = {"type", "color", "style"}
        if not required_keys.issubset(parsed_json.keys()):
            raise ValueError("AI Vision response is missing the expected English JSON format.")

        return parsed_json

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from AI Vision: {e}")
        ai_output = response.text
        print(f"Raw output from AI Vision: {ai_output}")
        return None
    except Exception as e:
        print(f"Error during AI Vision classification (Gemini): {e}")
        return None