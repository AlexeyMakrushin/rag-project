# App Flow Document

## Onboarding and Sign-In/Sign-Up

When a new user first visits the application, they arrive at a clean landing page that explains the core purpose: centralizing and AI‐enriching personal documents. A prominent button invites them to sign up or sign in. Clicking sign up opens a simple form where they enter their email address and choose a password. Alternatively, they can sign up with a Google account or via a Telegram login link, which automatically retrieves basic profile information and sends a confirmation code. Once they submit the form, the system sends a verification email or Telegram message containing a code that the user must enter to confirm their account. Upon confirmation, they are taken straight into the application. Returning users click the sign‐in link, enter their credentials or choose the social login option again, and are authenticated. If a user forgets their password, they click a “Forgot password” link, enter their email address, receive a reset link, and follow it to set a new password. A sign‐out button sits in the top right corner of every page, and clicking it immediately ends the session and returns the user to the landing page.

## Main Dashboard or Home Page

Once signed in, the user lands on the main dashboard, which greets them by name and displays a high‐level overview of the system state. Along the top is a persistent header with the application logo on the left, a search bar in the center, and a user menu on the right. Down the left side runs a navigation panel containing links to Sync Status, Document Library, Search, Indexing, Settings, and Help. In the center of the screen, the user sees widgets showing the number of indexed files, date of the last sync, storage usage, and any active alerts. Below that, a list of recent documents or recent search queries is presented so the user can resume work quickly. Every item in that list is clickable, taking the user directly to the document preview or search result.

## Detailed Feature Flows and Page Transitions

### Synchronization Setup Flow

From the navigation panel, the user clicks Sync Status to go to the synchronization setup page. Here they see existing connections for Synology NAS, Yandex Disk, and Google Drive, along with a button to add a new storage provider. Clicking that button reveals a form where the user chooses the service type, enters credentials or API tokens, selects the folders to sync, and saves. As soon as the connection is active, the dashboard updates to show sync progress in real time. If the user wants to pause or resume syncing, they simply toggle a switch next to each provider entry. Whenever a new file appears or changes in one of the connected folders, the sync engine pushes or pulls it to the central server automatically.

### Document Ingestion and Indexing Flow

When files land on the server via sync, a background watcher notices new or changed items and begins the ingestion pipeline. For users who prefer manual control, the Indexing link in the navigation opens a page where they can trigger a full re‐index or an incremental update. On that page, a progress bar shows the number of files processed, chunks embedded, and any errors encountered. If a document fails to convert, a link allows the user to review the error details and retry just that file. Once indexing finishes, the system writes the new vectors into the database and the dashboard’s statistics widget refreshes to reflect the updated counts.

### Search and Q&A Flow

To perform a semantic search or ask a question, the user types into the search bar at the top of any page or selects Search in the navigation. The Search page loads with an input box and a large run button. After submitting a query, the screen fills with a ranked list of matching documents and snippets. Each listing shows the document title, path, modification date, and a preview snippet. Clicking a result opens a full preview pane where the user can scroll the original text or click an Ask a Question button. That brings up a Q&A panel at the side. The user types or selects follow‐up questions, and the system displays AI‐generated answers with linked references to the source document. A Summarize button yields a concise overview of the entire file.

### Report Drafting and AI Assistance Flow

From the document preview or Q&A panel, the user may choose Create Report, which opens an embedded editor pane. This pane connects to the Claude desktop plugin or the built‐in text field in the web app. As the user types, the plugin fetches relevant context from the vector store and suggests sentences or data points. The suggestions appear inline, and the user can accept, edit, or reject them. Once satisfied with the draft, the user clicks Export to download a Word document or copy the content for another application.

### Telegram Bot Interaction Flow

Users can also interact through Telegram. After linking their Telegram account in Settings, they message the bot with commands like “search budget report” or “summarize Q1 sales.” The bot forwards those to the same backend API and returns the results as chat messages, complete with preview links and answer blocks. If the user’s server is behind a VPN, they set up a webhook or use a proxy service to allow the bot to communicate with the REST API securely.

### Claude Desktop Plugin Flow

When drafting in Claude, the user grabs the plugin icon from the sidebar. The first time they click it, they supply the local API endpoint URL and an access token. After that, whenever they highlight text or ask for context, the plugin sends queries to the local service, retrieves relevant document excerpts or summaries, and inserts them directly into the Claude session. Users can adjust model parameters in the plugin settings.

## Settings and Account Management

Clicking Settings in the navigation takes the user to a unified settings page with tabs for Profile, Storage, API Keys, Notifications, and Backup. In Profile, the user updates email, password, and display name. The Storage tab lists connected providers and offers add or remove options. API Keys shows the user’s personal token for REST API access and allows regeneration. Notifications lets them choose whether they receive emails or Telegram messages for sync errors, backup failures, or indexing issues. In Backup, the user sets the frequency of encrypted snapshots to the NAS and toggles on or off. After saving any changes, a confirmation banner appears, and the user can click Home to return to the main dashboard.

## Error States and Alternate Paths

If the user enters an invalid email or password on login, a clear inline message informs them of the mistake and suggests using the reset password flow. During synchronization, if a connection to Yandex Disk or NAS fails, an alert icon appears next to that provider with a Retry link. Indexing failures show a red progress bar and a list of files that could not be processed, each with a Retry button. On the Search page, if the API experiences rate limits or connectivity problems, a notification banner invites the user to try again later or reduce query complexity. Should the backup to NAS run out of disk space, the user sees a warning icon in Backup settings and an email and Telegram message explaining the issue. All error messages include guidance on how to resolve or whom to contact for support.

## Conclusion and Overall App Journey

The user’s journey begins with signing up or logging in and moves immediately to the dashboard, where they connect storage providers to synchronize files. As documents flow in, the ingestion pipeline transparently converts and indexes them in the vector database. From any page, the user can search or ask questions in natural language, preview results, generate summaries, and draft new reports with AI assistance. Alternate interfaces like the Telegram bot and the Claude desktop plugin offer the same core capabilities in chat or writing environments. Throughout the experience, settings let the user manage their account, storage connections, API keys, notifications, and backup schedules. Error states are handled gracefully with inline messages and retry options, ensuring that the user always knows what went wrong and how to fix it. Overall, the system guides the user from account setup to everyday productivity, delivering AI‐powered document retrieval and authoring in a simple, unified flow.
