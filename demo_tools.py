"""Direct unit validation for tools without LLM involvement."""
from tools import calculate_profile_score, check_skills, generate_portfolio_assets

# 1. Score
r = calculate_profile_score(3, 1, 2, 6)
assert r["score"] == 65 and r["level"] == "promising"
assert r["breakdown"]["github_repos"] == 15
assert calculate_profile_score(0, 0, 0, 0)["level"] == "starter"
assert calculate_profile_score(9, 9, 9, 9)["score"] == 100

# 2. Skill check
r = check_skills("web developer", "JS, ReactJS, html5, js, tailwind")
assert "javascript" in r["matched"] and "react" in r["matched"]
assert "css" in r["missing"] and "git" in r["missing"]

# 3. Asset generation
r = generate_portfolio_assets(
    "Asha", "web developer", "js, css, react", "Weather app; Notes app",
    "asha@example.com", "ashapatil"
)
assert r["status"] == "success"
assert r["freelance_ready"] is True

# 4. Guardrails
for bad in [True, -1, "3", 1.5, 1001]:
    try:
        calculate_profile_score(bad, 1, 1, 1)
    except ValueError:
        pass
    else:
        raise AssertionError(f"Invalid input {bad} was accepted")

print("All direct tool checks passed successfully.")