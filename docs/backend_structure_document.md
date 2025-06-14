# Backend Structure Document

## 1. Backend Architecture

Overview
- We use a service-oriented design, where each major capability runs as its own component:
  - **Sync Service**: Keeps files in sync between NAS, cloud storage, and server.
  - **Ingestion & Preprocessing Service**: Detects file types, extracts text, splits into chunks.
  - **Embedding Service**: Calls OpenAI Embeddings API to turn chunks into vectors.
  - **Vector Store & Retrieval API**: Stores vectors in Qdrant and exposes REST endpoints for search, Q&A, and summarization.
  - **User Interaction Layer**: Includes the REST API (FastAPI), the Telegram Bot (Node.js/Python), and integration plugin.
  - **Web Dashboard API**: Serves configuration and monitoring info to the React/Next.js frontend.

Design Patterns & Frameworks
- **FastAPI**: High-performance Python framework powering the main REST API.
- **Async Tasks**: Background jobs for ingestion and embedding (via FastAPI’s BackgroundTasks or a task queue like Celery).
- **Docker & Docker Compose**: Each service containerized for consistency and easy deployment.

Scalability
- Horizontal scaling of stateless services (API, ingestion) by spinning up additional containers.
- Qdrant can be clustered for larger vector volumes.
- Future-proofed to move to Kubernetes if demand grows.

Maintainability
- Clear separation of concerns (sync, ingestion, embedding, retrieval).
- Modular codebases with unit tests for each service.
- Docker ensures consistent environments across developers and production.

Performance
- Asynchronous I/O for file extraction and API calls.
- Batch embedding generation to reduce OpenAI API overhead.
- Caching of recent queries and embeddings in memory or via Redis (optional).

---

## 2. Database Management

Primary Datastore: Qdrant (NoSQL Vector Database)
- Stores document embeddings alongside metadata for semantic search.
- Supports real-time nearest-neighbor queries on high-dimensional vectors.

Metadata Storage
- Basic metadata (file name, path, source, upload timestamp) lives in Qdrant’s payload fields.

Data Flow
1. Ingestion service extracts text and splits into chunks.
2. Embedding service generates vectors via the OpenAI Embeddings API.
3. Vectors and metadata are upserted into the Qdrant collection.
4. Retrieval API queries Qdrant and returns matching documents or chunks.

Data Management Practices
- **Incremental Updates**: Nightly jobs add new or changed files.
- **On-Demand Reindexing**: Manual trigger to reprocess specific files.
- **Backups**: Snapshots of Qdrant data stored on Synology NAS.

---

## 3. Database Schema

Collection Name: **documents**

Human-Readable Schema:
- **id**: Unique identifier for each text chunk.
- **embedding**: 1536-dimensional vector (float32 array) from OpenAI.
- **file_name**: Original file name (e.g., “report.pdf”).
- **file_path**: Absolute or relative path on server/NAS/Yandex/Google.
- **source**: One of [“NAS”, “YandexDisk”, “GoogleDrive”].
- **chunk_index**: Integer order of chunk in the document.
- **text_snippet**: Plain text content of the chunk.
- **timestamp**: DateTime when chunk was ingested or updated.

Since this is a NoSQL vector store, we don’t write SQL. The Qdrant collection holds vectors plus these payload fields.

---

## 4. API Design and Endpoints

Approach: **RESTful API** built with FastAPI

Authentication: JWT or API keys over HTTPS

Key Endpoints:

1. **/api/v1/documents/upload**  
   - Purpose: Trigger ingestion of new files or force reindex.  
   - Method: POST  
   - Payload: File metadata and optional file upload.  

2. **/api/v1/search**  
   - Purpose: Perform semantic search over documents.  
   - Method: POST  
   - Payload: { query: string, top_k: integer }  
   - Response: List of matching chunks with metadata and similarity scores.

3. **/api/v1/qa**  
   - Purpose: Ask a question and get answer from documents.  
   - Method: POST  
   - Payload: { question: string, context_ids: [id,…] }  
   - Response: Generated answer using GPT-3.5/Claude/Gemini.

4. **/api/v1/summarize**  
   - Purpose: Summarize a document or text snippet.  
   - Method: POST  
   - Payload: { document_id: string, length: “short”|“long” }  
   - Response: Summarized text.

