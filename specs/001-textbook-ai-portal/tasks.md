---
description: "Task list for feature implementation"
---

# Tasks: Physical AI & Humanoid Robotics Textbook + AI Portal

**Input**: Design documents from `specs/001-textbook-ai-portal/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend and frontend directory structure (`backend/`, `frontend/`)
- [ ] T002 [P] Initialize FastAPI project in `backend/` with dependencies (`fastapi`, `uvicorn`, `pydantic`, `pytest`)
- [ ] T003 [P] Initialize Docusaurus project in `frontend/`
- [ ] T004 [P] Configure linting and formatting for `backend/` (e.g., `black`, `ruff`)
- [ ] T005 [P] Configure linting and formatting for `frontend/` (e.g., `eslint`, `prettier`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [ ] T006 Setup database connection to Neon Postgres in `backend/src/database.py`
- [ ] T007 Setup vector store connection to Qdrant in `backend/src/vector_store.py`
- [ ] T008 Implement user authentication using `better-auth` in `backend/src/auth.py` and integrate with FastAPI
- [ ] T009 Setup basic API routing in `backend/src/main.py`
- [ ] T010 Create base `User` model in `backend/src/models/user.py`
- [ ] T011 [P] Setup frontend services for API communication in `frontend/src/services/api.ts`

---

## Phase 3: User Story 1 - Anonymous User Reads Content (Priority: P1) 🎯 MVP

**Goal**: An anonymous user can browse the textbook content and utilize the RAG chatbot for basic queries without logging in.
**Independent Test**: The book UI can be accessed publicly, content is displayed, and the chatbot responds to general queries from the textbook content.

### Implementation for User Story 1

- [ ] T012 [US1] Create `Chapter` model in `backend/src/models/chapter.py`
- [ ] T013 [US1] Create a service in `backend/src/services/content_service.py` to fetch chapters.
- [ ] T014 [US1] Create API endpoint in `backend/src/api/content.py` to get a list of chapters and a single chapter.
- [ ] T015 [US1] Implement RAG pipeline service in `backend/src/services/rag_service.py` using OpenAI Agents and Qdrant.
- [ ] T016 [US1] Create API endpoint in `backend/src/api/chatbot.py` for chatbot queries.
- [ ] T017 [P] [US1] Create Docusaurus pages in `frontend/src/pages/` for table of contents and chapter view.
- [ ] T018 [P] [US1] Create a chatbot component in `frontend/src/components/Chatbot.tsx`.
- [ ] T019 [US1] Implement frontend logic to fetch and display chapter content in `frontend/src/pages/`.
- [ ] T020 [US1] Implement frontend logic to interact with the chatbot API in `frontend/src/components/Chatbot.tsx`.
- [ ] T021 [P] [US1] Implement UI for language toggle (English/Urdu) and search.

---

## Phase 4: User Story 2 - Registered User Personalizes Experience (Priority: P1)

**Goal**: A registered user can log in, personalize their reading experience, track progress, and utilize advanced chatbot features.
**Independent Test**: A user can register, log in, set preferences, save notes, and their personalized settings persist across sessions.

### Implementation for User Story 2

- [ ] T022 [US2] Extend `User` model in `backend/src/models/user.py` with preferences, progress, notes, and bookmarks.
- [ ] T023 [US2] Create API endpoints in `backend/src/api/users.py` for getting/updating user profile, progress, and notes.
- [ ] T024 [US2] Enhance `rag_service.py` in `backend/src/services/` to handle user-specific context (highlighted text).
- [ ] T025 [P] [US2] Create login and registration pages in `frontend/src/pages/auth/`.
- [ ] T026 [P] [US2] Create a user dashboard page in `frontend/src/pages/dashboard/`.
- [ ] T027 [P] [US2] Implement UI components for progress tracking, notes, and bookmarks in `frontend/src/components/`.
- [ ] T028 [US2] Implement "Ask AI on selection" feature in the frontend.

---

## Phase 5: User Story 3 - Admin Manages Content & Translations (Priority: P2)

**Goal**: An Admin/Content Manager can add, edit, and publish textbook content and manage its translations.
**Independent Test**: An admin can log into a content management interface, create a new chapter in English and provide an Urdu translation, then publish it.

### Implementation for User Story 3

- [ ] T029 [US3] Implement role-based access control (Admin role) in `backend/src/auth.py`.
- [ ] T030 [US3] Create admin-only API endpoints in `backend/src/api/admin.py` for creating, updating, and publishing chapters.
- [ ] T031 [P] [US3] Create an admin dashboard in `frontend/src/pages/admin/`.
- [ ] T032 [P] [US3] Create forms for adding/editing Markdown content for chapters (EN/UR) in `frontend/src/components/admin/`.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T033 [P] Documentation updates in `docs/` for both backend and frontend.
- [ ] T034 Code cleanup and refactoring across the codebase.
- [ ] T035 Performance optimization for API endpoints and frontend rendering.
- [ ] T036 Security hardening (input validation, rate limiting, etc.).
- [ ] T037 Add comprehensive tests for backend (`pytest`) and frontend (`jest`).
