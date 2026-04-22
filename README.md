# -AI-SaaS-Product-Assistant
AI-powered SaaS product assistant built with FastAPI, ChromaDB, and RAG. It enables semantic product search, chatbot-based recommendations, and lead capture through an interactive web UI.

This project is a lightweight AI-powered SaaS product assistant built using FastAPI, ChromaDB, and sentence-transformer embeddings. It provides a chat-based interface for exploring SaaS products through natural language queries.

The system is designed as a simplified retrieval-augmented generation (RAG) pipeline, focusing on semantic product search, intent detection, and structured responses.


## Project Overview

The goal of this project is to simulate how a SaaS product discovery assistant would work in a real-world application.

Instead of relying on keyword search, the system uses vector embeddings to understand user intent and match relevant products based on meaning rather than exact text.

Users can:
- Search for SaaS tools in natural language
- Compare different product categories
- View structured product details
- Trigger a simulated purchase flow
- Submit email as a lead for follow-up

## System Architecture

The system follows a simple RAG-inspired pipeline:

User Query  
→ Intent Detection (rule-based classification)  
→ Embedding Generation (SentenceTransformer model)  
→ Vector Similarity Search (ChromaDB)  
→ Top-K Product Retrieval  
→ Response Formatting (summary or detailed view)  
→ Frontend Chat Interface  

## Core Features

- Semantic search over SaaS product catalog  
- Vector-based product retrieval using ChromaDB  
- Lightweight intent detection system  
- Structured product summaries and full-detail responses  
- Category-based filtering  
- Simulated purchase flow with email capture  
- Simple chat UI for interaction  

## How to Run the Project

### 1. Install dependencies

```bash
pip install -r requirements.txt


##Start the backend server
uvicorn main:app --reload


##Open the frontend
http://127.0.0.1:8000

##Limitations

This project is not production-ready and has some limitations:

No real LLM integration (uses rule-based intent handling)
No user authentication system
No persistent database (uses JSON and local ChromaDB storage)
No long-term memory in conversations
Basic frontend UI without advanced UX features

###Purpose of This Project

This project was built to understand and demonstrate:

How retrieval-augmented systems work in practice
How vector databases are used for semantic search
How simple AI agents can be structured without LLMs
How FastAPI can serve as a lightweight AI backend

It is intentionally kept simple but structured in a way that can scale into a full SaaS product.
