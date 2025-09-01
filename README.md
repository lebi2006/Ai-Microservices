# **AI Microservices (LangChain + Ollama)**



This project implements three AI-powered microservices using **FastAPI**, **LangChain,** and a local **Ollama (Mistral) model**.

It also includes a **frontend dashboard**, a **sample document for testing**, and a **Postman collection for API validation**.





#### **1. REST API (FastAPI)**

\- The backend is built with **FastAPI** (`app/main.py`) and exposes the following endpoints:

  - **Summarization** → `/summarize`

  - **Document Q\&A** → `/qa`

  - **Learning Path Generator** → `/learning-path`

  - **Health Check** → `/health`



Run the backend with:



uvicorn app.main:app --reload



#### **2. Postman Collection**



A ready-to-use Postman collection is provided:

AI Microservices.postman\_collection.json (saved in project root).



Import this file in Postman to test all endpoints directly.



Example:



For Q\&A, select method POST /qa



Add query as text field



Attach sample\_document.txt as a file



#### **3. Frontend (HTML/JS/CSS)**



The project includes a minimal frontend under /frontend:



index.html → Web UI



script.js → API calls



style.css → Styling



Run the backend and open in browser:



http://127.0.0.1:8000/

#### **4. Sample Input File**



A sample document is included:

sample\_document.txt

This can be uploaded in Postman or via the frontend Q\&A module.



#### **5. README Documentation**



This README explains:



Project setup



API endpoints



Postman usage



Frontend usage



Where to find deliverables



##### **Project Structure**

ai-microservices/

│

├── app/                          # FastAPI microservices

│   ├── main.py                   # Entry point

│   ├── summarizer.py             # Summarization service

│   ├── qa\_service.py             # Document Q\&A service

│   ├── learning\_path.py          # Dynamic learning path service

│   └── \_\_init\_\_.py

│

├── frontend/                     # Web-based frontend

│   ├── index.html

│   ├── script.js

│   └── style.css

│

├── venv/                         # Virtual environment (ignored in submission)

│

├── sample\_document.txt            # Test file for Q\&A

├── AI Microservices.postman\_collection.json  # Postman collection

├── requirements.txt               # Dependencies

└── README.md                      # This file



API Endpoints

Health Check



GET /health

Response:

{ "status": "ok" }





###### **Summarization**



POST /summarize

Request (JSON):

{

  "text": "LangChain is a framework for building LLM-powered apps...",

  "length": "short"

}



Response:
{

  "summary": "LangChain is a framework for creating LLM applications, enabling chaining of models, tools, and memory."

}



###### **Q\&A**



POST /qa



Request (form-data):



query: What is LangChain?



file: sample\_document.txt



Response:
{

  "answer": "LangChain is a framework for building LLM-powered applications.",

  "reasoning": "The document describes LangChain as a toolkit that connects models, data, and tools for practical AI workflows."

}



###### **Learning Path**



POST /learning-path



Request (JSON):
{

  "goal": "data science",

  "background": "Python basics",

  "duration\_weeks": 6,

  "hours\_per\_week": 8

}



Response(truncated):
{

  "weeks": \[

    {

      "week": 1,

      "topics": \["Python basics review", "NumPy"],

      "resources": \[{"title": "NumPy Documentation", "type": "article", "link": "https://numpy.org/doc/stable/"}],

      "practicals": \["Hands-on with arrays"]

    }

  ],

  "raw\_text": "... original LLM response ..."

}



#### **Setup Instructions**



Clone the project:

git clone https://github.com/lebi2006/Ai-Microservices.git

cd ai-microservices



Create virtual environment:

python -m venv venv

venv\\Scripts\\activate   # on Windows



Install dependencies:
pip install -r requirements.txt



Run the backend:

uvicorn app.main:app --reload



Access:
API docs: http://127.0.0.1:8000/docs

Frontend: http://127.0.0.1:8000/


###### **Author:**
###### **Lebi Maria C.**

###### **AI Microservices with LangChain + Ollama**

###### **Date: Aug 2025**






