# Portfolio & Freelance Profile Generator

## Purpose
Score a student's technical readiness, evaluate role-specific skills, and generate a structured JSON portfolio state along with a clean Markdown resume for freelancing.

## Required inputs
projects, internships, certifications, github_repos, target_role, skills, name, project_details, contact, github_handle

## Workflow
1. Request calculate_profile_score once.
2. After success, request check_skills once.
3. After success, request generate_portfolio_assets once.
4. Summarise all results in clear language, confirming both portfolio_data.json and generated_resume.md are created.

## Constraints
Never guess missing input values.
Do not invent projects, skills, or github handles.
Request one tool per turn. Never repeat a completed tool.
Report missing skills and readiness scores clearly.

## Missing inputs and errors
Ask for missing inputs instead of inventing them.
On a tool error, report it. Do not retry in the same run.