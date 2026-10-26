# DevGuild 🌐 — Autonomous Talent Pipeline
**Hacktoberfest 2026 Submission**

DevGuild is a two-sided freelance developer marketplace. Instead of manually filling out long profile forms, developers simply provide their GitHub handle. An autonomous local AI agent (powered by Gemma 2) ingests their public repositories, evaluates their technical readiness, synthesizes action-driven resume bullets, generates a personalized learning roadmap for missing skills, and instantly publishes their portfolio to a live talent directory.

## 🚀 Features

- **GitHub Auto-Ingestion:** Fetches public repositories, descriptions, and languages directly via the GitHub API.
- **Local AI Agent (Gemma 2):** Uses Ollama to run structured reasoning steps that score profiles, match skills, and generate polished portfolio payloads.
- **Deterministic Roadmaps:** Maps identified skill gaps to actionable, time-bound learning milestones.
- **Real-Time Live Directory:** Uses Supabase to instantly sync imported profiles to the global frontend.
- **Terminal Monitor:** A Python-based listener that watches the Supabase database and alerts the terminal in real time when new builders are published from the UI.
- **Single-File Frontend:** A lightning-fast, highly polished `index.html` using Tailwind CSS and vanilla JavaScript.

## 🏗️ Architecture & Tech Stack

1. **Frontend UI:** Vanilla HTML5, Tailwind CSS (via CDN), Supabase JS SDK.
2. **Backend Agent / Tooling:** Python 3, Ollama (Gemma 2 9B).
3. **Database:** Supabase (PostgreSQL).

## 🛠️ Setup & Installation

### Prerequisites
- [Ollama](https://ollama.com/) installed locally with the Gemma 2 model (`ollama run gemma2:9b`).
- Python 3.10+
- A free [Supabase](https://supabase.com) account.

### 1. Database Configuration
1. Create a new Supabase project.
2. Run this SQL command in the Supabase SQL Editor to create the main table:
   ```sql
   CREATE TABLE freelance_profiles (
       id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
       created_at TIMESTAMPTZ DEFAULT NOW(),
       name TEXT,
       role TEXT,
       contact TEXT,
       github_url TEXT,
       skills TEXT[],
       is_available BOOLEAN DEFAULT TRUE,
       portfolio_json JSONB
   );
   ```
3. Disable Row Level Security (RLS) for the demo, or add a public `SELECT` and `INSERT` policy.

### 2. Environment Setup
Add your Supabase Project URL and Anon Key to:
- `app.py` and `monitor.py` (Python files).
- The top of the `<script>` tag in `index.html`.

### 3. Running the Project

**Start the Terminal Monitor:**
This script will watch for new profiles being published live.
```bash
python monitor.py
```

**Launch the Frontend:**
Since the frontend is static, you can simply open `index.html` in any web browser, or use a local server:
```bash
python -m http.server 8000
```
Then navigate to `http://localhost:8000`.

**Run the Local AI Pipeline (Optional Backend mode):**
If you want to run the Gemma agent directly from the CLI instead of the UI:
```bash
python app.py
```

## 🤝 Contributing
This project is open for Hacktoberfest! Feel free to fork the repository, submit pull requests, and open issues for UI improvements or backend pipeline optimizations.

## Developers
This project was created by the DevGuild. The onboard members were Akash Shinde (akash-shinde2008) and Niranjan Salunkhe (YesWizardo).