5. **/api/v1/sync/status**  
   - Purpose: Get current status of file synchronization.  
   - Method: GET  

6. **/api/v1/metrics**  
   - Purpose: Health and usage metrics for monitoring.  
   - Method: GET  

7. **/api/v1/auth/login** & **/logout**  
   - Purpose: Obtain or invalidate JWT tokens.

These endpoints serve both the web dashboard and the Telegram bot.

---

## 5. Hosting Solutions

Current Environment
- **Linux Server (8 GB RAM, 120 GB SSD)**: Hosts Dockerized services (Qdrant, FastAPI, ingestion, sync).
- **Synology NAS**: Backup storage for raw files and Qdrant snapshots.

Cloud Storage Endpoints
- **Yandex Disk** and **Google Drive**: Mounted via `rclone` for primary and secondary file sources.

Advantages
- **Cost-Effective**: No ongoing cloud VM costs.
- **Full Control**: You own hardware and backups.
- **Reliability**: Local infrastructure with VPN and firewall ensures secure access.

Future Options
- Migrating to a cloud provider (AWS/GCP/Azure) with managed Kubernetes.
- Using a managed vector DB service if scale demands.

---

## 6. Infrastructure Components

1. **Reverse Proxy / Load Balancer**
   - Nginx handles SSL termination and routes traffic to FastAPI and the web dashboard.

2. **Synchronization Mechanism**
   - `rclone` (or `Syncthing`) runs as a scheduled service to sync files from NAS, Yandex, and Google.

3. **Container Orchestration**
   - Docker Compose manages multi-container setups locally.
   - Each service has its own container: sync, ingestion, API, Qdrant.

4. **Content Delivery**
   - Static assets for the web dashboard can be served via Nginx and optionally cached through a CDN (e.g., Cloudflare).

5. **Caching Layer (Optional)**
   - Redis for caching frequent queries or API responses to reduce Qdrant load.

6. **Task Scheduling**
   - Cron jobs or Celery Beat to run nightly indexing and backup tasks.

These components together provide load distribution, fault tolerance, and fast response times.

---

## 7. Security Measures

Authentication & Authorization
- JWT tokens for API access.
- Role-based permissions for admin vs. standard users.

Network Security
- **VPN**: Required for direct SSH or admin access to the server.
- **Firewall Rules**: Only ports 443 (HTTPS) and 22 (SSH over VPN) are open.

Data Encryption
- **At Rest**: Qdrant snapshots and raw files on NAS encrypted with AES-256.
- **In Transit**: All API traffic over HTTPS/TLS.

API Security
- Rate limiting on endpoints to prevent abuse.
- Input validation and sanitization in FastAPI.

Compliance
- You control all hardware; policies can be drafted to comply with GDPR or other standards as needed.

---

## 8. Monitoring and Maintenance

Logging
- Centralized logs (via Docker logging drivers) aggregated to a log file or ELK stack.
- Application logs from FastAPI include request traces, errors, and performance metrics.

Metrics & Alerts
- **Prometheus** collects metrics from FastAPI, Qdrant, and sync jobs.
- **Grafana Dashboard** displays real-time CPU, memory, request latency, and QPS.
- Alerting for failed syncs, high API latency, or low disk space.

Backups & Recovery
- Nightly snapshots of Qdrant stored on Synology NAS.
- Periodic full backups of raw documents and configurations.

Maintenance Tasks
- Regular dependency updates (Docker images, Python packages).
- Security patching of the OS and containers.
- Quarterly review of firewall and VPN configurations.

---

## 9. Conclusion and Overall Backend Summary

This backend setup unifies your document sources, processes them for semantic capabilities, and serves both humans (via web/Telegram) and AI models. Key strengths:
- **Modularity**: Independent services for sync, ingestion, embedding, and retrieval.
- **Flexibility**: Supports multiple AI providers (OpenAI, Claude, Gemini).
- **Cost-Effective Hosting**: Runs on your Linux server + NAS with optional cloud integration.
- **Security & Compliance**: VPN, firewall, encryption, and role-based access.
- **Scalability**: Docker containers can scale horizontally; Qdrant can cluster when needed.

Together, these components deliver a robust, maintainable, and high-performing AI-powered document management backend tailored to your needs.