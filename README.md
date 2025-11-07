# Smart Wardrobe Organizer 👗

**Your Personal Fashion Assistant. No more "I have nothing to wear" moments.**

*A project for the Blackbox.AI x PNJ Hackathon.*

This web application allows you to catalog your entire wardrobe just by uploading photos. Our AI analyzes your clothes, saves them to a digital closet, and then acts as your personal fashion stylist to give you mix-and-match recommendations.

This project is a case study in how **Blackbox.AI (The Coding Assistant)** empowers developers to rapidly integrate and build with other advanced AI APIs (like Google Gemini).

## ✨ Key Features

* **Automatic Cataloging:** Upload a clothing item, and the AI (Gemini) will instantly identify its **Type**, **Color**, and **Style**.
* **Visual Digital Closet:** View your entire collection in an easy-to-search, filterable visual grid.
* **AI Mix & Match:** Select 2-3 items from your closet, and the AI will provide a compatibility **rating** and styling advice.
* **Modern Design:** A clean, responsive interface built on Streamlit with custom CSS styling.

## 💻 Tech Stack

* **Programming Language:** Python (3.11.9)
* **Application Framework:** [Streamlit](https://streamlit.io/)
* **AI Vision & Logic:** [Google Gemini API](https://ai.google.dev/) (Model `gemini-2.5-flash`)
* **Styling:** Custom CSS
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
    git clone https://github.com/anis-hmixenjoyer/smart-wardrobe-organizer.git
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

### 3. API Key Configuration (Crucial Step)

This application requires a Google Gemini API Key to function.

1.  Go to [**Google AI Studio**](https://aistudio.google.com/).
2.  Log in and create a new API Key.
3.  The **Free Tier** is more than sufficient for this hackathon.
4.  **Save the API Key to Your Local Environment.**
    Open a terminal (NOT inside the `venv`) and run:
    ```bash
    # For Windows
    setx GOOGLE_API_KEY "PASTE_YOUR_API_KEY_HERE"
    
    # For Mac/Linux
    echo "export GOOGLE_API_KEY='YOUR_KEY_HERE'" >> ~/.zshrc && source ~/.zshrc
    ```
5.  **IMPORTANT:** **Close and re-open** your terminal for the new key to be recognized.

> **SECURITY WARNING:**
> Never hard-code your API key in the (`.py`) files or push it to GitHub. This project's `.gitignore` is set up to ignore data files, but it is your responsibility to keep your API key secure locally.

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
