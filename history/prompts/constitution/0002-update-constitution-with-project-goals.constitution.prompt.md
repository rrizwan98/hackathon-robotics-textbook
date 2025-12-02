---
id: 0002
title: Update Constitution with Project Goals
stage: constitution
date: 2025-12-02
surface: agent
model: gemini-1.5-flash-latest
feature: none
branch: master
user: User
command: /sp.constitution Update my constitution to align with the following project goals:

Project: Physical AI & Humanoid Robotics Textbook + AI Portal

Mandatory principles to include:
- Spec-Driven Development (Spec-Kit Plus + Gemini CLI)
- AI-integrated textbook with embedded RAG chatbot
- Robotics domain alignment (ROS2, simulation, VLA, humanoids)
- Localization and accessibility: Urdu translation required
- Personalized learning for logged-in users
- Test automation for both backend (FastAPI) and frontend
- Clear branching and PR approval workflow
- Deployment standards (Docusaurus frontend + cloud backend)

Mandatory technologies to define:
- Docusaurus, FastAPI, Neon Postgres, Qdrant, OpenAI Agents
- GitHub Pages deployment
- Vercel optional fallback for frontend
- Better-auth for authentication

Governance adjustments:
- Replace voting system with milestone + PR-based decision model
- Add roles for AI Engineer, Robotics/Content Lead, and DevOps

Also:
- Add proper ratification date
- Increase version to 0.2.0 after amendment
labels: ["constitution", "project-goals", "update"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - None
---

## Prompt

/sp.constitution Update my constitution to align with the following project goals:

Project: Physical AI & Humanoid Robotics Textbook + AI Portal

Mandatory principles to include:
- Spec-Driven Development (Spec-Kit Plus + Gemini CLI)
- AI-integrated textbook with embedded RAG chatbot
- Robotics domain alignment (ROS2, simulation, VLA, humanoids)
- Localization and accessibility: Urdu translation required
- Personalized learning for logged-in users
- Test automation for both backend (FastAPI) and frontend
- Clear branching and PR approval workflow
- Deployment standards (Docusaurus frontend + cloud backend)

Mandatory technologies to define:
- Docusaurus, FastAPI, Neon Postgres, Qdrant, OpenAI Agents
- GitHub Pages deployment
- Vercel optional fallback for frontend
- Better-auth for authentication

Governance adjustments:
- Replace voting system with milestone + PR-based decision model
- Add roles for AI Engineer, Robotics/Content Lead, and DevOps

Also:
- Add proper ratification date
- Increase version to 0.2.0 after amendment

## Response snapshot

Successfully updated the project constitution file to version 0.2.0, incorporating new project goals, principles, technology stack, and governance roles.
New Version: 0.2.0 (Minor version bump due to new principles, technology stack, and governance roles.)
Files for Manual Follow-up:
- .specify/templates/plan-template.md
- .specify/templates/spec-template.md
- .specify/templates/tasks-template.md
- All files in .specify/templates/commands/
- README.md
- docs/quickstart.md
Suggested Commit Message: docs: amend constitution to v0.2.0 (update project goals, principles, tech, and governance)

## Outcome

- ✅ Impact: Successfully updated the project constitution to version 0.2.0, incorporating new project goals, principles, technology stack, and governance roles.
- 🧪 Tests: N/A (no tests were run for this task)
- 📁 Files: Updated `.specify/memory/constitution.md`.
- 🔁 Next prompts: Review and update dependent templates (plan-template, spec-template, tasks-template, command files, README, quickstart docs).
- 🧠 Reflection: The `create-phr.sh` script did not create the directory or the file, necessitating a manual fallback.

## Evaluation notes (flywheel)

- Failure modes observed: Script for PHR creation did not work as expected.
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Investigate `create-phr.sh` script for proper directory creation and error reporting.
