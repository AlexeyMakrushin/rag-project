# Project Requirements Document

## 1. Project Overview

You want to build a personal document indexing and AI-powered retrieval system that pulls together your Word, PowerPoint, Excel and PDF files from multiple machines (MacBook Air M3, iMac), a Synology NAS, Yandex Disk and Google Drive. The system will automatically sync files to your 120 GB server, extract and embed their text, store embeddings in a vector database, and let you search, ask questions, auto-summarize or get writing assistance from an AI. You will interact via a simple web dashboard, a Telegram bot and a Claude desktop plugin, with the option to add a standalone desktop app later.

This project is driven by three main goals:

1.  **Centralization & Searchability** – stop hunting through scattered folders by giving every document a place in a single, semantic index.
2.  **AI-Assisted Productivity** – use semantic search, Q&A and summary features to speed up report writing and analytics.
3.  **Safety & Reliability** – keep your data backed up on NAS, encrypted at rest, synchronized automatically and monitored for failures. Success means sub-second search responses, nightly backup completion, and 95% accuracy in retrieving relevant documents.

## 2. In-Scope vs. Out-of-Scope

### In-Scope (Version 1.0)

*   Automated two-way file synchronization across Synology NAS, 120 GB server, Yandex Disk and Google Drive using tools like Syncthing or rclone.
*   Document ingestion pipeline: detect file type, extract text (via Apache Tika or pdfplumber), normalize content and capture metadata.
*   Cloud-based embedding generation (OpenAI text-embedding-ada-002, with caching and batching).
*   Vector store deployment on the 120 GB server using Qdrant (open-source vector database).
*   Nightly encrypted backups of the raw files and Qdrant data to Synology NAS.
*   Lightweight REST API (Python + FastAPI) for semantic search, Q&A, summarization and on-demand re-indexing.
*   Web dashboard (React/Next.js) to enter queries, view results, preview documents and trigger re-index jobs.
*   Telegram bot integration for quick Q&A and file searches.
*   Claude desktop plugin to call the local API for drafting assistance.
*   Basic security: TLS for transport, AES-256 encryption at rest, VPN/SSH-only access, firewall rules.
*   Monitoring & logging of sync jobs, ingestion errors, API health and storage usage with alerting via Telegram or email.

### Out-of-Scope (Phase 2+)

*   On-device embedding models or fully offline AI.
*   Mobile apps (iOS/Android).
*   Advanced multi-user role and permission management.
*   Audio, video or image content indexing.
*   A monolithic desktop client beyond the initial plugin.
*   Automated AI-driven file tagging or auto-cleanup (although manual tools will exist).

## 3. User Flow

When you add or modify files on your Synology NAS, Yandex Disk or Google Drive, a sync agent (Syncthing/rclone) running on your NAS and server mirrors those changes to the 120 GB server in near-real time. A watcher process notices new or updated documents, runs them through a text-extraction step, splits them into logical chunks, and sends each chunk to a cloud embedding API. Embeddings and metadata go into Qdrant, and a nightly cron job snapshots both documents and database data back to your NAS in an encrypted form.

To search or get AI assistance, you open the web dashboard, type a query, and see ranked results with snippets and relevance scores. You can click through to preview the original file, ask follow-up questions or request an automatic summary. Alternatively, you send a query to the Telegram bot and get results in chat bubbles, or ask directly inside Claude desktop—your plugin fetches context from the REST API and feeds it to the language model to draft new content. If you reorganize or clean files, you trigger a manual re-index from the dashboard or via a command-line script to keep the vector store up to date.

## 4. Core Features

*   **Storage Synchronization**

    *   Automated two-way sync across NAS, server and cloud drives
    *   Conflict resolution with versioning or overwrite rules

*   **Preprocessing & Extraction**

    *   File-type detection (Office vs. PDF)
    *   Text extraction (Apache Tika, pdfplumber) and normalization
    *   Metadata capture (path, timestamp, size)

*   **Embedding Pipeline**

    *   Batch calls to a cloud embedding API (OpenAI)
    *   Local cache of embeddings to avoid duplicate API calls
    *   Future-proof hooks for on-device models

*   **Vector Database**

    *   Qdrant deployed in Docker on the server
    *   Stores vectors + associated metadata for fast nearest-neighbor queries

