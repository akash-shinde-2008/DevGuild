"""A bounded host for the local portfolio generator using Gemma via structured prompting."""
import json
import logging
from pathlib import Path

import ollama

from tools import (
    calculate_profile_score,
    check_skills,
    generate_portfolio_assets,
    push_to_supabase,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

MODEL_NAME = "gemma2:9b"
MAX_STEPS = 6

# Replace with your Supabase credentials
SUPABASE_URL = "https://vbhxgcxwfjzwkamzgqhi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZiaHhnY3h3Zmp6d2thbXpncWhpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTI5ODIyMzAsImV4cCI6MjEwODU1ODIzMH0.vTPjnXksTFxpv1JCSfGRkyJ5d03v5WOVNUUqhjlu1ZQ"

TOOLS = {
    "calculate_profile_score": calculate_profile_score,
    "check_skills": check_skills,
    "generate_portfolio_assets": generate_portfolio_assets,
}
ORDER = ("calculate_profile_score", "check_skills", "generate_portfolio_assets")

TOOL_DESCRIPTIONS = """
Available Tools:
1. calculate_profile_score(projects: int, internships: int, certifications: int, github_repos: int)
2. check_skills(target_role: str, skills: str)
3. generate_portfolio_assets(name: str, target_role: str, skills: str, project_details: str, contact: str, github_handle: str)

Instructions:
To call a tool, respond ONLY with a valid JSON object matching this schema:
{"name": "tool_name", "arguments": {"param1": "value"}}

When all tools have completed, respond normally in plain text summarizing the results.
"""


def build_system_prompt() -> str:
    path = Path(__file__).resolve().with_name("SKILL.md")
    return (
        "You are a portfolio planning assistant.\n"
        + path.read_text(encoding="utf-8")
        + "\n\n"
        + TOOL_DESCRIPTIONS
    )


def dispatch(name: str, args: dict) -> dict:
    if name not in TOOLS:
        return {"error": f"Unknown tool: {name}"}
    try:
        return TOOLS[name](**args)
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}


def parse_tool_call(content: str) -> tuple[str, dict] | None:
    text = content.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
    try:
        data = json.loads(text.strip())
        if isinstance(data, dict) and "name" in data and "arguments" in data:
            return data["name"], data["arguments"]
    except Exception:
        pass
    return None


def run_agent(user_query: str, client: ollama.Client | None = None) -> str:
    if not isinstance(user_query, str) or not user_query.strip():
        return "Please provide a portfolio request."

    try:
        system = build_system_prompt()
    except OSError as exc:
        return f"Cannot load SKILL.md: {exc}"

    if client is None:
        client = ollama.Client(host="http://localhost:11434", timeout=120.0)

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_query},
    ]
    completed = []

    for step in range(1, MAX_STEPS + 1):
        pending = ORDER[len(completed):len(completed) + 1]

        try:
            response = client.chat(
                model=MODEL_NAME,
                messages=messages,
                options={"temperature": 0},
            )
        except Exception as exc:
            return f"Model request failed: {type(exc).__name__}: {exc}"

        message = response.message
        content = (message.content or "").strip()
        messages.append({"role": "assistant", "content": content})

        parsed = parse_tool_call(content)

        if not parsed:
            if len(completed) < len(ORDER):
                return (
                    "Plan incomplete; all tool checks are required.\n"
                    + (content or "Please supply all required inputs.")
                )
            return content or "All checks finished; model summary was empty."

        name, args = parsed

        if name not in TOOLS:
            return f"Stopped: unknown tool {name}."
        if not pending or name != pending[0]:
            return f"Stopped: tool {name} is out of order or repeated."

        log.info("Step %d REQUEST %s %s", step, name, args)
        result = dispatch(name, args)
        log.info("Step %d RESULT %s %s", step, name, result)

        messages.append({
            "role": "user",
            "content": f"Tool '{name}' result: {json.dumps(result)}",
        })

        if "error" in result:
            return f"Stopped: {name}: {result['error']}"

        completed.append(name)

        if name == "generate_portfolio_assets":
            try:
                with open("portfolio_data.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                push_to_supabase(
                    supabase_url=SUPABASE_URL,
                    supabase_key=SUPABASE_KEY,
                    name=data["profile"]["name"],
                    target_role=args.get("target_role", "web developer"),
                    skills=data.get("skills", []),
                    contact=data["profile"]["contact"],
                    github_handle=args.get("github_handle", "dev"),
                    portfolio_json=data,
                )
                log.info("Uploaded generated portfolio directly to Supabase.")
            except Exception as e:
                log.error("Failed to upload to Supabase: %s", e)

    return "Stopped: reached MAX_STEPS without a final answer."


if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  DevGuild • AI Freelance Portfolio & Resume Generator")
    print("=" * 55)
    print("Paste candidate details (or press Enter for default demo):")
    user_input = input("\n> ").strip()

    if not user_input:
        user_input = (
            "Create a portfolio and resume for Asha Patil, aspiring web developer. "
            "She has 3 projects, 1 internship, 2 certifications, and 6 GitHub repos. "
            "Skills: JS, ReactJS, HTML, Git, Tailwind. "
            "Projects: Weather app using React; Campus notes sharing site. "
            "Contact: asha@example.com. GitHub handle: ashapatil."
        )

    print("\nRunning Gemma agent pipeline...\n")
    print(run_agent(user_input))