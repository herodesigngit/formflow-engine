# 🚀 FormFlow Engine

An enterprise-grade, lightweight Python microservice built on **FastAPI** and **PyPDF** designed for high-volume JSON-to-PDF form filling and automated PDF field flattening.

---

## 📌 Executive Summary

**FormFlow Engine** decouples PDF template rendering from core application logic. It accepts structured JSON payloads via REST API endpoints, dynamically populates fillable PDF forms (AcroForms), flattens field layers to enforce read-only integrity, and streams the completed document directly to the caller.

Designed with **stateless resource management**, generated files are automatically purged post-download via async background workers to maintain a zero-disk footprint.

---

## ✨ Architectural Highlights

* **High-Throughput Processing:** Powered by FastAPI's asynchronous architecture.
* **AcroForm Ingestion & Flattening:** Dynamic field-mapping with enforced `flags=1` bitwise operations for field locking.
* **Ephemeral Storage Architecture:** Non-blocking `BackgroundTasks` execute file cleanup immediately after document streaming completes.
* **Production-Grade Containerization:** Multi-stage Docker build producing an optimized slim runtime container (~150MB footprint).
* **Strict Type Safety:** Fully validated input interfaces using Pydantic v2 data models.

---

## 📂 Project Architecture

```text
formflow-engine/
├── src/
│   ├── __init__.py           # Package exports and interface definitions
│   ├── main.py               # FastAPI router, payload validation, background workers
│   ├── pdf_processor.py      # Core AcroForm mapping & PDF flattening engine
│   └── exceptions.py         # Custom application exception hierarchy
├── templates/                # Store static fillable PDF templates (.pdf)
├── storage/
│   └── output/               # Temporary runtime storage for output PDFs
├── Dockerfile                # Multi-stage production container build
└── requirements.txt          # Frozen application dependencies
```

---

## 🛠️ Tech Stack & Dependencies

* **Framework:** FastAPI (`0.111.0`)
* **ASGI Server:** Uvicorn (`0.30.1`)
* **PDF Engine:** PyPDF (`4.2.0`)
* **Data Validation:** Pydantic (`2.7.2`)
* **Runtime:** Python 3.11 Slim

---

## 🚀 Getting Started

### Local Development Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-org/formflow-engine.git
   cd formflow-engine
   ```

2. **Set Up Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Service:**
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```
   * **API Docs (Swagger UI):** `http://localhost:8000/docs`
   * **ReDoc Interface:** `http://localhost:8000/redoc`

---

## 🐳 Docker Deployment

The application features a 2-stage `Dockerfile` optimized for reduced attack surface and minimal image size.

```bash
# Build production image
docker build -t formflow-engine:1.0.0 .

# Run containerized service
docker run -d \
  -p 8000:8000 \
  --name formflow-service \
  --restart unless-stopped \
  formflow-engine:1.0.0
```

---

## 📡 API Reference

### Generate Flattened PDF

Fills a designated server-side template with target key-value pairs and streams back the finalized PDF file.

* **Endpoint:** `POST /api/v1/generate-pdf`
* **Content-Type:** `application/json`

#### Request Body Schema

```json
{
  "template_name": "W4_Form_Template.pdf",
  "payload": {
    "First Name": "John",
    "Last Name": "Doe",
    "Address": "123 Technology Park",
    "City": "Tech City"
  }
}
```

#### cURL Example

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/generate-pdf' \
  -H 'accept: application/pdf' \
  -H 'Content-Type: application/json' \
  -d '{
  "template_name": "W4_Form_Template.pdf",
  "payload": {
    "First Name": "John",
    "Last Name": "Doe"
  }
}' \
  --output completed_form.pdf
```

#### Response Specs

* **200 OK:** Binary stream of `application/pdf`.
* **404 Not Found:** Template does not exist in `templates/`.
* **422 Unprocessable Entity:** Payload schema mismatch or invalid JSON.
* **500 Internal Server Error:** Failures during PDF parsing or mapping.

---

## 🔒 Resource & Security Design

1. **Storage Cleanup Strategy:**
   To avoid disk space leaks during continuous usage, every request registers a post-response asynchronous task (`clean_up_file`) that purges generated output artifacts immediately after the network socket flushes.

2. **Container Security:**
   * Non-root user privileges inside the multi-stage final image.
   * Minimal base image (`python:3.11-slim`) to eliminate OS-level security vulnerabilities.
