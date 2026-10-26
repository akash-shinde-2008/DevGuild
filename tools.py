"""Tools for the local portfolio agent: profile scoring, skill checking, asset generation, and Supabase upload."""
import json
import logging
import urllib.error
import urllib.request
from typing import Any

from supabase import create_client

log = logging.getLogger(__name__)

BENCHMARKS = {
    "web developer": {
        "core_skills": ["html", "css", "javascript", "react", "git", "tailwind", "node.js"],
        "min_projects": 2,
    },
    "frontend developer": {
        "core_skills": ["html", "css", "javascript", "react", "typescript", "git", "tailwind"],
        "min_projects": 2,
    },
    "backend developer": {
        "core_skills": ["python", "node.js", "sql", "git", "docker", "api"],
        "min_projects": 2,
    },
    "full stack developer": {
        "core_skills": ["javascript", "react", "node.js", "sql", "git", "html", "css"],
        "min_projects": 3,
    },
}

ROADMAP_LOOKUP = {
    "css": {"duration": "2 weeks", "action": "Build a responsive CSS Grid/Flexbox landing page from Figma."},
    "node.js": {"duration": "3 weeks", "action": "Develop a REST API with Express, JWT authentication, and PostgreSQL."},
    "python": {"duration": "3 weeks", "action": "Write automated CLI scripts and data-processing pipelines using Pandas."},
    "react": {"duration": "3 weeks", "action": "Build a SPA with state management and external API integrations."},
    "docker": {"duration": "1 week", "action": "Containerize a full-stack web application with Docker Compose."},
    "sql": {"duration": "2 weeks", "action": "Practice complex joins, indexing, and design relational schemas in PostgreSQL."},
    "typescript": {"duration": "2 weeks", "action": "Refactor an existing JavaScript project to strict TypeScript types."},
    "git": {"duration": "1 week", "action": "Master branch rebasing, merge conflict resolution, and GitHub Actions CI/CD."},
}


def calculate_profile_score(
    projects: int,
    internships: int,
    certifications: int,
    github_repos: int,
) -> dict[str, Any]:
    """Scores candidate readiness out of 100 based on quantifiable achievements."""
    projects_pts = min(int(projects) * 10, 40)
    internships_pts = min(int(internships) * 10, 20)
    certs_pts = min(int(certifications) * 5, 15)
    repos_pts = min(int(github_repos) * 2.5, 25)

    total = int(projects_pts + internships_pts + certs_pts + repos_pts)

    if total >= 80:
        level = "Job Ready"
    elif total >= 60:
        level = "Promising"
    else:
        level = "Needs Development"

    return {
        "score": total,
        "max_score": 100,
        "level": level,
        "breakdown": {
            "projects": projects_pts,
            "internships": internships_pts,
            "certifications": certs_pts,
            "github_repos": int(repos_pts),
        },
    }


def check_skills(target_role: str, skills: str) -> dict[str, Any]:
    """Compares user skills against target benchmark role to identify matching and missing skills."""
    role_key = target_role.strip().lower()
    target = BENCHMARKS.get(role_key, BENCHMARKS["web developer"])
    core = target["core_skills"]

    # Parse candidate skills
    raw = [s.strip().lower() for s in skills.replace(";", ",").split(",") if s.strip()]
    normalized = []
    for s in raw:
        if s in ("js", "javascript"):
            normalized.append("javascript")
        elif s in ("react", "reactjs"):
            normalized.append("react")
        else:
            normalized.append(s)

    user_skills = set(normalized)
    matched = sorted([s for s in core if s in user_skills])
    missing = sorted([s for s in core if s not in user_skills])
    extra = sorted([s for s in user_skills if s not in core])

    return {
        "role": role_key,
        "matched": matched,
        "missing": missing,
        "extra": extra,
    }


