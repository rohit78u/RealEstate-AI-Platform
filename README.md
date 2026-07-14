# AI Real Estate Intelligence Platform

A production-ready web application for browsing properties, predicting house prices with Machine Learning (XGBoost + SHAP), and interacting with an AI real estate assistant powered by RAG (ChromaDB + Gemini).

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | React (Vite), Tailwind CSS, Axios, React Router, Recharts |
| Backend | FastAPI, SQLAlchemy, MySQL, Pydantic, JWT, bcrypt |
| ML | XGBoost, Scikit-learn, Joblib, SHAP |
| AI | ChromaDB, Gemini API |

## Features

- **Authentication** — Register, login, JWT, role-based access (Admin/User)
- **Property Management** — Search, filter, sort, pagination, image upload
- **Price Prediction** — XGBoost model with SHAP explainability
- **AI Chatbot** — RAG-powered assistant grounded in property listings
- **Dashboard** — Analytics with interactive charts
- **REST APIs** — Fully documented via Swagger at `/docs`

## Quick Start

### 1. Environment Setup

```bash
cp .env.example .env
# Edit .env with your GEMINI_API_KEY and secrets
```

### 2. Docker (Recommended)

```bash
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs

### 3. Local Development

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Train ML model
python -m app.ml.train

# Seed sample data
python -m app.seed

# Start server
uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

Frontend dev server: http://localhost:5173

## Default Admin Account

| Field | Value |
|-------|-------|
| Email | `admin@realestate.com` |
| Password | `admin123` |

## API Endpoints

| Module | Endpoints |
|--------|-----------|
| Auth | `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me` |
| Properties | `GET/POST/PUT/DELETE /api/properties`, `POST /api/properties/{id}/images` |
| Predictions | `POST /api/predictions`, `GET /api/predictions/history` |
| Chat | `POST /api/chat/sessions`, `POST /api/chat/sessions/{id}/message` |
| Dashboard | `GET /api/dashboard/summary`, `GET /api/dashboard/charts` |

## Testing

```bash
cd backend
pytest -v
```

## Project Structure

```
├── backend/          # FastAPI application
│   ├── app/
│   │   ├── api/      # REST route handlers
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # Business logic, ML, RAG
│   │   └── ml/       # Training pipeline
│   └── tests/
├── frontend/         # React application
│   └── src/
│       ├── pages/
│       ├── components/
│       └── context/
├── docker-compose.yml
└── .env.example
```

## License

MIT
