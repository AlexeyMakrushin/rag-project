flowchart TD
  S1[Synchronization Setup] --> S2[File Ingestion and Preprocessing]
  S2 --> S3[Embedding Generation]
  S3 --> S4[Vector Store Deployment]
  S4 --> S5{Initial Index Completed}
  S5 -->|Yes| S6[Schedule Incremental Updates]
  S5 -->|No| S3
  S6 --> S7[Retrieval API Layer]
  S7 --> U1[Claude Desktop Plugin]
  S7 --> U2[Telegram Bot]
  S7 --> U3[Web Dashboard]
  S7 --> M1[Security and Monitoring]