def fetch_github_repos(github_handle: str) -> list[dict[str, str]]:
    """Fetches public repositories from the GitHub API."""
    url = f"https://api.github.com/users/{github_handle}/repos?sort=updated&per_page=5"
    req = urllib.request.Request(url, headers={"User-Agent": "DevGuild-Portfolio-Agent"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            repos = []
            for r in data:
                repos.append({
                    "title": r.get("name", "Project"),
                    "description": r.get("description") or "Public repository on GitHub.",
                    "url": r.get("html_url", ""),
                    "language": r.get("language") or "Code",
                })
            return repos
    except Exception:
        return []


def generate_learning_roadmap(missing_skills: list[str]) -> list[dict[str, str]]:
    """Generates a deterministic study plan for each missing skill."""
    roadmap = []
    for skill in missing_skills:
        key = skill.strip().lower()
        if key in ROADMAP_LOOKUP:
            roadmap.append({
                "skill": skill.capitalize(),
                "duration": ROADMAP_LOOKUP[key]["duration"],
                "action": ROADMAP_LOOKUP[key]["action"],
            })
        else:
            roadmap.append({
                "skill": skill.capitalize(),
                "duration": "2 weeks",
                "action": f"Build a practical proof-of-concept project applying {skill}.",
            })
    return roadmap


def generate_resume_bullet(title: str, description: str, role: str) -> str:
    """Formats project facts into an action-driven resume bullet point."""
    clean_title = title.replace("-", " ").title()
    desc = description.strip().rstrip(".")
    return f"Engineered and deployed {clean_title} ({desc}), ensuring production-grade architecture and maintainable code quality for {role} workflows."


def generate_portfolio_assets(
    name: str,
    target_role: str,
    skills: str,
    project_details: str,
    contact: str,
    github_handle: str,
    theme: str = "neon-developer",
    readiness_score: int = 65,
    readiness_level: str = "Promising",
    missing_skills: list[str] | None = None,
) -> dict[str, Any]:
    """Generates structured portfolio JSON and markdown resume."""
    if missing_skills is None:
        missing_skills = ["css", "node.js"]

    # Gather projects: GitHub API first, fallback to user string
    gh_repos = fetch_github_repos(github_handle)
    projects = []

    if gh_repos:
        for r in gh_repos[:3]:
            bullet = generate_resume_bullet(r["title"], r["description"], target_role)
            projects.append({
                "title": r["title"],
                "description": r["description"],
                "resume_bullet": bullet,
            })
    else:
        raw_items = [p.strip() for p in project_details.replace(";", ",").split(",") if p.strip()]
        for p in raw_items:
            bullet = generate_resume_bullet(p, f"Featured work in {target_role}", target_role)
            projects.append({
                "title": p,
                "description": f"Featured work in {target_role}.",
                "resume_bullet": bullet,
            })

    skill_list = [s.strip().lower() for s in skills.replace(";", ",").split(",") if s.strip()]
    roadmap = generate_learning_roadmap(missing_skills)

    portfolio_data = {
        "profile": {"name": name, "contact": contact},
        "theme": theme,
        "role": target_role,
        "skills": skill_list,
        "missing_skills": missing_skills,
        "readiness_score": readiness_score,
        "readiness_level": readiness_level,
        "projects": projects,
        "learning_roadmap": roadmap,
    }

    # Save to local JSON
    with open("portfolio_data.json", "w", encoding="utf-8") as f:
        json.dump(portfolio_data, f, indent=2)

    # Save to local Markdown Resume
    with open("generated_resume.md", "w", encoding="utf-8") as f:
        f.write(f"# {name} - {target_role.title()}\n\n")
        f.write(f"**Contact:** {contact} | **GitHub:** [{github_handle}](https://github.com/{github_handle})\n\n")
        f.write(f"### Technical Readiness: {readiness_score}/100 ({readiness_level})\n\n")
        f.write("### Verified Skills\n" + ", ".join(skill_list) + "\n\n")
        f.write("### Featured Projects & Experience\n")
        for proj in projects:
            f.write(f"- **{proj['title']}**: {proj['resume_bullet']}\n")
        f.write("\n### Target Learning Roadmap\n")
        for item in roadmap:
            f.write(f"- **{item['skill']}** ({item['duration']}): {item['action']}\n")

    return {
        "status": "success",
        "resume_path": "generated_resume.md",
        "portfolio_path": "portfolio_data.json",
        "freelance_ready": True,
    }


def push_to_supabase(
    supabase_url: str,
    supabase_key: str,
    name: str,
    target_role: str,
    skills: list[str],
    contact: str,
    github_handle: str,
    portfolio_json: dict,
) -> dict[str, Any]:
    """Inserts a generated portfolio profile directly into the Supabase database."""
    try:
        client = create_client(supabase_url, supabase_key)
        record = {
            "name": name,
            "role": target_role,
            "contact": contact,
            "github_url": f"https://github.com/{github_handle}",
            "skills": skills,
            "portfolio_json": portfolio_json,
            "is_available": True,
        }
        res = client.table("freelance_profiles").insert(record).execute()
        return {"status": "success", "data": res.data}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}