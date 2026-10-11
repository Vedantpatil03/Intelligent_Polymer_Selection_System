# Intelligent Polymer Material Selection and Recommendation System

### PolyGuide AI — Engineering Decision Support for Polymer Material Selection

A web-based decision-support system that helps users identify and rank suitable polymer materials for engineering applications using **hard-constraint screening and weighted Multi-Criteria Decision-Making (MCDM)**.

PolyGuide AI combines structured polymer property data, requirement-based filtering, transparent scoring, personalized recommendation history, and an AI-powered conversational assistant in one application.

<p align="center">
  <img src="https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React and Vite" />
  <img src="https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Database-MongoDB%20Atlas-47A248?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB Atlas" />
  <img src="https://img.shields.io/badge/Decision%20Engine-Weighted%20MCDM-6C63FF?style=for-the-badge" alt="Weighted MCDM" />
</p>

---

## 🌐 Live Application

**Live Website:** https://polyguideai.vercel.app/

**Backend API:** https://polymer-selection-backend.onrender.com

**API Documentation:** https://polymer-selection-backend.onrender.com/docs

> The deployed application depends on the availability and configuration of the frontend, backend, database, and external AI service. Some backend services may take time to respond after inactivity.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Problem Statement](#-problem-statement)
- [Objectives](#-objectives)
- [Key Features](#-key-features)
- [Application Scenarios](#-application-scenarios)
- [How It Works](#-how-it-works)
- [Weighted MCDM Methodology](#-weighted-mcdm-methodology)
- [Technology Stack](#-technology-stack)
- [System Architecture](#-system-architecture)
- [Dataset Description](#-dataset-description)
- [Project Structure](#-project-structure)
- [Installation and Setup](#-installation-and-setup)
- [Environment Configuration](#-environment-configuration)
- [Running the Application](#-running-the-application)
- [API Endpoints](#-api-endpoints)
- [Authentication and Data Privacy](#-authentication-and-data-privacy)
- [PolyGuide AI Chatbot](#-polyguide-ai-chatbot)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Limitations](#-limitations)
- [Future Enhancements](#-future-enhancements)
- [Contributors](#-contributors)
- [License](#-license)

---

## 🔍 Overview

Selecting an appropriate polymer is an important part of engineering design. Different polymers exhibit different mechanical, thermal, chemical, optical, and processing characteristics.

A polymer suitable for one application may not satisfy the requirements of another. Engineers must therefore evaluate several properties simultaneously while considering mandatory requirements and trade-offs.

The **Intelligent Polymer Material Selection and Recommendation System** addresses this challenge through a structured software-based decision-support approach.

The application allows users to select a predefined engineering scenario or define a custom application. It evaluates polymer candidates against mandatory requirements, scores eligible candidates using weighted MCDM, and presents ranked recommendations with relevant explanations.

The system also supports user accounts, personalized recommendation history, PDF export, and PolyGuide AI for conversational explanations.

The recommendation engine uses deterministic rules and weighted scoring. The chatbot assists with explanations; it does not determine or override the calculated rankings.

## ❗ Problem Statement

Manual polymer selection often requires reviewing multiple material datasheets and comparing numerous properties. This process can be time-consuming and makes it difficult to apply consistent selection criteria across different applications.

A centralized decision-support system is needed to organize polymer information, check mandatory engineering requirements, compare multiple criteria systematically, and produce transparent rankings of eligible materials.

This project addresses the problem through structured data management, hard-constraint screening, and weighted MCDM.

## 🎯 Objectives

- Maintain structured information about polymer materials and their engineering properties.
- Support predefined and custom application requirements.
- Eliminate candidates that fail mandatory constraints.
- Score and rank eligible polymers using weighted MCDM.
- Explain the factors influencing recommendation results.
- Provide an interactive web interface for material selection.
- Implement user authentication and personalized recommendation history.
- Allow users to export their history as PDF.
- Provide a conversational assistant for polymer-related questions.
- Deploy the application using modern web technologies.

---

## ✨ Key Features

### 1. Dashboard

Provides an overview of the available application scenarios, polymer materials, and supported selection properties.

### 2. Material Recommendation

Allows users to choose a predefined engineering application and obtain ranked polymer recommendations.

### 3. Custom Material Selection

Allows users to specify a custom application name, required property values, and hard or soft constraints according to the supported interface.

### 4. Hard-Constraint Screening

Checks mandatory requirements and excludes candidates that fail them before final ranking.

### 5. Weighted MCDM Ranking

Calculates weighted scores for eligible polymers and sorts the results by overall suitability score.

### 6. Recommendation Explanations

Provides relevant information about material suitability, important properties, and selection trade-offs.

### 7. User Authentication

Supports registration, login, and logout for personalized access.

### 8. Personal Recommendation History

Stores recommendation records for individual users, subject to the implemented authentication and authorization rules.

### 9. PDF Export

Allows users to export their recommendation history for documentation and reference.

### 10. PolyGuide AI Chatbot

Provides conversational explanations about polymer properties, application requirements, and existing recommendation results through the Groq API.

---

## 🏭 Application Scenarios

The current project dataset contains seven predefined engineering scenarios.

| ID | Application | Important Selection Criteria |
|---|---|---|
| A001 | Automotive Underhood Bracket | Tensile strength, service temperature, chemical resistance, density, cost |
| A002 | Transparent Safety Shield | Optical transparency, impact strength, temperature capability, density |
| A003 | Consumer Drink Closure | Cost, density, injection-molding suitability, water absorption |
| A004 | High-Temperature Aerospace Connector | Service temperature, heat resistance, tensile modulus, tensile strength |
| A005 | Medical Autoclave Tray | Temperature capability, chemical resistance, heat resistance, water absorption |
| A006 | Precision Actuator Gear | Wear resistance, tensile modulus, tensile strength, service temperature |
| A007 | Air Cooler Water-Distribution Tray | Water absorption, chemical resistance, injection-molding suitability, strength, cost |

These scenarios are intended for preliminary engineering screening. The system does not certify a material for aerospace, medical, automotive, or other regulated applications.

---

## ⚙️ How It Works

The recommendation workflow follows these stages:

1. **Application selection:** The user selects a predefined scenario or enters custom requirements.
2. **Requirement retrieval:** The backend retrieves the relevant requirements and polymer data.
3. **Hard-constraint screening:** Candidates that fail mandatory requirements are excluded.
4. **Criterion scoring:** Each eligible candidate receives scores for the applicable criteria.
5. **Weight application:** Criterion scores are multiplied by their configured normalized weights.
6. **Score aggregation:** Weighted contributions are combined into an overall score.
7. **Ranking:** Eligible candidates are sorted in descending order of score.
8. **Explanation:** The application displays rankings and relevant suitability information.
9. **History storage:** Authenticated users can save and revisit their recommendation records.

---

## 🧮 Weighted MCDM Methodology

Multi-Criteria Decision-Making (MCDM) is used when an alternative must be evaluated against multiple criteria.

In this project, polymer candidates are first screened using mandatory constraints. Eligible candidates are then evaluated through weighted scoring.

The general weighted-score equation is:

\[
S_i = \sum_{j=1}^{n} w_j r_{ij}
\]

Where:

- \(S_i\) is the overall score of candidate polymer \(i\).
- \(w_j\) is the normalized weight of criterion \(j\).
- \(r_{ij}\) is the score of candidate \(i\) on criterion \(j\).
- \(n\) is the number of criteria considered.

When weights are represented as percentages, they are converted to fractions by dividing by 100.

### Hard Constraints

Hard constraints represent mandatory requirements. Candidates that fail a hard constraint are excluded from the eligible set.

### Soft Criteria

Soft criteria influence the overall score and ranking without automatically disqualifying a candidate.

### Direction-Aware Scoring

The scoring system considers whether higher or lower values are preferable for a criterion. Categorical properties also use defined scoring rules.

The final ranking depends on the configured requirements, criterion weights, scoring rules, and available data. A higher score does not guarantee real-world material performance.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React.js, Vite, JavaScript, CSS |
| Backend | Python, FastAPI |
| Data Processing | Pandas, NumPy |
| Recommendation Engine | Weighted MCDM, constraint screening |
| Database | MongoDB Atlas |
| Database Driver | PyMongo |
| Data Validation | Pydantic |
| Authentication | Password hashing and signed tokens/sessions |
| AI Assistant | Groq API |
| API Testing | Postman |
| Development Environment | Visual Studio Code |
| Version Control | Git, GitHub |
| Frontend Hosting | Vercel |
| Backend Hosting | Render |

---

## 🏗️ System Architecture

```text
                 ┌──────────────────────────┐
                 │          User            │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │ React + Vite Frontend    │
                 │ Dashboard / Selection    │
                 │ History / Chatbot        │
                 └────────────┬─────────────┘
                              │ HTTPS / REST API
                              ▼
                 ┌──────────────────────────┐
                 │ FastAPI Backend          │
                 │ Authentication / APIs    │
                 └────────────┬─────────────┘
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
       ┌────────────────┐ ┌────────────┐ ┌─────────────┐
       │ MongoDB Atlas  │ │ Python     │ │ Groq API    │
       │ Users / Data / │ │ MCDM Engine │ │ Explanatory │
       │ History        │ │            │ │ Chatbot     │
       └────────────────┘ └─────┬──────┘ └─────────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │ Ranked Recommendations │
                     │ Scores and Explanations │
                     └─────────────────────┘
```

The MCDM engine determines the rankings. Groq provides the conversational assistant and does not replace the deterministic recommendation process.

---

## 📂 Dataset Description

The project uses four CSV datasets.

| File | Description | Current Size |
|---|---|---:|
| `final_polymers.csv` | Polymer identities and descriptive information | 20 records |
| `final_polymer_properties.csv` | Polymer engineering properties | 20 records, 23 columns |
| `final_property_sources.csv` | Supporting property-source records | 139 records |
| `final_application_requirements.csv` | Requirements for predefined scenarios | 36 rows across 7 scenarios |

### Supported Property Categories

The system supports 14 selectable properties, including:

- Tensile strength
- Tensile modulus
- Impact strength
- Maximum service temperature
- Heat resistance
- Chemical resistance
- Density
- Water absorption
- Wear resistance
- Injection-molding suitability
- Optical transparency
- Melting or softening temperature
- Cost category
- Other supported properties defined by the dataset and implementation

The exact property names and units are determined by the project's CSV files.

**Data-quality note:** Missing values must remain missing rather than being automatically interpreted as zero. Property values and source URLs should be independently verified before being used for critical engineering decisions.

---

## 📁 Project Structure

The repository is organized approximately as follows:

```text
Intelligent_Polymer_Selection_System/
│
├── backend/
│   ├── api/
│   │   ├── main.py
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   └── auth.py
│   │
│   ├── database/
│   │   ├── connection.py
│   │   └── collections.py
│   │
│   ├── recommendation/
│   │   ├── constraints.py
│   │   ├── explanation.py
│   │   ├── loader.py
│   │   ├── mcdm.py
│   │   ├── mongo_loader.py
│   │   ├── recommender.py
│   │   └── scoring.py
│   │
│   ├── requirements.txt
│   ├── validate_data.py
│   └── .env.example
│
├── data/
│   ├── final_polymers.csv
│   ├── final_polymer_properties.csv
│   ├── final_property_sources.csv
│   └── final_application_requirements.csv
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── .env.example
│
├── .gitignore
└── README.md
```

> The structure is illustrative. Use the actual repository files as the source of truth, because implementation details may evolve.

---

## 🚀 Installation and Setup

### Prerequisites

Install the following:

- Python 3.13 or a compatible version supported by the backend dependencies.
- Node.js and npm.
- Git.
- A MongoDB Atlas account and database.
- A Groq API key if chatbot functionality is required.

### 1. Clone the Repository

```bash
git clone https://github.com/Vedantpatil03/Intelligent_Polymer_Selection_System
cd Intelligent_Polymer_Selection_System
```


### 2. Configure the Backend

```bash
cd backend
python -m venv venv
```

Activate the virtual environment.

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

```cmd
venv\Scripts\activate.bat
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

### 3. Configure Backend Environment Variables

Create `backend/.env` using `backend/.env.example` as a reference.

Set the actual MongoDB connection string, database name, authentication secrets, and Groq configuration required by your implementation.

### 4. Configure the Frontend

Open a separate terminal:

```bash
cd frontend
npm install
```

Create `frontend/.env` using `frontend/.env.example` as a reference.

For local development, the frontend API URL is typically:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Use the exact variable names defined by the project.

---

## ▶️ Running the Application

### Start the Backend

From the `backend` directory with the virtual environment activated:

```bash
python -m uvicorn api.main:app --reload
```

The backend should be available at:

http://127.0.0.1:8000

Interactive API documentation:

http://127.0.0.1:8000/docs

### Start the Frontend

From the `frontend` directory:

```bash
npm run dev
```

Open the local URL displayed by Vite, typically:

http://localhost:5173

Keep both the backend and frontend terminals running during local development.

---

## 🔌 API Endpoints

The backend provides REST endpoints for application data, polymer data, recommendations, authentication, and history.

The following are representative endpoint names. Verify the actual registered routes in FastAPI's `/docs` page.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Backend status |
| GET | `/health` | Health check |
| GET | `/applications` | Retrieve application scenarios |
| GET | `/polymers` | Retrieve polymer data |
| GET | `/properties` | Retrieve supported properties |
| POST | `/auth/register` | Register a user |
| POST | `/auth/login` | Authenticate a user |
| GET | `/auth/me` | Retrieve the current user |
| POST | `/auth/logout` | End the user session |
| GET | `/history` | Retrieve the current user's history |
| DELETE | `/history` | Clear the current user's history, if implemented |

Recommendation, custom-selection, individual-history, and chatbot routes depend on the actual backend implementation.

---

## 🔐 Authentication and Data Privacy

The application supports user authentication and personal recommendation history.

The backend should verify the authenticated identity and restrict history operations to records owned by that user. Client-provided user IDs must not be treated as proof of ownership.

Important security practices:

- Store password hashes rather than plaintext passwords.
- Keep JWT signing secrets, MongoDB credentials, and Groq API keys on the backend.
- Never commit `.env` files or private credentials to GitHub.
- Protect private API endpoints.
- Validate access to history records on every relevant request.
- Clear sensitive client-side state during logout and account switching.

Cross-user isolation should be tested before the application is considered production-ready.

---

## 🤖 PolyGuide AI Chatbot

PolyGuide AI is the conversational assistant integrated into the application through the Groq API.

Its intended responsibilities include:

- Explaining polymer families and material properties.
- Clarifying application requirements.
- Explaining why a ranked material may be suitable.
- Comparing available recommendation results.
- Answering questions using the available project context.

**The chatbot is not the decision-making engine.** Polymer eligibility and ranking are determined by the backend's hard-constraint screening and weighted MCDM calculations.

The chatbot must not invent missing material values, change recommendation scores, or claim that a polymer is certified for a regulated application.

---

## 🧪 Testing

Testing should cover the following areas.

### Dataset Validation

- Validate CSV structure and required columns.
- Check missing and invalid property values.
- Confirm application requirements use consistent units.
- Validate weights and scoring inputs.

### Recommendation Testing

- Confirm that hard constraints eliminate ineligible candidates.
- Confirm that eligible candidates receive scores.
- Verify ranking order and score calculations.
- Check that explanations agree with the calculated results.

### Authentication Testing

- Test registration and login.
- Test invalid credentials and expired sessions.
- Test logout and protected endpoints.

### History Isolation Testing

- Create a recommendation using Account A.
- Sign in using Account B.
- Verify that Account B cannot view or delete Account A's records.
- Sign back into Account A and verify its history persists.

### Deployment Testing

- Verify frontend-to-backend communication.
- Verify database connectivity.
- Test recommendations, custom selection, PDF export, and chatbot functionality on the live deployment.

Report actual observed results rather than inventing accuracy or performance measurements.

---

## ☁️ Deployment

### Frontend — Vercel

The frontend is deployed on Vercel.

Live application:

https://polyguideai.vercel.app/

Configure the production environment variable:

```env
VITE_API_BASE_URL=https://polymer-selection-backend.onrender.com
```

Vite environment variables prefixed with `VITE_` are exposed to the browser. Never put secrets in them.

### Backend — Render

The backend is deployed on Render.

Backend URL:

https://polymer-selection-backend.onrender.com

Configure the required backend environment variables, including:

- `MONGODB_URI`
- `MONGODB_DATABASE`
- `GROQ_API_KEY`
- The authentication signing secret expected by the code
- `FRONTEND_URL`
- Any other configuration required by the application

Do not publish actual secret values.

### Database — MongoDB Atlas

MongoDB Atlas provides persistent database storage for polymer data, application requirements, user accounts, and recommendation history, according to the implemented collection design.

Ensure network access, database permissions, and credentials are configured securely.

---

## ⚠️ Limitations

- Recommendations depend on the completeness and quality of the available property data.
- Missing values and differences between test methods can affect comparisons.
- Polymer grades, additives, processing conditions, and operating environments can influence real-world performance.
- Rankings depend on the configured criteria, weights, and scoring rules.
- A high score does not guarantee material performance or regulatory compliance.
- The chatbot may produce imperfect explanations and should not override the calculated ranking.
- The current dataset contains 20 polymer records and seven predefined application scenarios.

The application is intended for preliminary decision support and should be complemented by verified datasheets, engineering analysis, and appropriate testing.

---

## 🔮 Future Enhancements

- Expand the database with independently verified polymer property data.
- Add manufacturer-specific polymer grades.
- Introduce sensitivity analysis for criterion weights.
- Compare additional MCDM methods.
- Improve property-source traceability.
- Add richer charts and material-comparison reports.
- Introduce administrator tools for data maintenance.
- Evaluate recommendation quality using expert-reviewed case studies.

---


## 🙌 Acknowledgements

We acknowledge the documentation and tools provided by the developers of Python, React, FastAPI, MongoDB, Vite, and Groq, which support the implementation of this software-based engineering decision-support project.

**PolyGuide AI — Making Polymer Material Selection More Structured, Transparent, and Accessible.**
