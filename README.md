# 🎬 Retrievia – AI Video Assistant with RAG

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python"/>
  <img src="https://img.shields.io/badge/Streamlit-Web_App-red?style=for-the-badge&logo=streamlit"/>
  <img src="https://img.shields.io/badge/LangChain-RAG-green?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/License-MIT-purple?style=for-the-badge"/>
</p>

<p align="center">
AI-powered Video Assistant that transcribes videos, generates intelligent summaries, extracts key insights, and enables conversational Q&A using Retrieval-Augmented Generation (RAG).
</p>

---

## 🚀 Demo

🌐 **Live Demo:** https://retrievia.streamlit.app/
📂 **GitHub:** https://github.com/shivansh4565/Retrievia

---

# ✨ Features

### 🎥 Video Processing
- Supports YouTube URLs
- Supports Local Video Files
- Automatic Audio Extraction

### 🎙️ AI Transcription
- Speech-to-Text
- English & Hinglish Support
- Accurate Meeting Transcripts

### 📝 Smart Summarization
- AI Generated Summary
- Session Title Generation
- Concise Meeting Notes

### 📌 Information Extraction
- ✅ Action Items
- 🔑 Key Decisions
- ❓ Open Questions

### 💬 AI Chat (RAG)
- Ask questions about your video
- Semantic Retrieval
- Context-Aware Responses
- Natural Language Conversation

### 🎨 Modern UI
- Beautiful Glassmorphism Design
- Responsive Interface
- Interactive Chat Experience

---

# 🏗️ System Architecture

```text
            YouTube URL / Video File
                      │
                      ▼
             Audio Extraction
                      │
                      ▼
              Speech Transcription
                      │
                      ▼
        Transcript + Meeting Notes
                      │
        ┌─────────────┼──────────────┐
        ▼             ▼              ▼
   Summary      Information      Title
               Extraction
        │
        ▼
Vector Embeddings (RAG)
        │
        ▼
 Conversational AI Chat
```

---

# 🛠️ Tech Stack

## Frontend

- Streamlit

## Backend

- Python

## AI/LLM

- LangChain
- Groq LLM
- Retrieval-Augmented Generation (RAG)

## Speech Processing

- Whisper
- FFmpeg

## Vector Search

- FAISS

## Embeddings

- HuggingFace Embeddings

## Libraries

- Python
- Streamlit
- LangChain
- FAISS
- Whisper
- dotenv

---

# 📂 Project Structure

```bash
Retrievia/
│
├── app.py
├── requirements.txt
├── .env
│
├── core/
│   ├── transcriber.py
│   ├── summarizer.py
│   ├── rag_engine.py
│   └── extractor.py
│
├── utils/
│   └── audio_processor.py
│
├── assets/
│
└── README.md
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/shivansh4565/Retrievia

cd Retrievia
```

---

## Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a **.env**

```env
GROQ_API_KEY=your_api_key
```

---

## Run

```bash
streamlit run app.py
```

---

# 💻 How It Works

### Step 1

Paste a YouTube URL or provide a local video path.

↓

### Step 2

Retrievia extracts audio from the video.

↓

### Step 3

Speech is converted into text.

↓

### Step 4

AI generates:

- Summary
- Title
- Action Items
- Key Decisions
- Questions

↓

### Step 5

Transcript is indexed into a Vector Store.

↓

### Step 6

Chat naturally with your video using RAG.

---



# 🎯 Future Improvements

- Multi-language Support
- PDF Export
- Meeting Timeline
- Speaker Identification
- Video Highlights
- Live Meeting Support
- Cloud Storage
- Team Collaboration
- Timestamp-based Search
- Mobile Responsive UI

---

# 📊 Skills Demonstrated

- Retrieval-Augmented Generation (RAG)
- Large Language Models
- Prompt Engineering
- Semantic Search
- Speech Recognition
- Information Extraction
- Streamlit Development
- Vector Databases
- LangChain
- AI Application Development

---

# 👨‍💻 Author

**Shivansh Saxena**

Full Stack Developer • AI/ML Engineer

GitHub: https://github.com/shivansh4565

LinkedIn: https://linkedin.com/in/shivansh-saxena

Portfolio: https://shivanshsaxena.vercel.app

---

# ⭐ Support

If you found this project useful,

⭐ Star this repository

🍴 Fork it

🛠️ Contribute to improve Retrievia

---

<p align="center">
Made with ❤️ by <b>Shivansh Saxena</b>
</p>
