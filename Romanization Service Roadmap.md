# **Project: Universal Romanization Service (OmniRom)**

## **📌 Vision**

To build a highly accurate, low-latency, "any-to-Latin" transliteration API. Instead of relying on a single flawed universal engine, this service acts as an **Orchestrator**, dynamically detecting the input script and routing it to the most accurate, language-specific engine available.

## **🏗️ System Architecture**

1. **Input Normalization Layer:** Cleans Unicode (NFKC), handles emojis, and strips formatting.  
2. **Language/Script Detection Layer:** Uses CLD3 or langid to detect the source text.  
3. **The Router (Switchboard):** Maps the detected language to the best available engine.  
4. **Engine Layer:** Containerized/imported NLP libraries (e.g., uroman, Indic-Xlit, pypinyin).  
5. **Post-Processing Layer:** Applies stylistic formatting (Academic, Chat/Slang, Phonetic).  
6. **Caching Layer:** Redis cache for O(1) lookups on frequently romanized words.

## **🧰 Tech Stack**

* **Backend:** Python (FastAPI) for async performance and native NLP library support.  
* **Caching:** Redis (LRU cache for high-frequency words).  
* **Task Queue:** Celery \+ RabbitMQ/Redis (for batch processing large files).  
* **Containerization:** Docker & Docker Compose (Crucial for managing heavy ML dependencies).  
* **Engines:** ICU, Uroman, AI4Bharat Indic-Xlit, pypinyin, MeCab/Cutlet.

## **🗺️ Development Roadmap**

### **Phase 1: Foundation & MVP (Minimum Viable Product)**

*Goal: Establish the API shell, detection, and a universal fallback.*

* \[ \] Initialize Git repository and Python virtual environment/Poetry.  
* \[ \] Set up FastAPI project structure (app/api, app/engines, app/core).  
* \[ \] Implement pycld3 or langid for script detection.  
* \[ \] Integrate **ICU (International Components for Unicode)** via PyICU for standard rule-based transliteration (Russian, Greek, Arabic).  
* \[ \] Integrate **uroman** as the universal fallback engine for unsupported scripts.  
* \[ \] Build the /v1/romanize POST endpoint.  
* \[ \] Create basic Dockerfile.

### **Phase 2: Integrating the "Specialists"**

*Goal: Drastically improve accuracy for complex language families.*

* \[ \] **Indic Languages:** Integrate AI4Bharat/Indic-Xlit (Hindi, Bengali, Tamil, etc.).  
* \[ \] **Chinese:** Integrate pypinyin to handle tone marks and Mandarin logograms.  
* \[ \] **Japanese:** Integrate MeCab \+ Cutlet to handle Kanji-to-Romaji ambiguity.  
* \[ \] **Korean:** Integrate a dedicated Hangul romanizer (e.g., korean-romanizer).  
* \[ \] Update the Router Logic to seamlessly hand off requests to these new engines based on the detection layer.

### **Phase 3: Performance & Reliability**

*Goal: Make the service production-ready and fast.*

* \[ \] Implement **Redis Caching**: Hash input strings. If hash(text) exists in Redis, return immediately without hitting the ML models.  
* \[ \] Add **Batch Processing Endpoint** (/v1/romanize/batch) to handle arrays of strings efficiently.  
* \[ \] Implement **File Processing Endpoint**: Accept .txt, .csv, or .srt files, process them via background tasks (Celery), and return a download link.  
* \[ \] Write unit tests for the Router and each engine integration (pytest).

### **Phase 4: Advanced Features & "The Secret Sauce"**

*Goal: Differentiate from Google/Azure APIs.*

* \[ \] Add style parameter to API request:  
  * academic: Strict diacritics (e.g., *Namastē*).  
  * chat: Informal, social-media style (e.g., *Namastey*).  
* \[ \] Explore integrating a lightweight local LLM (e.g., Llama 3 8B or Qwen via vLLM) strictly for the chat style post-processing.  
* \[ \] Setup Prometheus & Grafana to track which languages are requested most frequently.

## **📄 API Design Specification (Draft)**

**Endpoint:** POST /api/v1/romanize  
**Request Body:**  
`{`  
  `"text": "こんにちは、世界！",`  
  `"source_lang": "auto",`   
  `"style": "standard"`   
`}`

**Response Body:**  
`{`  
  `"original": "こんにちは、世界！",`  
  `"romanized": "Konnichiwa, sekai!",`  
  `"metadata": {`  
    `"detected_lang": "ja",`  
    `"engine_used": "mecab_cutlet",`  
    `"cached": false,`  
    `"processing_time_ms": 42`  
  `}`  
`}`  