*   **Backup & Recovery**

    *   Nightly encrypted snapshots of raw files and vector store to NAS
    *   Simple restore procedure documented in case of data loss

*   **REST API**

    *   Endpoints for `search`, `qa`, `summarize` and `reindex`
    *   Token-based authentication, TLS only

*   **Web Dashboard**

    *   React/Next.js SPA
    *   Search bar, result list, document preview, summary view, reindex button

*   **Telegram Bot**

    *   Node.js or Python client using Telegram Bot API
    *   Handles `/search`, `/ask`, `/summary` commands

*   **Claude Desktop Plugin**

    *   Calls local REST API for context when drafting in Claude

*   **Monitoring & Alerting**

    *   Logs ingestion errors, API latency, disk usage
    *   Alerts via Telegram or email on failure or low storage

## 5. Tech Stack & Tools

*   **Frontend**

    *   React, Next.js for the web dashboard

*   **Backend**

    *   Python 3.x + FastAPI for REST services
    *   Node.js or Python for the Telegram bot

*   **Vector Store**

    *   Qdrant (Docker container)

*   **Sync & Storage**

    *   Syncthing or rclone for file sync
    *   Cron/systemd timers for scheduled jobs

*   **Containerization**

    *   Docker, Docker Compose

*   **AI Models & APIs**

    *   OpenAI Embeddings API (text-embedding-ada-002)
    *   (Optional) OpenAI GPT-3.5 or Claude 3.7 Sonnet for summarization/Q&A
    *   Google Gemini 2.5 Pro for future tests

*   **IDE & Dev Tools**

    *   VS Code with Cursor extension for AI-powered coding
    *   Cline for collaborative AI pairing

*   **Bot Integration**

    *   Telegram Bot API

*   **Infrastructure**

    *   120 GB Linux server (8 GB RAM)
    *   Synology NAS for backups (16 GB RAM)
    *   MacBook Air M3 and iMac development clients

## 6. Non-Functional Requirements

*   **Performance**:

    *   Semantic search queries return results within 500 ms on average.
    *   Batch embedding pipeline processes 1 GB of text in under 15 minutes.

*   **Scalability**:

    *   Support up to 100 GB of indexed documents and 10 million vectors.

*   **Reliability**:

    *   99% uptime for the REST API.
    *   Nightly backup success rate ≥ 95%.

*   **Security**:

    *   TLS for all API traffic.
    *   AES-256 encryption at rest for backups and vector store.
    *   Access restricted via VPN/SSH and firewall rules.

*   **Usability**:

    *   Web UI works on desktop and tablet browsers.
    *   Telegram bot commands are discoverable via `/help`.

*   **Maintainability**:

    *   Modular codebase with clear package boundaries.
    *   Containerized services for easy updates.

## 7. Constraints & Assumptions

*   Server resources are limited (8 GB RAM, 120 GB storage), so indexing and queries must be memory-efficient.
*   You will rely on a stable internet connection and cloud API availability (OpenAI, Anthropic).
*   Yandex Disk and Google Drive rate limits are unknown; sync tools must handle throttling and retries.
*   The initial corpus is mostly static; nightly incremental indexing is sufficient.
*   Future multi-user support will require an OAuth provider or API-key management, but V1 is single-user.

## 8. Known Issues & Potential Pitfalls

*   **API Rate Limits & Cost**

    *   Embedding large documents can hit OpenAI rate limits or cost more than expected.
    *   Mitigation: batch requests, cache embeddings, monitor usage.

*   **File Conversion Errors**

    *   Complex Office files may fail extraction or lose formatting.
    *   Mitigation: log failures, skip or flag for manual review.

*   **Sync Conflicts**

    *   Simultaneous edits across devices can create version collisions.
    *   Mitigation: use a sync tool with built-in conflict resolution and version history.

*   **Backup Failures**

    *   NAS may become unreachable or run out of space.
    *   Mitigation: disk-usage alerts and automatic retries.

*   **Vector Store Growth**

    *   Qdrant database may grow beyond server capacity over time.
    *   Mitigation: archive old vectors, shard collections or prune low-value data.

–––\
This document spells out exactly what to build in Version 1.0. It covers the core architecture, features, user flows, tools and safeguards so you—or an AI model—can move directly into technical designs (tech stack docs, frontend guidelines, backend structure, etc.) without missing any critical detail.
