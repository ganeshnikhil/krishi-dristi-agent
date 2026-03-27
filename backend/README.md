## Overview

This project is a **Smart Farming Assistant** designed to help farmers make better decisions by providing insights about **weather, soil, crop yield predictions, fertilizer recommendations**, and more. The system uses **AI models**, **external APIs**, and **local caching** to provide quick, reliable, and offline-capable responses.

Key features:

* **Weather information:** Current and forecasted weather for the farmer’s location.
* **Soil data analysis:** Moisture, temperature, and other soil parameters.
* **Crop yield prediction:** Based on historical and environmental data.
* **Fertilizer recommendation:** Predict optimal fertilizers for different crops.
* **Offline & online support:** Caching and offline AI models for areas with low connectivity.
* **Multilingual support:** Supports multiple languages for farmer accessibility.
* **Meta-search engine:** SearXNG integration for advanced information retrieval.
* **Goverment scheme rag:** Included goverment scheme RAG.
* **Farming practices rag:** Inluded best farming practices RAG
---

## Project Structure

* **app/**: Core application logic.

  * **agents/**: AI agents (online/offline) handling queries and reasoning.
  * **services/**: Interfaces with external APIs (weather, soil, etc.).
  * **tools/**: Reusable tools for crops, fertilizers, soil, and weather.
  * **translation/**: Handles offline and online language conversion.
  * **schemas/**: Request and response models.
  * **data/**: Raw data, cached files, and farmer datasets.
* **Train-Test/**: Datasets and model training scripts for crop yield and fertilizer prediction.
* **notebooks/**: Jupyter notebooks for exploration and testing.
* **main.py**: Entry point of the application.
* **requirements.txt**: Python dependencies.
* **app/searxng-local/**: Docker configuration and YAML for SearXNG meta-search engine.

---

## Required API Keys

Add the following API keys in a `.env` file:

| Variable               | Description                              |
| ---------------------- | ---------------------------------------- |
| `OPENWEATHER_API_KEY`  | OpenWeatherMap API for weather.          |
| `LLM_API_KEY`          | API key for large language models.       |
| `NVIDIA_MODEL_NAME`    | NVIDIA NeMoTTS model for text-to-speech. |
| `GPT_MODEL_NAME`       | GPT reasoning model.                     |
| `SARVAM_MODEL_API`     | Sarvam multilingual model endpoint.      |
| `SARVAM30_MODEL_NAME`  | Sarvam 30B model for offline reasoning.  |
| `SARVAM105_MODEL_NAME` | Sarvam 105B model.                       |
| `SARVAM_M_FREE`        | Sarvam-M free model.                     |
| `AGRO_POLYGON_ID`      | Polygon ID for farm soil data.           |
| `AGRO_MONOTRONIG_API`  | AgroMonitoring soil API key.             |

> These keys are essential for weather, soil, AI reasoning, and multilingual features.

---

## Setup Process

### 1. Clone the Repository

```bash
git clone https://github.com/ganeshnikhil/krishi-dristi-agent.git
cd backend
```

---

### 2. Setup Virtual Environment

A virtual environment isolates your project dependencies:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

### 3. Setup Environment Variables

Create a `.env` file in the project root with all API keys:

```env
OPENWEATHER_API_KEY=your_openweather_key
LLM_API_KEY=your_llm_key
NVIDIA_MODEL_NAME=nvidia/nemotron-3-super-120b-a12b:free
GPT_MODEL_NAME=openai/gpt-oss-120b:free
SARVAM_MODEL_API=https://your-sarvam-api.com
SARVAM30_MODEL_NAME=sarvam-30b
SARVAM105_MODEL_NAME=sarvam-105b
SARVAM_M_FREE=sarvam-m
AGRO_POLYGON_ID=your_polygon_id
AGRO_MONOTRONIG_API=your_agro_api_key
```

---

### 4. Initialize Cache

Weather and other API calls use caching to reduce latency and support offline usage. The cache is stored in:

```text
app/data/weather_cache.sqlite
```

The cache automatically expires after a set time (default 10 minutes) and updates with fresh data from APIs.

---

### 5. Setup SearXNG Meta-Search Engine (Docker)

SearXNG is used to provide meta-search capabilities for farmer queries.

1. Navigate to the SearXNG folder:

```bash
cd app/searxng-local
```

2. Ensure the `docker-compose.yml` and `settings.yml` files are present.
3. Start SearXNG using Docker:

```bash
docker-compose up -d
```

> SearXNG will run locally, and the main app can query it for meta-search results.

4. To stop SearXNG:

```bash
docker-compose down
```

---

### 6. Run the Main Application

Activate the virtual environment (if not already active):

```bash
source venv/bin/activate  # macOS/Linux
```

Then run:

```bash
python main.py
```

The system will:

* Load AI agents.
* Initialize tools for weather, soil, crop, and fertilizer.
* Load cache for offline support.
* Connect to SearXNG for meta-search.

---

## How It Works (Beginner-Friendly)

1. **Farmer input** – Example: “What fertilizer should I use for wheat?”
2. **Agent selection** – Online or offline agent based on internet availability.
3. **Tool usage** – Specialized tools:

   * Weather → Cached or live weather.
   * Soil → Moisture, temperature, and nutrients.
   * Crop/Fertilizer → ML model predictions.
4. **AI reasoning** – Combine data and generate a clear answer.
5. **Multilingual output** – Convert to farmer’s preferred language using Sarvam models.
6. **Audio guidance** – Optional text-to-speech with NVIDIA NeMo models.

---

## Important Notes

* Python 3.12.2 required.
* Ensure `app/data` exists for caching.
* API keys are required for live data and AI predictions.
* The system is **advisory only**; critical farming decisions should also involve local experts.

---

## Benefits

* Quick access to actionable **farming insights**.
* **Offline support** via caching and local AI models.
* **Multilingual support** for accessibility.
* **Integrated meta-search engine** for advanced information retrieval.
