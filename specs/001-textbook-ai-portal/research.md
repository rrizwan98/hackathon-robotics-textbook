# Research Findings: Physical AI & Humanoid Robotics Textbook + AI Portal

**Branch**: `001-textbook-ai-portal` | **Date**: 2025-12-02
**Context**: Phase 0 research to resolve unknowns, identify best practices for dependencies, and integration patterns for various components of the platform.

## 1. Technical Context - Clarifications

No explicit `[NEEDS CLARIFICATION]` markers were identified in the "Technical Context" section of `plan.md`. The initial technical context provided sufficient detail or allowed for reasonable assumptions.

## 2. Best Practices & Integration Patterns

### 2.1 Python (FastAPI) Project Structure Best Practices

*   **Decision**: Adopt a modular, layered project structure.
*   **Rationale**: Promotes maintainability, scalability, and testability. Separates concerns into distinct layers (e.g., routers, services, repositories, models).
*   **Alternatives considered**: Monolithic application (rejected for larger projects), microservices (overkill for initial phase).

### 2.2 JavaScript/TypeScript (Docusaurus/React) Project Structure Best Practices

*   **Decision**: Leverage Docusaurus's inherent structure, augmenting with standard React component organization.
*   **Rationale**: Docusaurus provides a strong foundation for content-heavy sites. Standard React patterns (e.g., `components`, `hooks`, `utils`) ensure maintainability and reusability.
*   **Alternatives considered**: Custom React SPA from scratch (rejected due to overhead of content management features), other static site generators (rejected as Docusaurus fits the "textbook" format well).

### 2.3 Integration Patterns for FastAPI with Docusaurus

*   **Decision**: Implement FastAPI as a standalone backend API service, and Docusaurus as a static frontend consuming these APIs.
*   **Rationale**: Decouples frontend and backend, allowing independent development, deployment, and scaling. Enhances flexibility and technology choices for each layer.
*   **Alternatives considered**: Monolithic (rejected for modularity), server-side rendering with Python (not Docusaurus's strength).

### 2.4 Best Practices for using Neon Postgres (Serverless Database)

*   **Decision**: Utilize Neon's serverless capabilities for cost-efficiency and scalability with a connection pooling strategy.
*   **Rationale**: Automatic scaling and cost optimization are beneficial. Connection pooling is crucial to manage connections in a serverless environment and avoid cold starts.
*   **Alternatives considered**: Self-hosted PostgreSQL (rejected for operational overhead), other serverless databases (Neon offers strong performance and features).

### 2.5 Best Practices for Qdrant (Vector Database) Integration for RAG

*   **Decision**: Integrate Qdrant as a dedicated vector store for RAG, managing embeddings and performing similarity searches.
*   **Rationale**: Qdrant is optimized for vector similarity search, crucial for efficient RAG. Decoupling it from the main database allows specialized scaling.
*   **Alternatives considered**: Using PostgreSQL extensions for vectors (less performant for pure vector search), other vector databases (Qdrant offers good balance of features and performance).

### 2.6 Best Practices for OpenAI Agents and RAG Pipeline Implementation

*   **Decision**: Design a RAG pipeline that includes: content ingestion -> chunking -> embedding generation (using an appropriate embedding model) -> vector storage (Qdrant) -> retrieval -> prompt construction -> LLM generation (using OpenAI Agents) -> response parsing and citation.
*   **Rationale**: A well-defined pipeline ensures robust, context-aware, and citable responses from the chatbot. OpenAI Agents provide powerful LLM capabilities.
*   **Alternatives considered**: Pure LLM generation without RAG (rejected due to hallucination and lack of citations), other RAG frameworks (OpenAI provides good integration).

### 2.7 Best Practices for Better-auth Implementation (User Authentication & Personalization)

*   **Decision**: Integrate Better-auth to handle both OAuth (GitHub, Google) and email/password authentication methods, supporting user profile management and secure token handling.
*   **Rationale**: Better-auth simplifies complex authentication flows and provides robust security features. Supporting both methods offers user flexibility as per the spec.
*   **Alternatives considered**: Custom authentication system (rejected for security and complexity), only one authentication method (rejected by spec).

### 2.8 Strategies for Efficient Content Storage and Retrieval (Markdown, Assets)

*   **Decision**: Store Markdown content and assets in a version-controlled repository (Git) and serve via Docusaurus's static site generation. For larger binary assets or user-uploaded media, consider object storage (e.g., S3-compatible).
*   **Rationale**: Git-based content management integrates well with SDD and version control. Docusaurus optimizes static content delivery. Object storage is scalable and cost-effective for large files.
*   **Alternatives considered**: Database storage for Markdown (rejected for complexity and lack of native versioning), CDN for all assets (will be part of deployment but not primary storage).

### 2.9 Test Automation Strategies for Docusaurus Applications

*   **Decision**: Implement unit/component tests for React components using Jest/React Testing Library, and end-to-end tests for UI interactions and content rendering using Playwright.
*   **Rationale**: Ensures UI functionality, responsiveness, and correct display of multilingual content, including RTL.
*   **Alternatives considered**: Manual testing only (rejected for efficiency and reliability), other E2E frameworks (Playwright offers good browser automation).

### 2.10 Deployment Strategies for Docusaurus on GitHub Pages/Vercel

*   **Decision**: Automate deployment of Docusaurus frontend via GitHub Actions to GitHub Pages or Vercel.
*   **Rationale**: Leverages CI/CD for continuous deployment, ensuring quick updates and reliable hosting. GitHub Pages is free for open source, Vercel offers additional features.
*   **Alternatives considered**: Manual deployment (rejected for efficiency), self-hosting (rejected for complexity).

### 2.11 Deployment Strategies for FastAPI Backend on a Cloud Platform

*   **Decision**: Deploy FastAPI backend as a containerized application (e.g., Docker) on a managed cloud service (e.g., AWS Fargate, Google Cloud Run, Azure Container Apps).
*   **Rationale**: Containerization provides portability and consistency. Managed services offer scalability, reliability, and reduced operational overhead.
*   **Alternatives considered**: Serverless functions (potential cold start issues for some RAG requests), self-managed VMs (rejected for operational burden).

## 3. Unresolved Clarifications

All `[NEEDS CLARIFICATION]` markers from the "Technical Context" in `plan.md` have been addressed either by making informed decisions based on common best practices or by explicitly identifying them as research topics with proposed solutions.
