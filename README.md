# TEJAS: AI-Powered Fake News & Fraud Detection Application

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68%2B-green)
![React](https://img.shields.io/badge/React-18.0%2B-blue)
![Docker](https://img.shields.io/badge/Docker-20.10%2B-blue)

**TEJAS** is an advanced, evidence-based misinformation verification system designed to analyze text and image claims, retrieve real-world supporting evidence from the web, apply semantic reasoning, and return a final verdict with a clear, AI-generated explanation.

This system combines transformer-based machine learning models, web evidence retrieval, and deterministic reasoning logic to ensure reliable and explainable fact-checking. It is fully containerized and includes a one-click deployment script for easy setup.

---

## 🚀 Key Features

### 1. Multi-Modal Fact Verification
*   **Text Analysis**: Accepts user-submitted text claims and verifies them against trusted web sources.
*   **OCR Support**: Extracts text from images using Tesseract OCR to fact-check screenshots or memes.

### 2. Evidence-Based Reasoning Engine
*   **Semantic Search**: Retrieves related evidence from multiple trusted web sources.
*   **Contradiction Detection**: Uses Natural Language Inference (NLI) to detect contradictions between claims and evidence.
*   **Source Authority**: Ranks evidence based on source credibility and relevance.

### 3. AI-Generated Explanations
*   **Human-Readable Insights**: An AI agent synthesizes the evidence into a clear, natural language explanation of *why* a claim is True, False, or Unverified.
*   **Transparent Verdicts**: Provides definitive verdicts (TRUE, FALSE, INSUFFICIENT) backed by cited sources.

### 4. Robust Architecture
*   **Orchestration**: integrated **n8n** workflows for complex pipeline management.
*   **Containerized**: Fully Dockerized backend, frontend, and orchestration layers.
*   **Public Access**: Built-in **ngrok** integration for secure, public-facing demos without complex network configuration.

---

## 🛠️ Technology Stack

*   **Backend**: Python, FastAPI, Uvicorn, Tesseract OCR
*   **Frontend**: React, Nginx
*   **ML/AI**: PyTorch, Transformers (Hugging Face), NLI Models
*   **Automation**: n8n
*   **Infrastructure**: Docker, Docker Compose, Ngrok

---

## 📋 Prerequisites

Before running the application, ensure you have the following installed:

*   **[Docker Desktop](https://www.docker.com/products/docker-desktop)** (running and configured)
*   **[Ngrok](https://ngrok.com/)** account and authtoken

---

## ⚡ Quick Start (Windows)

The application comes with a one-click batch script for Windows environments.

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/tejas-fake-news-detection.git
    cd tejas-fake-news-detection
    ```

2.  **Configure Ngrok**
    *   Open `ngrok.yml` in the root directory.
    *   Replace the placeholder with your actual Ngrok authtoken.
    ```yaml
    authtoken: YOUR_NGROK_AUTHTOKEN_HERE
    ```

3.  **Run the System**
    *   Double-click `run_everything.bat` OR run it from the command line:
    ```bash
    run_everything.bat
    ```
    *   This script will:
        *   Start Docker containers (Backend, Frontend, n8n).
        *   Initialize the Ngrok tunnel.
        *   Display the public URL to access the application.

---

## 🐳 Manual Setup (Docker Compose)

If you prefer to run the containers manually or are on a non-Windows system:

1.  **Build and Start Containers**
    ```bash
    docker-compose up --build -d
    ```

2.  **Access the Application**
    *   **Frontend**: http://localhost:8080
    *   **Backend API**: http://localhost:8000
    *   **n8n Workflow**: http://localhost:5678 (or via the configured ngrok tunnel)
    *   **API Documentation**: http://localhost:8000/docs (Swagger UI)

---

## 🔌 API Endpoints

The backend exposes a REST API built with FastAPI.

*   `POST /factcheck`: Verifies a text claim.
    *   **Body**: `{"text": "Claim to verify"}`
*   `POST /extract-text`: Extracts text from an uploaded image (OCR).
    *   **Body**: Image file (multipart/form-data)
*   `GET /`: Health check.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
