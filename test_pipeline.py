import json
from tools import generate_portfolio_assets, push_to_supabase

# Replace with your project credentials (same ones from index.html)
SUPABASE_URL = "https://vbhxgcxwfjzwkamzgqhi.supabase.co/"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZiaHhnY3h3Zmp6d2thbXpncWhpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTI5ODIyMzAsImV4cCI6MjEwODU1ODIzMH0.vTPjnXksTFxpv1JCSfGRkyJ5d03v5WOVNUUqhjlu1ZQ";

# 1. Generate local files (portfolio_data.json and generated_resume.md)
result = generate_portfolio_assets(
    name="Asha Patil",
    target_role="web developer",
    skills="js, react, html, css, git, tailwind",
    project_details="Weather app using React; Campus notes sharing platform",
    contact="asha@example.com",
    github_handle="ashapatil",
)
print("Asset Generation Status:", result["status"])

# 2. Read the structured JSON
with open("portfolio_data.json", "r", encoding="utf-8") as f:
    portfolio_data = json.load(f)

# 3. Push to the live database
db_res = push_to_supabase(
    supabase_url=SUPABASE_URL,
    supabase_key=SUPABASE_KEY,
    name=portfolio_data["profile"]["name"],
    target_role="web developer",
    skills=portfolio_data["skills"],
    contact=portfolio_data["profile"]["contact"],
    github_handle="ashapatil",
    portfolio_json=portfolio_data,
)
print("Supabase Upload Status:", db_res)