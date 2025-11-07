# Smart Wardrobe Organizer 👗

**Your Personal Fashion Assistant. No more "I have nothing to wear" moments.**

*A project for the Blackbox.AI x PNJ Hackathon.*

This web application allows you to catalog your entire wardrobe just by uploading photos. Our AI analyzes your clothes, removes the background, saves them to a digital closet, and then acts as your personal fashion stylist to give you mix-and-match recommendations based on your local weather.

This project is a case study in how **Blackbox.AI (The Coding Assistant)** empowers developers to rapidly integrate and build with other advanced AI APIs.

## ✨ Key Features

* **Automatic Cataloging:** Upload a clothing item, and the AI API will instantly identify its **Type**, **Color**, and **Style**.
* **AI Background Removal:** Automatically removes the background from your clothing photos (using `rembg`) for a clean look in your digital closet.
* **Visual Digital Closet:** View your entire collection in an easy-to-search, filterable visual grid.
* **Weather-Aware AI Stylist:** Select 2-3 items, and our AI Stylist will provide a compatibility **rating** and styling advice **based on your local weather**.

## 💻 Tech Stack

* **Programming Language:** Python (3.11.9)
* **Application Framework:** [Streamlit](https://streamlit.io/)
* **AI Vision & Logic:** [Google Gemini API](https://ai.google.dev/) (Model `gemini-2.5-flash`)
* **Background Removal:** [rembg](https://github.com/danielgatis/rembg)
* **Weather Data:** [OpenWeatherMap API](https://openweathermap.org/api)
* **Environment:** `venv` & `pip`

## 🚀 Getting Started

Follow these steps to get a local copy up and running.

### 1. Prerequisites

* Ensure you have [Python 3.8 - 3.13](https://www.python.org/downloads/) installed.
* Ensure you have [Git](https://git-scm.com/downloads) installed.

### 2. Local Installation

1.  **Clone the Repository**
    Open your terminal and clone the project:
    ```bash
    git clone [https://github.com/anis-hmixenjoyer/smart-wardrobe-organizer.git](https://github.com/anis-hmixenjoyer/smart-wardrobe-organizer.git)
    cd smart-wardrobe-organizer
    ```

2.  **Create a Virtual Environment**
    It's highly recommended to use a `venv` to prevent dependency conflicts.
    ```bash
    # Create the venv
    python -m venv venv
    
    # Activate venv (Windows)
    .\venv\Scripts\activate
    
    # Activate venv (Mac/Linux)
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    All required libraries are listed in `requirements.txt`.
    ```bash
    # Make sure your (venv) is active
    pip install -r requirements.txt
    ```

    > **Note on `rembg`:**
    > The `rembg` library requires a specific runtime. If you encounter an error when running the app, you may need to install `onnxruntime` manually:
    > ```bash
    > pip install onnxruntime
    > ```

### 3. API Key & Environment Setup (.env)

This application requires **two API keys** to function. We will use a `.env` file to keep them secure.

1.  **Create the `.env` file**
    In the main project folder (next to `app.py`), create a new file named:
    `.env`

2.  **Add Your Keys**
    Open the `.env` file with a text editor and add your API keys in this format:

    ```ini
    GOOGLE_API_KEY="PASTE_YOUR_GEMINI_API_KEY_HERE"
    OPENWEATHER_API_KEY="PASTE_YOUR_OPENWEATHER_API_KEY_HERE"
    ```

3.  **Where to Get These Keys:**
    * **`GOOGLE_API_KEY`:** Get it from [**Google AI Studio**](https://aistudio.google.com/). Log in and create a new API key. The **Free Tier** is more than sufficient.
    * **`OPENWEATHER_API_KEY`:**
        1.  Sign up at [**OpenWeatherMap**](https://openweathermap.org/price).
        2.  Choose the **"Free"** plan (Current Weather Data).
        3.  After signing up, go to "My API Keys" to find your key. 

> **SECURITY WARNING:**
> The `.gitignore` file in this project is already configured to **ignore the `.env` file**. This is VERY IMPORTANT to prevent your secret API keys from being uploaded to GitHub.
> **Never** share your `.env` file or write your keys directly in your `.py` files.

## ▶️ Running the Application

1.  Open your terminal.
2.  Navigate to the project folder: `cd smart-wardrobe-organizer`
3.  Activate your `venv`: `.\venv\Scripts\activate`
4.  Run the Streamlit app:
    ```bash
    streamlit run app.py
    ```
5.  Open your browser and go to `http://localhost:8501`.

## 👩‍💻 Our Team

* **AI Vision & Data:** [@anis-hmixenjoyer](https://github.com/anis-hmixenjoyer)
* **Backend & LLM:** [@pandora-jisung](https://github.com/pandora-jisung)
* **Frontend & UI/UX:** [@Wanda234134](https://github.com/Wanda234134)

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
