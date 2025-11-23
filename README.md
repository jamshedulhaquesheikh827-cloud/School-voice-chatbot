# 🏫 School Voice Assistant (MGSDO Version)

A child-friendly, voice-enabled chatbot for school queries. Parents and students can ask questions via text or voice in Roman Urdu/English.

## ✨ Features
- **Voice Chat**: Click the microphone to speak your question.
- **Text Chat**: Type your questions normally.
- **Audio Response**: The bot speaks back the answer!
- **Smart FAQ**: Instantly answers common questions (Fees, Timing, Holidays).
- **AI Powered**: Uses Gemini AI for questions not in the FAQ.
- **Child-Friendly UI**: Colorful and easy to use.

## 🚀 How to Run Locally

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: You may need to install ffmpeg for audio processing if it's not on your system.*

2.  **Set up API Key**:
    - Create a `.env` file in this directory.
    - Add your Gemini API key:
      ```
      GEMINI_API_KEY=your_api_key_here
      ```

3.  **Run the App**:
    ```bash
    streamlit run app.py
    ```

## ☁️ How to Deploy to Streamlit Cloud

1.  **Push to GitHub**: Upload all these files (`app.py`, `requirements.txt`, `school-faq.txt`) to a GitHub repository.
2.  **Go to Streamlit Cloud**: Visit [share.streamlit.io](https://share.streamlit.io/).
3.  **Deploy**:
    - Click "New App".
    - Select your GitHub repository.
    - Set the main file path to `app.py`.
    - Click "Deploy".
4.  **Add Secrets**:
    - In your app dashboard, go to "Settings" -> "Secrets".
    - Add your API key:
      ```toml
      GEMINI_API_KEY = "your_api_key_here"
      ```

## 🛠️ Files Included
- `app.py`: The main application code.
- `school-faq.txt`: The knowledge base for the bot.
- `requirements.txt`: List of Python libraries needed.

## 🧪 Test It
Try asking:
- "Kal chutti hai?"
- "Admission fee kitni hai?"
- "Principal ka naam kya hai?"
