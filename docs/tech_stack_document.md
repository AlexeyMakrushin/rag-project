# Tech Stack Document

This document explains the technology choices for your personal document indexing and AI-powered retrieval system. It’s written in everyday language so anyone—technical or not—can understand why each tool and framework was selected.

## 1. Frontend Technologies

We want a smooth, responsive interface that works in your browser today and can evolve into a desktop app later.

*   **React & Next.js**\
    A popular combination for building fast web apps. Next.js gives us automatic routing, server-side rendering (for snappy page loads) and easy API routes.
*   **CSS Modules (built into Next.js)**\
    Lets us write component-scoped styles without worrying about name clashes. We can also add a utility-first library like Tailwind CSS later if you want more design flexibility.
*   **Responsive Design**\
    We’ll use standard CSS techniques (flexbox, grid, media queries) so the dashboard works on both desktop and tablet browsers.

## 2. Backend Technologies

The backend glues everything together: it syncs files, extracts text, creates embeddings, stores them, and answers your queries.

### 2.1 Server & API Frameworks

*   **FastAPI (Python)**\
    A modern, high-performance web framework perfect for building our REST API (`/search`, `/qa`, `/summarize`, `/reindex`). It’s easy to secure and auto-generates documentation.
*   **Node.js (or Python)**\
    Used for the Telegram Bot service. Both ecosystems have solid libraries for the Telegram Bot API.

### 2.2 Text Extraction & Preprocessing

*   **Apache Tika** and **pdfplumber**\
    To convert Word, PowerPoint, Excel and PDF files into plain text. We’ll normalize the text (remove headers/footers, boilerplate), capture metadata (file path, timestamp, size), and chunk large documents.

### 2.3 Embedding & Language Models

*   **OpenAI Embeddings API (text-embedding-ada-002)**\
    Generates the vector representations that power semantic search.
*   **OpenAI GPT-3.5** and **Anthropic Claude 3.7 Sonnet**\
    Provide text-generation services for Q&A and document summarization.
*   **Google Gemini 2.5 Pro** (future plug-in)\
    We plan to experiment with this for advanced reasoning tasks.

### 2.4 Vector Database

*   **Qdrant** (running in Docker)\
    An open-source vector store that gives us fast nearest-neighbor search and flexible metadata filters.

### 2.5 Sync & Scheduling

*   **rclone** or **Syncthing**\
    Automates two-way sync between your Synology NAS, Yandex Disk, Google Drive and the 120 GB server.
*   **cron** (or systemd timers)\
    Schedules nightly backups, incremental indexing jobs and health-check scripts.

## 3. Infrastructure and Deployment

We’ll keep everything on your existing hardware, containerized for easy maintenance.

*   **Hosting Platforms**

    *   120 GB Linux server (8 GB RAM) for all processing and services
    *   Synology NAS (16 GB RAM) for encrypted backups

*   **Containerization**

    *   Docker & Docker Compose to package each service (API, vector store, bot) in its own container

*   **Version Control & CI/CD**

    *   Git for source code management
    *   GitHub (or GitLab) Actions to automatically build and push Docker images, then deploy to your server via SSH

*   **Development Tools**

    *   **VS Code** with the **Cursor** extension for AI-powered coding assistance
    *   **Cline** as an AI pairing partner when designing and debugging features

*   **Monitoring & Logging**

    *   Lightweight metrics (Prometheus + Grafana or a hosted alternative) to track CPU/disk usage, API latency and error rates
    *   Centralized logs with alerting (via Telegram or email) if sync, embedding calls or backups fail

## 4. Third-Party Integrations

These services extend your system without you having to build everything from scratch.

*   **Cloud File Storage**

    *   Yandex Disk & Google Drive (via rclone/Syncthing) for file sync and consolidation

*   **Messaging & Chat**

    *   Telegram Bot API to answer queries and deliver summaries in chat

*   **AI & Cloud APIs**

    *   OpenAI (embeddings, GPT-3.5)
    *   Anthropic Claude 3.7 Sonnet (hybrid reasoning)
    *   Google Gemini 2.5 Pro (future tests)

## 5. Security and Performance Considerations

We want to protect your data and keep the system fast as your corpus grows.

### 5.1 Security Measures

*   **Encryption at Rest**

    *   AES-256 for both the Qdrant data volumes and nightly NAS backups

*   **Secure Transport**

    *   TLS/HTTPS for all API traffic
    *   VPN or SSH-only access with strict firewall rules

*   **Access Control**

    *   Token-based authentication on the FastAPI service
    *   Future support for OAuth or scoped API keys when you add more users

### 5.2 Performance Optimizations

*   **Batch Embedding & Caching**

    *   Group text chunks into batches to reduce API cost and latency
    *   Cache embeddings locally so only new or changed content triggers calls

*   **Incremental Indexing**

    *   A nightly cron job processes only modified files
    *   On-demand re-indexing via the dashboard or CLI when you reorganize

*   **Vector Store Tuning**

    *   Configure Qdrant with appropriate collection shards and distance metrics
    *   Prune or archive low-value vectors if storage gets tight

## 6. Conclusion and Overall Tech Stack Summary

By combining open-source tools, reliable cloud APIs and your existing hardware, we’ll build a system that:

*   **Centralizes** your scattered documents into one searchable index
*   **Empowers** you with semantic search, Q&A and auto-summaries
*   **Secures** your data with encryption, VPN/SSH and regular backups
*   **Scales** comfortably to 100+ GB of files and millions of vectors
*   **Deploys** easily via Docker and CI/CD on your 120 GB server

Key highlights that set this stack apart:

*   Use of **FastAPI** for clean, documented REST endpoints
*   **Qdrant** for open-source, self-hosted vector search
*   A combo of **OpenAI**, **Claude** and **Gemini** for best-in-class AI capabilities
*   **rclone/Syncthing** bridging local NAS, Yandex Disk and Google Drive seamlessly
*   **VS Code + Cursor** and **Cline** empowering rapid, AI-driven development

This setup aligns with your goals of centralization, AI-assisted productivity and rock-solid reliability. With these technologies in place, you’ll have a maintainable, extensible foundation to build advanced search, Q&A and drafting tools on top of your personal document library.
