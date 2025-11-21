## 🚀 How to Run (Setup in 2 minutes)

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/banking-ai-orchestrator.git
cd banking-ai-orchestrator
```
### 2. Create virtual environment & install dependencies
```bash
python -m venv venv
source venv/bin/activate          # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
### 3. Get your Gemini API Key
→ https://aistudio.google.com/app/apikey
Create a new key → copy it
### 4. Create .env file (never commit this!)
```env
GEMINI_API_KEY=your_actual_api_key_here
```
### 5. Run the system
Terminal 1 – Backend (FastAPI)
```bash
uvicorn main:app --reload
```
Terminal 2 – Frontend (Streamlit)
```bash
streamlit run app.py
```
→ Open your browser: http://localhost:8501
Done! You now have the full Banking AI Orchestrator running locally.