# 🏠 AI Real Estate Intelligence Platform

> An end-to-end real estate intelligence platform that combines **Python/FastAPI backend development, machine learning, RAG, and LLM-powered property assistance**.

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

## 📌 Overview

This project provides a complete workflow for real estate discovery and intelligence. Users can browse and filter property listings, receive machine-learning-based price predictions with explainability, and interact with an AI assistant that retrieves relevant property information before generating responses.

The project demonstrates practical experience with **REST API development, authentication, relational databases, ML inference, explainable ML, semantic retrieval, and RAG-based AI workflows**.

## ✨ Key Features

- 🔐 **Authentication & Authorization** — Registration, login, JWT authentication, and Admin/User roles
- 🏘️ **Property Management** — Search, filtering, sorting, pagination, and image uploads
- 📈 **Price Prediction** — Machine-learning-based property price prediction with SHAP explainability
- 💬 **RAG AI Assistant** — Retrieves relevant property information from ChromaDB before generating responses with Gemini
- 📊 **Analytics Dashboard** — Property and prediction analytics with interactive visualizations
- 🔌 **REST APIs** — Backend APIs documented through FastAPI Swagger/OpenAPI
- 🧪 **Automated Testing** — Backend tests using pytest
- 🐳 **Containerized Development** — Docker-based local setup

## 🏗️ Architecture

```text
                    ┌──────────────────────┐
                    │     Web Frontend     │
                    │   React + Vite       │
                    └──────────┬───────────┘
                               │ REST API
                               ▼
                    ┌──────────────────────┐
                    │    FastAPI Backend   │
                    │ Authentication       │
                    │ Business Logic       │
                    │ REST Endpoints       │
                    └──────┬─────────┬─────┘
                           │         │
                 ┌─────────▼───┐ ┌──▼──────────────┐
                 │    MySQL    │ │ ML / RAG Layer  │
                 │ SQLAlchemy  │ │                 │
                 └─────────────┘ │ ML + SHAP        │
                                 │ ChromaDB + Gemini │
                                 └───────────────────┘
```

## 🛠️ Tech Stack

| Area | Technologies |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy, Pydantic |
| API | REST, Swagger/OpenAPI |
| Authentication | JWT, bcrypt, Role-Based Access Control |
| Database | MySQL |
| Machine Learning | XGBoost, Scikit-learn, Joblib, SHAP |
| AI / RAG | ChromaDB, Gemini API |
| Frontend | React, Vite, Tailwind CSS, Axios, React Router, Recharts |
| Testing | pytest |
| DevOps | Docker |

## 🔄 Core Workflows

### 1. Property Price Prediction

```text
Property Details
      ↓
FastAPI Prediction Endpoint
      ↓
Trained ML Model
      ↓
Predicted Property Price
      ↓
SHAP Explanation
```

### 2. RAG Property Assistant

```text
User Question
      ↓
FastAPI Chat Endpoint
      ↓
Query / Retrieval
      ↓
ChromaDB Property Context
      ↓
Gemini LLM
      ↓
Grounded Response
```

## 🔑 Main API Modules

| Module | Example Endpoints |
|---|---|
| Authentication | `POST /api/auth/register` · `POST /api/auth/login` · `GET /api/auth/me` |
| Properties | `GET/POST/PUT/DELETE /api/properties` |
| Property Images | `POST /api/properties/{id}/images` |
| Predictions | `POST /api/predictions` · `GET /api/predictions/history` |
| AI Chat | `POST /api/chat/sessions` · `POST /api/chat/sessions/{id}/message` |
| Dashboard | `GET /api/dashboard/summary` · `GET /api/dashboard/charts` |

Full interactive API documentation is available through FastAPI Swagger at `/docs` when the backend is running.

## 🚀 Getting Started

### 1. Configure Environment

```bash
cp .env.example .env
```

Update `.env` with the required database credentials, Gemini API key, JWT settings, and other application configuration.

### 2. Run with Docker

```bash
docker-compose up --build
```

Typical local endpoints:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

### 3. Run Backend Locally

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
python -m app.ml.train
python -m app.seed
uvicorn app.main:app --reload --port 8000
```

### 4. Run Frontend Locally

```bash
cd frontend
npm install
npm run dev
```

## 🧪 Testing

Run the backend test suite with:

```bash
cd backend
pytest -v
```

## 📁 Project Structure

```text
RealEstate-AI-Platform/
├── backend/
│   ├── app/
│   │   ├── api/          # REST route handlers
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic, ML and RAG services
│   │   └── ml/           # ML training pipeline
│   └── tests/            # Backend tests
│
├── frontend/             # React application
│   └── src/
│       ├── pages/
│       ├── components/
│       └── context/
│
├── docker-compose.yml
└── .env.example
```

## 🎯 What This Project Demonstrates

- Building backend services with **FastAPI**
- Designing and consuming **REST APIs**
- Implementing **JWT authentication and RBAC**
- Working with **SQLAlchemy and MySQL**
- Serving **machine learning predictions through APIs**
- Applying **SHAP for model explainability**
- Building a **retrieval-augmented generation workflow**
- Integrating an **LLM API** into an application
- Writing backend tests with **pytest**
- Running the application with **Docker**

## 📌 Project Status

This project is being developed as a hands-on portfolio project focused on combining backend engineering, data science, and AI-powered application workflows.

## 📄 License

MIT
