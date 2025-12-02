<!-- Sync Impact Report:
Version change: 0.1.0 -> 0.2.0
Modified principles:
  - Clear Prerequisites -> Spec-Driven Development (Spec-Kit Plus + Gemini CLI)
  - Incremental Development -> AI-integrated textbook with embedded RAG chatbot
  - Test-Driven Development -> Robotics domain alignment (ROS2, simulation, VLA, humanoids)
  - Added: Localization and accessibility: Urdu translation required
  - Added: Personalized learning for logged-in users
  - Added: Test automation for both backend (FastAPI) and frontend
  - Added: Clear branching and PR approval workflow
  - Added: Deployment standards (Docusaurus frontend + cloud backend)
  - Added: Technology Stack
Added sections:
  - 3.4 Roles and Responsibilities
Removed sections:
  - None
Templates requiring updates:
  - .specify/templates/plan-template.md ⚠ pending
  - .specify/templates/spec-template.md ⚠ pending
  - .specify/templates/tasks-template.md ⚠ pending
  - .specify/templates/commands/*.md ⚠ pending
  - README.md ⚠ pending
  - docs/quickstart.md ⚠ pending
Follow-up TODOs:
  - None
-->

# Project Constitution: Physical AI & Humanoid Robotics Textbook + AI Portal

## 1. Introduction

This constitution outlines the core principles, governance, and operating guidelines for the "Physical AI & Humanoid Robotics Textbook + AI Portal" project. It serves as a foundational document for all contributors and stakeholders.

## 2. Core Principles

### 2.1 Spec-Driven Development (Spec-Kit Plus + Gemini CLI)
**Principle:** All development must adhere to a Spec-Driven Development (SDD) methodology, utilizing Spec-Kit Plus and the Gemini CLI for specification, planning, task management, and execution.
**Rationale:** Ensures clarity, traceability, and consistency throughout the development lifecycle, facilitating effective collaboration and predictable outcomes.

### 2.2 AI-integrated textbook with embedded RAG chatbot
**Principle:** The core product is an AI-integrated textbook, featuring an embedded Retrieval Augmented Generation (RAG) chatbot for interactive learning and content exploration.
**Rationale:** Leverages advanced AI capabilities to enhance the educational experience, providing dynamic and personalized access to information within the textbook context.

### 2.3 Robotics domain alignment (ROS2, simulation, VLA, humanoids)
**Principle:** All content, examples, and functionalities must align with the robotics domain, specifically incorporating concepts from ROS2, robotic simulation, Visual-Language-Action (VLA) models, and humanoid robotics.
**Rationale:** Guarantees relevance and depth in the chosen subject matter, providing specialized knowledge and practical application for the target audience.

### 2.4 Localization and accessibility: Urdu translation required
**Principle:** The textbook content must be localized, with an initial mandatory translation into Urdu, and designed for accessibility to cater to a diverse global audience.
**Rationale:** Expands reach and inclusivity, making the educational material available and usable for a broader range of learners.

### 2.5 Personalized learning for logged-in users
**Principle:** Logged-in users will experience personalized learning paths, content recommendations, and progress tracking tailored to their individual needs and learning styles.
**Rationale:** Enhances engagement and effectiveness by adapting the learning experience to each user, optimizing knowledge acquisition and retention.

### 2.6 Test automation for both backend (FastAPI) and frontend
**Principle:** Comprehensive test automation is mandatory for both backend (FastAPI) and frontend components, covering unit, integration, and end-to-end testing.
**Rationale:** Ensures software quality, stability, and reliability, enabling rapid development cycles with confidence and minimizing regressions.

### 2.7 Clear branching and PR approval workflow
**Principle:** A clear, well-defined branching strategy and Pull Request (PR) approval workflow must be followed for all code contributions.
**Rationale:** Maintains code quality, facilitates collaborative development, and ensures proper review and integration of changes into the codebase.

### 2.8 Deployment standards (Docusaurus frontend + cloud backend)
**Principle:** Adherence to defined deployment standards is required, utilizing Docusaurus for frontend hosting and a robust cloud platform for backend services.
**Rationale:** Ensures consistent, reliable, and scalable deployment of the application, maintaining high availability and performance.

### 2.9 Technology Stack
**Principle:** The project will utilize the following core technologies: Docusaurus for frontend, FastAPI for backend, Neon Postgres for the primary database, Qdrant for vector search, and OpenAI Agents for advanced AI capabilities. Deployment will primarily target GitHub Pages for the Docusaurus frontend, with Vercel as an optional fallback. Better-auth will be used for robust authentication.
**Rationale:** Standardizes the technology landscape, leverages established and performant tools, and ensures architectural consistency and maintainability.

## 3. Governance

### 3.1 Amendment Procedure
Amendments to this constitution must follow a formal proposal, review, and approval process, with decisions made through a milestone and Pull Request (PR)-based model, ensuring iterative and transparent governance.

### 3.2 Versioning Policy
This constitution will adhere to semantic versioning (MAJOR.MINOR.PATCH) to reflect changes in governance: MAJOR for breaking changes, MINOR for new principles/sections, and PATCH for minor clarifications.

### 3.3 Compliance Review
Regular reviews will be conducted to ensure ongoing adherence to the principles and guidelines outlined in this constitution, with findings and actions documented.

### 3.4 Roles and Responsibilities
**AI Engineer:** Responsible for the design, development, and integration of AI models and RAG chatbot functionalities, leveraging tools such as OpenAI Agents.
**Robotics/Content Lead:** Oversees the robotics domain content, textbook structure, and educational material accuracy, including localization efforts and alignment with ROS2, simulation, VLA, and humanoid concepts.
**DevOps Engineer:** Manages the deployment pipelines, infrastructure (GitHub Pages, cloud backend), and ensures operational stability and scalability, including Docusaurus, FastAPI, Neon Postgres, Qdrant, and Better-auth deployments.

## 4. Document History

- **Constitution Version:** 0.2.0
- **Ratification Date:** 2025-12-02
- **Last Amended Date:** 2025-12-02
