# HOMEase AI Technical Architecture Plan

This document presents a detailed technical architecture for the HOMEase AI platform, engineered for robust, scalable, and secure deployment **entirely on Google Cloud Platform (GCP)**—**explicitly avoiding Vercel**. The architecture leverages a serverless-first, event-driven approach using the Firebase ecosystem and GCP-native services.

---

## Guiding Principles

- **Serverless First**: Minimize infrastructure management by using managed, auto-scaling services such as Cloud Run and Cloud Functions.
- **Decoupled & Event-Driven**: Employ asynchronous messaging (Google Cloud Pub/Sub) to create a resilient, scalable system where components can evolve independently.
- **Security by Design**: Integrate security at every layer, from frontend middleware and API authorization to granular Firestore security rules.
- **CI/CD Automation**: Automate all testing and deployment pipelines using GitHub Actions for reliability and rapid iteration.
- **GCP Native (No Vercel)**: Fully utilize GCP for hosting, deployment, AI/ML, and operations.

---

## 1. Foundational Cloud Architecture & Deployment

The HOMEase AI platform is built **entirely on Google Cloud Platform** for deep integration between:

- **Frontend**: Next.js (App Router)
- **Backend Services**: Google Cloud Functions
- **Database**: Firestore
- **AI/ML**: Google Gemini, Fal.ai

---

## 1.1 High-Level Architecture Diagrams (C4 Model)

### Level 1: System Context Diagram

This diagram illustrates how the HOMEase AI platform interacts with users and external systems:

## Task Understanding

The HOMEase AI platform requires a **comprehensive technical architecture plan** for a lead generation service focused on home modifications. The plan must address all major layers—**frontend, backend, data, security, and deployment**—and adhere to the following key constraints:

- **Deployment must be on Google Cloud Platform (GCP)**, with **no use of Vercel**.
- The architecture must be **scalable, secure, and modern**, leveraging technologies such as **Next.js 15, Firebase, Google Cloud AI**, and more.
- All documented features must be supported, including **AR assessments, automated lead matching, and real-time communication**.

---

## Execution Strategy

The project will be delivered in **phases**, with a strong emphasis on building a secure and stable foundation before parallelizing feature development. The **first three tasks**—Foundational Architecture, Data Modeling, and Authentication—are **critical prerequisites** and must be completed in order. Once these are in place, API development, asynchronous workflows, and frontend work can proceed in parallel. **DevOps and CI/CD** will be established early and refined throughout the project to ensure reliability and rapid iteration.

---

## Subtasks Overview

Below is a breakdown of the major subtasks, their priorities, required expertise, and dependencies:

### 1. Foundational Architecture & GCP Deployment Strategy

- **Priority:** 1
- **Expertise:** Cloud & DevOps Architect
- **Description:**  
  - Define the complete cloud infrastructure and deployment strategy, **explicitly avoiding Vercel**.
  - Select and justify hosting solutions for the Next.js frontend and serverless backend functions within GCP.
  - Create high-level architecture diagrams (e.g., C4 context/container diagrams) to illustrate system components and their interactions.
- **Dependencies:** None

### 2. Firestore Data Modeling & Security Rules Design

- **Priority:** 2
- **Expertise:** Data Architect / Senior Backend Engineer
- **Description:**  
  - Design a comprehensive NoSQL data schema for Google Firestore.
  - Define all collections (e.g., users, contractors, leads, assessments, chats, reviews), document structures, and relationships (including sub-collections).
  - Design Firestore Security Rules to enforce data access policies based on user roles (homeowner, contractor, admin).
- **Dependencies:** Foundational Architecture & Deployment

### 3. Authentication and Authorization (AuthN/AuthZ) Design

- **Priority:** 3
- **Expertise:** Security Specialist / Senior Backend Engineer
- **Description:**  
  - Detail the end-to-end authentication and authorization flow.
  - Specify integration of NextAuth.js v5 with Firebase Authentication.
  - Define JWT handling (issuance, refresh, secure storage in HTTP-only cookies).
  - Design a Role-Based Access Control (RBAC) system, detailing how user roles and permissions are checked in Next.js Middleware, API endpoints (Firebase Functions), and Firestore Security Rules.
- **Dependencies:** Data Modeling

### 4. Core API and Backend Services Architecture

- **Priority:** 4
- **Expertise:** Senior Backend Engineer
- **Description:**  
  - Define the architecture for all backend services and APIs using TypeScript-based Firebase Functions.
  - Specify RESTful API endpoints (e.g., `POST /api/leads`, `GET /api/assessments/{id}`).
  - Define request/response schemas using Zod for validation.
  - Detail business logic for each function, including Firestore interactions.
  - Structure functions for maintainability and scalability.
- **Dependencies:** Foundational Architecture, Data Modeling, AuthN/AuthZ

### 5. Asynchronous Workflows & AI Integration Plan

- **Priority:** 5
- **Expertise:** AI / Senior Backend Engineer
- **Description:**  
  - Design event-driven workflows for long-running and asynchronous tasks.
  - Detail the use of Google Cloud Pub/Sub to decouple processes.
  - Specify triggers and logic for background Cloud Functions (e.g., AR data processing with Google Gemini, lead matching algorithms, notifications).
  - Include error handling and retry mechanisms for critical background jobs.
- **Dependencies:** API and Backend

### 6. Next.js 15 Frontend Architecture Plan

- **Priority:** 6
- **Expertise:** Senior Frontend Engineer
- **Description:**  
  - Design the complete frontend architecture using Next.js 15 App Router.
  - Define project directory structure, component hierarchy, and the strategy for using React Server Components (RSC) vs. Client Components (`'use client'`).
  - Plan state management, focusing on URL state (nuqs) and real-time data sync with Firestore.
  - Detail implementation of key UI features: AR assessment submission, contractor dashboard, real-time chat.
- **Dependencies:** API and Backend, AuthN/AuthZ

### 7. DevOps, CI/CD, and Observability Plan

- **Priority:** 7
- **Expertise:** DevOps Engineer
- **Description:**  
  - Create a detailed plan for Continuous Integration/Continuous Deployment (CI/CD) and observability.
  - Define the CI/CD pipeline using GitHub Actions to automatically test, build, and deploy the Next.js app to Google Cloud Run and backend services to Firebase Functions/Google Cloud Functions.
  - Establish a strategy for logging, monitoring, and alerting using Google Cloud's operations suite (Cloud Logging, Cloud Monitoring) to ensure platform health and performance.
- **Dependencies:** Foundational Architecture & Deployment

---

## Technical Architecture Plan: HOMEase AI

This document presents a comprehensive technical architecture and deployment strategy for the HOMEase AI platform. The design emphasizes scalability, security, and cost-efficiency, leveraging a **serverless-first** approach on **Google Cloud Platform (GCP)** and the Firebase ecosystem. **Vercel is not used**; all hosting and backend operations are GCP-native.

---

### Guiding Principles

- **Serverless First:** Minimize infrastructure management by using managed, auto-scaling services.
- **Decoupled & Event-Driven:** Employ asynchronous messaging for a resilient, scalable, and independently evolving system.
- **Security by Design:** Integrate security at every layer, from frontend to database.
- **CI/CD Automation:** Automate testing and deployment for reliability and rapid iteration.
- **GCP Native (No Vercel):** Leverage the full GCP ecosystem for hosting, deployment, and operations.

---

## 1. Foundational Cloud Architecture

The HOMEase AI platform is built entirely on Google Cloud Platform, enabling deep integration between:

- **Application Layer:** Next.js (App Router)
- **Backend Services:** Google Cloud Functions
- **Database:** Firestore
- **AI/ML Capabilities:** Google Gemini, Fal.ai

---

### 1.1 High-Level Architecture Diagrams (C4 Model)

#### **Level 1: System Context Diagram**

This diagram illustrates how the HOMEase AI platform interacts with users and external systems:


## Firestore Data Modeling & Security Rules

This section details the NoSQL database schema for Google Firestore and the corresponding security rules that govern data access. The model is designed for query efficiency, scalability, and security, directly supporting the platform's features.

---

### 2.1 Data Model (Schema)

The database consists of several top-level collections. Relationships are managed through document IDs and, where appropriate, sub-collections for tightly-coupled data.

#### **Collections Overview**

| Collection         | Document ID         | Description                                                                                  |
|--------------------|--------------------|----------------------------------------------------------------------------------------------|
| `users`            | `auth.uid`         | Stores core user information and role. The single source of truth for user identity.         |
| `contractors`      | `auth.uid`         | Stores detailed public and private profiles for contractor users. Linked 1:1 with `users`.   |
| `leads`            | auto-generated     | Represents a single homeowner request, from initial AR scan to contractor matching, etc.     |
| `chats`            | auto-generated     | Contains metadata for a conversation thread between a homeowner and a contractor per lead.   |
| `platform_settings`| singleton_doc_name | Global platform configuration (e.g., lead pricing tiers), accessible by admins.              |

### 2.1.1 Contractors Collection
Stores professional details for contractors. Created during contractor onboarding and vetted by an admin.

**Document Path:** `contractors/{userId}` (same userId as in the users collection)

```json
{
  "userId": "auth.uid", // Reference back to the user
  "companyName": "Safe Living Solutions LLC",
  "status": "pending" | "approved" | "rejected",
  "vetting": {
    "licenseVerified": true,
    "insuranceVerified": false,
    "backgroundCheckPassed": true,
    "notes": "Awaiting proof of insurance."
  },
  "contact": {
    "phone": "555-123-4567",
    "email": "contact@safeliving.com",
    "address": "123 Main St, Austin, TX"
  },
  "specializations": ["grab-bars", "ramps", "walk-in-showers"],
  "serviceAreas": ["78701", "78702", "78704"], // ZIP codes or geohashes
  "isCAPSCertified": true,
  "bio": "20 years of experience in home modifications...",
  "avgRating": 4.8,
  "reviewCount": 25,
  "stripeConnectId": "acct_xxxxxxxxxxxxxx" // For receiving payouts
}
```

#### Sub-collection: Reviews
**Path:** `contractors/{userId}/reviews/{reviewId}`

```json
{
  "homeownerId": "auth.uid",
  "homeownerName": "John Smith",
  "leadId": "lead_abc123",
  "rating": 5,
  "comment": "Did an amazing job, very professional and clean.",
  "createdAt": "Timestamp"
}
```

### 2.1.2 Leads Collection
The core collection representing a job request.

**Document Path:** `leads/{leadId}`

```json
{
  "homeownerId": "auth.uid",
  "status": "new" | "matching" | "matched" | "in-progress" | "completed" | "cancelled",
  "urgency": "low" | "medium" | "high",
  "budgetRange": "1000-2500" | "2500-5000" | "5000+", // Optional
  "createdAt": "Timestamp",
  "updatedAt": "Timestamp",
  "matchedContractorId": "auth.uid" | null,
  "matchedAt": "Timestamp" | null,
  "completedAt": "Timestamp" | null,
  "chatId": "chat_xyz789" | null,
  "arAssessment": {
    "rawScanStoragePath": "gs://bucket/scans/{leadId}/scan.usdz",
    "photosStoragePaths": [
      "gs://bucket/photos/{leadId}/photo1.jpg",
      "gs://bucket/photos/{leadId}/photo2.jpg"
    ],
    "aiAnalysis": {
      "status": "pending" | "completed" | "failed",
      "hazards": [
        { "type": "trip_hazard", "location": "rug_edge", "confidence": 0.92 },
        { "type": "no_grab_bar", "location": "shower_wall", "confidence": 0.99 }
      ],
      "recommendations": [
        { "modification": "Install grab bar", "area": "Shower", "estimatedCost": "$250-$400" },
        { "modification": "Replace rug with non-slip mat", "area": "Living Room", "estimatedCost": "$50-$100" }
      ],
      "visualizations": [
        { "type": "after_image", "storagePath": "gs://bucket/viz/{leadId}/shower_after.png" }
      ]
    }
  },
  "scopeOfWork": {
    "title": "Bathroom Safety Upgrade",
    "items": [
      { "description": "Install two 24-inch stainless steel grab bars in shower.", "quantity": 1, "cost": 350 },
      { "description": "Install comfort-height toilet.", "quantity": 1, "cost": 600 }
    ],
    "totalCost": 950,
    "lastUpdatedBy": "contractor" | "homeowner"
  }
}
```

### 2.1.3 Chats Collection
Manages communication threads. A document is created when a lead is matched.

**Document Path:** `chats/{chatId}`

```json
{
  "leadId": "lead_abc123",
  "homeownerId": "auth.uid_of_homeowner",
  "contractorId": "auth.uid_of_contractor",
  "createdAt": "Timestamp",
  "lastMessage": {
    "text": "I can come by tomorrow at 2 PM.",
    "senderId": "auth.uid_of_contractor",
    "timestamp": "Timestamp"
  }
}
```

#### Sub-collection: Messages
**Path:** `chats/{chatId}/messages/{messageId}`

```json
{
  "senderId": "auth.uid",
  "text": "Sounds good, see you then!",
  "timestamp": "Timestamp",
  "attachment": {
    "type": "image",
    "storagePath": "gs://bucket/chat_attachments/{chatId}/image.jpg"
  }
}
```

### 2.2 Firestore Security Rules
```firebase-security-rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    // --- HELPER FUNCTIONS ---
    function isAuthenticated() { return request.auth != null; }
    function isOwner(userId) { return request.auth.uid == userId; }
    function getRole() { return get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role; }
    function isAdmin() { return getRole() == 'admin'; }
    function isHomeowner() { return getRole() == 'homeowner'; }
    function isApprovedContractor() {
      let userRole = getRole();
      if (userRole != 'contractor') return false;
      let contractorProfile = get(/databases/$(database)/documents/contractors/$(request.auth.uid)).data;
      return userRole == 'contractor' && contractorProfile.status == 'approved';
    }

    // --- COLLECTION RULES ---
    match /users/{userId} {
      allow read, update: if isOwner(userId) || isAdmin();
      allow create: if isAuthenticated();
    }

    match /contractors/{userId} {
      allow read: if isAuthenticated();
      allow create: if isOwner(userId);
      allow update: if (isOwner(userId) && !('status' in request.resource.data) && !('vetting' in request.resource.data)) || isAdmin();
      
      match /reviews/{reviewId} {
        allow read: if true;
        allow create: if isAuthenticated() && isHomeowner()
          && exists(/databases/$(database)/documents/leads/$(request.resource.data.leadId))
          && get(/databases/$(database)/documents/leads/$(request.resource.data.leadId)).data.homeownerId == request.auth.uid
          && get(/databases/$(database)/documents/leads/$(request.resource.data.leadId)).data.matchedContractorId == userId
          && get(/databases/$(database)/documents/leads/$(request.resource.data.leadId)).data.status == 'completed';
        allow update, delete: if isAdmin();
      }
    }

    match /leads/{leadId} {
      allow create: if isHomeowner() && request.resource.data.homeownerId == request.auth.uid;
      allow read: if isAdmin() || (isHomeowner() && resource.data.homeownerId == request.auth.uid) || (isApprovedContractor() && resource.data.matchedContractorId == request.auth.uid);
      allow update: if isAdmin() || (isHomeowner() && resource.data.homeownerId == request.auth.uid && resource.data.status != 'completed') || (isApprovedContractor() && resource.data.matchedContractorId == request.auth.uid);
    }

    match /chats/{chatId} {
      function isChatParticipant() { return request.auth.uid == resource.data.homeownerId || request.auth.uid == resource.data.contractorId; }
      allow read, update: if isChatParticipant() || isAdmin();
      allow create: if false;
      
      match /messages/{messageId} {
        function isChatParticipantFromParent() {
          let chatData = get(/databases/$(database)/documents/chats/$(chatId)).data;
          return request.auth.uid == chatData.homeownerId || request.auth.uid == chatData.contractorId;
        }
        allow read, create: if isChatParticipantFromParent() || isAdmin();
        allow update, delete: if isAdmin();
      }
    }
    
    match /platform_settings/{docId} {
        allow read, write: if isAdmin();
    }
  }
}
```


Here is the detailed DevOps, CI/CD, and Observability plan for the HOMEase AI platform, designed for a robust and scalable deployment on Google Cloud Platform.

4. DevOps, CI/CD, and Observability Plan
This section outlines the strategy for automating the build, test, and deployment processes (CI/CD) and for maintaining platform health through comprehensive monitoring, logging, and alerting (Observability). The entire strategy is centered around GitHub and the Google Cloud's operations suite.

4.1. Source Control & Branching Strategy
A GitFlow-inspired branching model will be used to manage code changes and releases:

main branch: Represents the production-ready code. A push or merge to main triggers the production deployment pipeline. This branch is protected, requiring pull request (PR) reviews and passing status checks.
develop branch: Represents the latest development version. A push or merge to develop triggers the staging deployment pipeline. This is the primary integration branch for feature work.
feature/* branches: Created from develop for new features or bug fixes. PRs are made from feature branches back into develop.
4.2. CI/CD Infrastructure Prerequisites: Secure GCP Authentication
To enable GitHub Actions to securely deploy to GCP without storing long-lived credentials, we will use Workload Identity Federation.

Create a GCP Service Account (SA): A dedicated SA will be created for GitHub Actions (e.g., github-actions-deployer@<project-id>.iam.gserviceaccount.com).
Grant Permissions: This SA will be granted necessary IAM roles:
roles/run.admin: To deploy and manage Cloud Run services.
roles/iam.serviceAccountUser: To act as the Cloud Run runtime service account.
roles/artifactregistry.writer: To push Docker images to Artifact Registry.
roles/cloudfunctions.developer: To deploy Cloud Functions.
roles/firebase.admin: For broader Firebase deployments (if needed).
Configure Workload Identity Federation: A Workload Identity Pool and Provider will be set up in GCP to trust identities from the HOMEase AI GitHub repository, mapping specific branches (main, develop) to the GCP Service Account.
This setup allows GitHub Actions to obtain short-lived GCP access tokens automatically, which is the industry best practice for security.

4.3. Continuous Integration & Deployment (CI/CD) Pipelines
We will use GitHub Actions for all CI/CD pipelines. Two primary, independent workflows will be created: one for the Next.js frontend and one for the backend Firebase Functions.

4.3.1. Pipeline 1: Next.js Frontend on Google Cloud Run
This pipeline automates the testing, containerization, and deployment of the Next.js application.

Trigger: On push to develop (deploys to Staging) and main (deploys to Production).

Workflow Steps:

Checkout Code: The repository is checked out.
Authenticate to GCP: The workflow authenticates using the pre-configured Workload Identity Federation.
Setup Node.js & Install Dependencies: Sets up the correct Node.js version and runs npm ci for a clean install.
Lint & Test: Runs static analysis (npm run lint), unit tests, and component tests (npm run test:ci) to ensure code quality. The pipeline fails if this step does not pass.
Build Next.js App: Executes npm run build to create a production-optimized build.
Build & Push Docker Image: Builds a Docker image using a multi-stage Dockerfile and pushes it to Google Artifact Registry. The image is tagged with the Git commit SHA for traceability.
Deploy to Cloud Run: The newly pushed Docker image is deployed as a new revision to the appropriate Cloud Run service (e.g., homease-frontend-staging or homease-frontend-prod).
Sample Dockerfile for Next.js (Standalone Output):

# Dockerfile

# 1. Install dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# 2. Build the application
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# Set build-time environment variables
ARG NEXT_PUBLIC_FIREBASE_API_KEY
ENV NEXT_PUBLIC_FIREBASE_API_KEY=${NEXT_PUBLIC_FIREBASE_API_KEY}
# ... other build-time env vars
RUN npm run build

# 3. Production image
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
# Disable telemetry
ENV NEXT_TELEMETRY_DISABLED 1

# Copy production assets from the builder stage
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/advanced-features/output-file-tracing

USER nextjs

EXPOSE 3000
ENV PORT 3000

CMD ["node", "server.js"]
Sample GitHub Actions Workflow (.github/workflows/deploy-frontend.yml):

name: Deploy Frontend to Cloud Run

on:
  push:
    branches: [ 'main', 'develop' ]
    paths:
      - 'app/**' # Or your frontend directory

env:
  GCP_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  GCP_REGION: 'us-central1'
  SERVICE_NAME: 'homease-frontend'
  GAR_LOCATION: 'us-central1' # Artifact Registry location
  REPOSITORY_NAME: 'homease-images'

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: 'read'
      id-token: 'write'

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Authenticate to Google Cloud
        uses: 'google-github-actions/auth@v2'
        with:
          workload_identity_provider: ${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }}
          service_account: ${{ secrets.GCP_SERVICE_ACCOUNT_EMAIL }}

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install Dependencies
        run: npm ci

      - name: Run Lint and Tests
        run: |
          npm run lint
          npm run test:ci

      - name: Build Next.js App
        run: npm run build
        env:
          NEXT_PUBLIC_FIREBASE_API_KEY: ${{ secrets.NEXT_PUBLIC_FIREBASE_API_KEY_PROD }} # Use different secrets for main/develop

      - name: Setup Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build and Push Docker Image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ env.GAR_LOCATION }}-docker.pkg.dev/${{ env.GCP_PROJECT_ID }}/${{ env.REPOSITORY_NAME }}/${{ env.SERVICE_NAME }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Deploy to Cloud Run
        uses: 'google-github-actions/deploy-cloud-run@v2'
        with:
          service: ${{ env.SERVICE_NAME }}-${{ github.ref_name == 'main' && 'prod' || 'staging' }}
          region: ${{ env.GCP_REGION }}
          image: ${{ env.GAR_LOCATION }}-docker.pkg.dev/${{ env.GCP_PROJECT_ID }}/${{ env.REPOSITORY_NAME }}/${{ env.SERVICE_NAME }}:${{ github.sha }}
          env_vars: |
            # Set runtime environment variables here
            NODE_ENV=production
4.3.2. Pipeline 2: Backend Services on Firebase/Cloud Functions
This pipeline automates the testing and deployment of all backend functions (e.g., leadMatching, arProcessing).

Trigger: On push to develop and main, scoped to the functions/ directory.

Workflow Steps:

Checkout Code: The repository is checked out.
Authenticate to GCP: Uses the same Workload Identity Federation setup.
Setup Node.js & Install Dependencies: Navigates to the functions directory and runs npm ci.
Lint & Test: Runs static analysis and unit/integration tests for the functions.
Deploy to Firebase/Cloud Functions: Uses the Firebase CLI to deploy the functions. The target Firebase project (homease-prod or homease-staging) is selected based on the Git branch.
Sample GitHub Actions Workflow (.github/workflows/deploy-backend.yml):

name: Deploy Backend Functions

on:
  push:
    branches: [ 'main', 'develop' ]
    paths:
      - 'functions/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: 'read'
      id-token: 'write'

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Authenticate to Google Cloud
        uses: 'google-github-actions/auth@v2'
        with:
          workload_identity_provider: ${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }}
          service_account: ${{ secrets.GCP_SERVICE_ACCOUNT_EMAIL }}

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install Firebase CLI
        run: npm install -g firebase-tools

      - name: Install Dependencies
        run: npm ci
        working-directory: ./functions

      - name: Run Lint and Tests
        run: |
          npm run lint
          npm run test
        working-directory: ./functions

      - name: Deploy to Firebase
        env:
          # Select project alias based on branch name
          FIREBASE_PROJECT: ${{ github.ref_name == 'main' && 'homease-prod' || 'homease-staging' }}
        run: |
          firebase deploy --only functions --project $FIREBASE_PROJECT --force
4.4. Observability Strategy
We will use the Google Cloud's operations suite (formerly Stackdriver) for a unified view of platform health.

4.4.1. Logging
Centralized Logging: Cloud Run and Cloud Functions automatically stream all stdout and stderr output to Cloud Logging, providing a centralized log repository.
Structured Logging: All backend services (Cloud Functions) and the Next.js backend will use a logger like pino to output JSON-formatted logs. This enriches logs with machine-readable context (e.g., userId, leadId, traceId) and enables powerful filtering and analysis in the Log Explorer.
Example Log: { "severity": "INFO", "message": "Lead matched successfully", "leadId": "xyz-123", "contractorId": "abc-789" }
Client-Side Logging: For capturing frontend errors and performance data, a dedicated service like Sentry or LogRocket is recommended. Alternatively, a lightweight "logging endpoint" can be created as a Cloud Function to receive errors from the client and write them to Cloud Logging, keeping all logs in one place.
Log Retention: Default retention policies will be used initially, with custom rules configured for specific logs (e.g., audit logs) as needed for compliance.
4.4.2. Monitoring
Platform Metrics: Cloud Monitoring automatically collects essential metrics for all GCP services used:
Cloud Run: Request count, latency (p50, p95, p99), container CPU/Memory utilization, instance count.
Cloud Functions: Invocation count, execution time, memory usage, success/error rate.
Pub/Sub: Number of undelivered/unacknowledged messages (critical for queue health), publish/subscribe request latencies.
Firestore: Document reads/writes/deletes, active connections.
Custom Business Metrics: We will create custom metrics from our Cloud Functions to track key business KPIs. For example, the leadMatching function will publish metrics like leads_matched_count or matching_algorithm_latency.
Dashboards: Custom dashboards will be created in Cloud Monitoring to provide a single-pane-of-glass view of system health, organized by service:
Frontend Dashboard: Displays Cloud Run latency, error rates, and instance counts.
Lead Processing Dashboard: Shows Pub/Sub queue depth, leadMatching function execution time and error rate, and Firestore write operations.
Business KPI Dashboard: Visualizes custom metrics like leads created per hour, contractor sign-ups, and successful payments.
4.4.3. Alerting
Alerting policies will be configured in Cloud Monitoring to proactively notify the engineering team of issues.

Alerting Philosophy: Alerts are categorized by severity. Critical alerts require immediate action (PagerDuty), while warnings are for investigation (Slack). The goal is to create high-signal, low-noise alerts.

Key Alerting Policies:

5xx Error Rate (Cloud Run): CRITICAL - Alert if the percentage of 5xx server errors for the frontend service exceeds 1% over a 5-minute window.
P95 Latency (Cloud Run): WARNING - Alert if the 95th percentile request latency for the frontend exceeds 1500ms.
Function Execution Errors: CRITICAL - Alert if the error rate for a critical function like leadMatching or arProcessing is > 0%.
Pub/Sub Queue Backlog: CRITICAL - Alert if the number of unacknowledged messages in the lead-created topic exceeds 100 for more than 10 minutes (indicates the consumer function is down or failing).
Billing Anomaly: WARNING - Configure a billing alert to notify if costs are projected to exceed the monthly budget.
Notification Channels: Alerts will be routed to:

PagerDuty: For critical, service-impacting alerts.
Slack Channel (#alerts-prod): For all critical and warning-level alerts.
Email: For billing alerts and weekly summary reports.
4.4.4. Distributed Tracing
To diagnose latency issues and understand request flows across multiple services, we will use Google Cloud Trace.

Automatic Tracing: Cloud Run, Cloud Functions, and Pub/Sub have native integration, automatically propagating trace contexts. This provides a baseline trace for requests.
Enhanced Tracing: To get full end-to-end visibility (e.g., from a user click in the Next.js app to a Firestore write in a downstream function), we will instrument the application code using the OpenTelemetry SDKs. This will allow us to create custom spans to measure the duration of specific operations, like calls to the Gemini API or Stripe, providing a detailed flame graph of the entire request lifecycle.

Here is the detailed technical architecture plan for the Authentication and Authorization (AuthN/AuthZ) system for the HOMEase AI platform.

3. Authentication and Authorization (AuthN/AuthZ) Design
This section details the end-to-end strategy for authenticating users and authorizing their access to resources across the HOMEase AI platform. The design employs a multi-layered security model using NextAuth.js v5 and Firebase Authentication to ensure that users can only access data and functionality appropriate for their role.

3.1. Core Components & Technologies
Firebase Authentication: Acts as the primary Identity Provider (IdP). It handles user credential storage, verification (email/password, social providers), and the issuance of short-lived Firebase ID Tokens upon successful login.
NextAuth.js v5 (Auth.js): Serves as the session management layer within the Next.js application. It orchestrates the login flow, securely manages session JWTs via HTTP-only cookies, and exposes session data to both client and server components.
Firestore Database: Stores user application-level data, most critically the role (homeowner, contractor, admin) in the users collection, which is the source of truth for authorization decisions.
Next.js Middleware: Provides the first layer of defense by protecting pages and routes within the Next.js application based on authentication status and user role.
Firebase Functions: The secure backend API layer. Every function call must be authenticated and authorized before executing its business logic.
Firestore Security Rules: The final and most critical layer of defense, enforcing data access policies directly at the database level.
3.2. End-to-End Authentication Flow
The following sequence describes how a user signs in and establishes a secure session with the HOMEase AI platform.

Login Sequence Diagram:

sequenceDiagram
    participant C as Client (Browser)
    participant F as Next.js Frontend
    participant FB_Auth as Firebase Auth Service
    participant NA_BE as NextAuth.js Backend
    participant FS as Firestore

    C->>F: User enters credentials and clicks "Login"
    F->>FB_Auth: signInWithEmailAndPassword(email, pass)
    FB_Auth-->>F: Returns Firebase ID Token (JWT)
    F->>NA_BE: POST /api/auth/callback/credentials with Firebase ID Token
    NA_BE->>FB_Auth: admin.auth().verifyIdToken(firebaseIdToken)
    FB_Auth-->>NA_BE: Verified Token (Decoded Payload with UID)
    NA_BE->>FS: getUserRole(uid) from 'users' collection
    FS-->>NA_BE: Returns user role ('homeowner', 'contractor', etc.)
    NA_BE->>NA_BE: Create NextAuth Session JWT (contains uid, role, email)
    NA_BE-->>C: Set-Cookie: __Secure-next-auth.session-token (HTTP-only)
    C->>F: Session is established. User is logged in.
    F->>F: Can now access session data (useSession() hook)
Step-by-Step Breakdown:

User Login: The user provides their credentials on the Next.js login page. The client-side code uses the Firebase Auth Client SDK to authenticate directly with the Firebase Authentication service.
Firebase ID Token: Upon successful authentication, Firebase Auth returns a short-lived Firebase ID Token to the client.
Initiate NextAuth Session: The client immediately makes a POST request to a custom NextAuth.js credentials provider endpoint (e.g., /api/auth/callback/credentials). The body of this request contains the Firebase ID Token.
Token Verification: The NextAuth.js backend receives the token. It uses the Firebase Admin SDK to verify the signature and payload of the Firebase ID Token. This is a secure server-to-server check that confirms the user's identity.
Role Hydration: Once the token is verified, NextAuth.js extracts the user's uid. It then queries the users collection in Firestore to retrieve the user's assigned role. This critical step happens within the NextAuth.js jwt and session callbacks.
Session JWT Creation & Storage: NextAuth.js creates its own Session JWT. This new token contains the essential session information: uid, role, email, name, etc. This Session JWT is then encrypted and stored in a secure, HTTP-only cookie. This prevents client-side JavaScript (e.g., XSS attacks) from accessing the token.
Session Established: The browser stores the cookie, and the user is now authenticated within the Next.js application. Client and Server Components can access the session data via NextAuth's useSession() hook and auth() server function, respectively.
3.3. Role-Based Access Control (RBAC) Implementation
Authorization is enforced at three distinct layers to provide defense-in-depth.

A. Role Definition:

Roles are defined in the Firestore users/{userId} document as a string field role.

homeowner: Default role for new sign-ups. Can create and manage their own leads.
contractor: Assigned upon sign-up but access is conditional. Full access is granted only when their profile in the contractors collection has status: 'approved'.
admin: Assigned manually in Firestore by a super-admin. Has privileged access to manage users, vet contractors, and oversee platform settings.
B. Layer 1: Next.js Middleware (middleware.ts)

The middleware protects frontend routes before a page is rendered. It inspects the session cookie, retrieves the user's role, and redirects if access is not permitted.

// src/middleware.ts
import { NextResponse } from 'next/server';
import { auth } from '@/auth'; // Your NextAuth.js config

export default auth((req) => {
  const { nextUrl } = req;
  const session = req.auth;
  const isAuthenticated = !!session;
  const userRole = session?.user?.role;

  const isContractorDashboard = nextUrl.pathname.startsWith('/dashboard/contractor');
  const isAdminPanel = nextUrl.pathname.startsWith('/dashboard/admin');
  const isAuthPage = nextUrl.pathname.startsWith('/login') || nextUrl.pathname.startsWith('/signup');

  if (!isAuthenticated && (isContractorDashboard || isAdminPanel)) {
    return NextResponse.redirect(new URL('/login', nextUrl));
  }

  if (isAuthenticated) {
    // Redirect logged-in users from auth pages
    if (isAuthPage) {
      return NextResponse.redirect(new URL('/dashboard', nextUrl));
    }
    // Protect contractor dashboard
    if (isContractorDashboard && userRole !== 'contractor') {
      return NextResponse.redirect(new URL('/unauthorized', nextUrl));
    }
    // Protect admin panel
    if (isAdminPanel && userRole !== 'admin') {
      return NextResponse.redirect(new URL('/unauthorized', nextUrl));
    }
  }
});

// Apply middleware to specific paths
export const config = {
  matcher: ['/dashboard/:path*', '/login', '/signup', '/admin/:path*'],
};
C. Layer 2: API Endpoints (Firebase Functions)

Backend functions must validate every incoming request. Since Firebase Functions operate outside the Next.js runtime, they cannot directly read the NextAuth.js session cookie. Instead, the client must present a valid Firebase ID Token.

Authenticated API Call Flow:

Token Exchange: When a Next.js component needs to call a Firebase Function, it first checks for a NextAuth session using auth().
Custom Token Generation: The Next.js backend (in a Server Action or Route Handler) uses the uid from the session to generate a Firebase Custom Token via the Firebase Admin SDK.
Client Sign-in: This custom token is sent to the client, which uses it to sign in with the Firebase Client SDK (signInWithCustomToken). This securely establishes a Firebase Auth context on the client and provides a standard Firebase ID Token.
API Call: The client now calls the Firebase Function, passing the Firebase ID Token in the Authorization: Bearer <token> header.
Function Verification: The Firebase Function verifies the ID Token using the Admin SDK, extracts the uid, and fetches the user's role from Firestore to perform its authorization checks before executing.
Example Firebase Function (TypeScript):

// functions/src/leads.ts
import * as functions from 'firebase-functions';
import * as admin from 'firebase-admin';

// Initialize admin SDK
admin.initializeApp();
const db = admin.firestore();

export const updateLeadScope = functions.https.onCall(async (data, context) => {
  // 1. Authentication: Throws error if user is not authenticated.
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'The function must be called while authenticated.');
  }

  const { uid } = context.auth;
  const { leadId, newScope } = data;

  // 2. Authorization: Get user role from Firestore
  const userDoc = await db.collection('users').doc(uid).get();
  const userRole = userDoc.data()?.role;

  const leadRef = db.collection('leads').doc(leadId);
  const leadDoc = await leadRef.get();

  if (!leadDoc.exists) {
    throw new functions.https.HttpsError('not-found', 'Lead not found.');
  }

  const leadData = leadDoc.data()!;

  // 3. RBAC Logic: Only the matched contractor or an admin can update the scope
  const isMatchedContractor = userRole === 'contractor' && leadData.matchedContractorId === uid;
  const isAdmin = userRole === 'admin';

  if (!isMatchedContractor && !isAdmin) {
    throw new functions.https.HttpsError('permission-denied', 'You do not have permission to update this lead.');
  }

  // 4. Execute Business Logic
  await leadRef.update({
    scopeOfWork: newScope,
    updatedAt: admin.firestore.FieldValue.serverTimestamp(),
  });

  return { success: true, message: 'Lead scope updated successfully.' };
});
D. Layer 3: Firestore Security Rules

This is the non-negotiable, final gatekeeper of data. These rules are enforced on the server side by Google, guaranteeing data integrity even if the middleware or API layers have a vulnerability. The rules directly reference the user's uid and role from their authenticated token (request.auth).

Key Security Rule Snippets (from data-modeling):

Role-Based Read/Write: A helper function getRole() securely fetches the user's role from the users collection to make decisions.
function getRole() {
  return get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role;
}
function isAdmin() {
  return getRole() == 'admin';
}
Ownership & Role Conditions: Access to a lead is granted based on ownership, role, and the lead's state.
match /leads/{leadId} {
  allow read: if isAdmin()
              // Homeowner can read their own lead
              || (isHomeowner() && resource.data.homeownerId == request.auth.uid)
              // Approved contractor can read a lead they are matched to
              || (isApprovedContractor() && resource.data.matchedContractorId == request.auth.uid);

  allow update: if isAdmin()
                // Matched contractor can update the lead
                || (isApprovedContractor() && resource.data.matchedContractorId == request.auth.uid);
}
Conditional Contractor Access: The isApprovedContractor() function ensures that a user with the contractor role can only perform actions if their profile status is 'approved', adding a crucial business logic check at the database layer.
function isApprovedContractor() {
  if (getRole() != 'contractor') { return false; }
  let contractorProfile = get(/databases/$(database)/documents/contractors/$(request.auth.uid)).data;
  return contractorProfile.status == 'approved';
}
This multi-layered AuthN/AuthZ architecture ensures a secure, scalable, and maintainable system for managing user access across the entire HOMEase AI platform.

Here is the detailed technical architecture plan for the Core API and Backend Services for the HOMEase AI platform.

4. Core API and Backend Services Architecture
This section defines the complete backend architecture using TypeScript-based Firebase Functions. The design prioritizes security, scalability, and maintainability by organizing functions by domain, using strongly-typed schemas with Zod, and leveraging both synchronous (HTTPS) and asynchronous (Pub/Sub) triggers.

4.1. Function Architecture and Structure
All backend logic resides within the functions/ directory of the Firebase project. The structure is organized by feature domain to ensure separation of concerns and scalability.

Recommended Directory Structure:

functions/
├── src/
│   ├── api/
│   │   ├── leads.ts         # Functions for managing leads
│   │   ├── contractors.ts   # Functions for contractor profiles & reviews
│   │   ├── assessments.ts   # Functions for AR assessment processing
│   │   ├── admin.ts         # Functions for admin-only operations
│   │   └── index.ts         # Exports all HTTPS callable functions
│   ├── background/
│   │   ├── matching.ts      # Lead matching background worker
│   │   ├── analysis.ts      # AR analysis background worker
│   │   ├── aggregates.ts    # Functions for updating aggregates (e.g., ratings)
│   │   └── index.ts         # Exports all background functions
│   ├── core/
│   │   ├── firebase.ts      # Firebase admin initialization
│   │   ├── roles.ts         # Role checking helper functions
│   │   └── types.ts         # Zod schemas and TypeScript types
│   └── index.ts             # Main entry point, loads and exports all functions
├── package.json
├── tsconfig.json
└── .eslintrc.js
Key Principles:

Callable Functions (https.onCall): All client-facing API endpoints are implemented as Callable Functions. This is the preferred method over standard HTTPS requests because it automatically deserializes the request body, validates the Firebase Auth token, and provides user context (context.auth).
Zod for Validation: Every function rigorously validates its input against a Zod schema. This prevents malformed data, provides strong type safety, and serves as clear API documentation.
Centralized Role Logic: Authorization checks (e.g., isHomeowner, isApprovedContractor) are handled by reusable helper functions in src/core/roles.ts to ensure consistency.
Asynchronous Offloading: Long-running or non-critical tasks (AI analysis, lead matching) are offloaded to background functions via Google Cloud Pub/Sub to keep API responses fast and prevent timeouts.
4.2. API Endpoint Specification
The following details the primary API endpoints, their schemas, and business logic.

A. Lead Management (/api/leads)
1. Create Lead

Function: createLead
Trigger: https.onCall
HTTP Equivalent: POST /api/leads
Description: A homeowner submits their initial request for a home modification. This creates a lead document and triggers the asynchronous lead matching process.
Authorization: homeowner
Request Schema (Zod):
// src/core/types.ts
const CreateLeadSchema = z.object({
  urgency: z.enum(["low", "medium", "high"]),
  budgetRange: z.string().optional(),
  // Initial AR data reference will be added in a separate step
});
Business Logic:
Verify the caller is an authenticated homeowner.
Validate the request body against CreateLeadSchema.
Create a new document in the leads collection with status: 'new', homeownerId: context.auth.uid, and the provided data.
Publish a message to the lead-created Pub/Sub topic with the leadId.
Return the newly created leadId to the client.
2. Get Lead Details

Function: getLead
Trigger: https.onCall
HTTP Equivalent: GET /api/leads/{leadId}
Description: Retrieves the full details of a specific lead.
Authorization: admin, or the homeowner who owns the lead, or the contractor matched to the lead.
Request Schema (Zod): z.object({ leadId: z.string().nonempty() })
Business Logic:
Validate input.
Fetch the lead document from Firestore.
Perform authorization check: (user.role === 'admin' || lead.homeownerId === uid || lead.matchedContractorId === uid).
If authorized, return the full lead document. Otherwise, throw a permission-denied error.
3. Update Lead Scope of Work

Function: updateLeadScope
Trigger: https.onCall
HTTP Equivalent: PATCH /api/leads/{leadId}/scope
Description: Allows a matched contractor to update the scope-of-work proposal on a lead.
Authorization: approvedContractor (must be matched to the lead), admin.
Request Schema (Zod):
const ScopeItemSchema = z.object({
  description: z.string(),
  quantity: z.number().min(1),
  cost: z.number().min(0),
});
const UpdateLeadScopeSchema = z.object({
  leadId: z.string(),
  scope: z.object({
    title: z.string(),
    items: z.array(ScopeItemSchema),
    totalCost: z.number(),
  }),
});
Business Logic:
Validate input.
Fetch the lead and verify the caller is the matchedContractorId or an admin.
Update the scopeOfWork field and updatedAt timestamp in the lead document.
Return a success confirmation.
B. AR Assessment Management (/api/assessments)
1. Create AR Assessment

Function: createAssessment
Trigger: https.onCall
HTTP Equivalent: POST /api/assessments
Description: The homeowner's app calls this after uploading the raw AR scan data (e.g., USDZ file) to Cloud Storage. This function links the stored file to the lead and triggers the AI analysis.
Authorization: homeowner (must own the lead).
Request Schema (Zod):
const CreateAssessmentSchema = z.object({
  leadId: z.string(),
  rawScanStoragePath: z.string().startsWith('gs://'),
  photosStoragePaths: z.array(z.string().startsWith('gs://')),
});
Business Logic:
Validate input.
Fetch the lead and verify the caller is the homeownerId.
Update the lead document with the storage paths and set arAssessment.aiAnalysis.status to 'pending'.
Publish a message to the ar-assessment-created Pub/Sub topic containing the leadId and storage paths.
Return a success confirmation.
C. Contractor Management (/api/contractors)
1. Update Contractor Profile

Function: updateContractorProfile
Trigger: https.onCall
HTTP Equivalent: PUT /api/contractors/{contractorId}
Description: Allows a contractor to update their own public-facing profile.
Authorization: contractor (can only update their own profile), admin.
Request Schema (Zod):
const UpdateContractorProfileSchema = z.object({
  companyName: z.string(),
  contact: z.object({ phone: z.string(), email: z.string().email() }),
  specializations: z.array(z.string()),
  serviceAreas: z.array(z.string()), // ZIP codes
  bio: z.string().optional(),
});
Business Logic:
Verify the caller is an authenticated contractor.
Validate the request body.
Update the document in the contractors collection where userId matches context.auth.uid.
Crucially, this function CANNOT modify the status or vetting fields. This can only be done by an admin function, enforcing separation of duties.
2. Admin: Update Contractor Status

Function: updateContractorStatus
Trigger: https.onCall
HTTP Equivalent: PATCH /api/admin/contractors/{contractorId}/status
Description: An admin function to approve or reject a contractor's application.
Authorization: admin.
Request Schema (Zod):
const UpdateContractorStatusSchema = z.object({
  contractorId: z.string(),
  status: z.enum(["approved", "rejected"]),
  notes: z.string().optional(), // Admin notes on the decision
});
Business Logic:
Verify the caller is an admin.
Validate input.
Update the specified contractor's document in the contractors collection, setting the status and updating vetting.notes.
(Optional) Trigger an email notification to the contractor about the status change.
4.3. Asynchronous Backend Workflows
These functions are triggered by events within the system and run in the background.

1. Lead Matching Worker

Function: onLeadCreated
Trigger: pubsub.topic('lead-created').onPublish()
Description: Finds suitable contractors for a newly created lead.
Input: Pub/Sub message containing { leadId: string }.
Business Logic:
The function is triggered when a new lead is created.
Reads the leadId from the message.
Updates the lead's status in Firestore to 'matching'.
Fetches lead details (e.g., location, required modifications if available from an initial questionnaire).
Queries the contractors collection for all contractors where status === 'approved'.
Matching Algorithm:
Filter contractors by serviceAreas (e.g., ZIP code).
Filter by specializations that match the work required.
Score remaining contractors based on avgRating, isCAPSCertified, and availability (future feature).
Select the top 3-5 matching contractors.
For this model, we will assign the best match directly. Update the lead document: set status to 'matched', populate matchedContractorId, and create a corresponding chat document for communication.
(Future Enhancement) Instead of direct assignment, add the top matches to a sub-collection on the lead, potentialContractors, and notify them.
2. AR Analysis Worker

Function: onArAssessmentCreated
Trigger: pubsub.topic('ar-assessment-created').onPublish()
Description: Processes AR data with AI to identify hazards and suggest modifications.
Input: Pub/Sub message containing { leadId: string, rawScanStoragePath: string }.
Business Logic:
The function is triggered after AR data is uploaded.
Reads the leadId and storage path from the message.
Call Google Gemini Vision API:
Pass the images/frames from the scan data to the Gemini Vision endpoint.
Use a carefully crafted prompt: "You are an expert in home accessibility for seniors (Aging-in-Place). Analyze this image of a room. Identify all potential hazards like trip risks, lack of support, poor lighting. For each hazard, suggest a specific modification (e.g., 'Install grab bar', 'Replace threshold with a ramp')."
Call Fal.ai (or another image generation service):
For key recommendations (e.g., adding a ramp), send the original image and a prompt to the image generation API: "Show this room but with a wooden wheelchair ramp installed leading up to the door."
Parse the structured JSON response from Gemini and get the storage path for the generated "after" image.
Update the corresponding lead document in Firestore under arAssessment.aiAnalysis with the results: set status to 'completed', and populate the hazards, recommendations, and visualizations fields.
The homeowner's frontend, listening to this document in real-time, will automatically update to show the analysis results.
3. Update Contractor Aggregate Rating

Function: updateContractorRating
Trigger: firestore.document('contractors/{contractorId}/reviews/{reviewId}').onCreate()
Description: When a new review is added, this function recalculates the contractor's average rating and review count.
Business Logic:
Triggered when a new document is created in any reviews sub-collection.
Get the contractorId from the trigger's context.
Run a Firestore Transaction to ensure atomicity: a. Read all reviews for that contractor from the reviews sub-collection. b. Calculate the new avgRating and reviewCount. c. Update the avgRating and reviewCount fields on the parent contractors/{contractorId} document.

Here is the detailed technical architecture plan for the Asynchronous Workflows and AI Integration for the HOMEase AI platform.

5. Asynchronous Workflows & AI Integration
To ensure a responsive user experience and handle computationally intensive tasks, HOMEase AI's architecture relies heavily on a decoupled, event-driven model using Google Cloud Pub/Sub and Cloud Functions. This approach offloads long-running processes like AI analysis and lead matching from the primary API, preventing timeouts and enabling robust, scalable background processing.

5.1. Architectural Overview
The core principle is to separate synchronous, user-facing actions from asynchronous, system-driven workflows. A user action (e.g., creating a lead) triggers a fast API call that validates data, creates an initial record in Firestore, and immediately publishes an event to a Pub/Sub topic. A dedicated background Cloud Function, subscribed to that topic, then performs the heavy lifting.

Visual Flow Diagram:

graph TD
    subgraph Client-Facing API (Firebase Callable Functions)
        A[Next.js Client] -->|1. Call createLead()| B(API: createLead)
        C[Next.js Client] -->|4. Call createAssessment()| D(API: createAssessment)
    end

    subgraph Synchronous Operations
        B -->|2. Writes to Firestore| E[Firestore: leads/{leadId} (status: 'new')]
        B -->|3. Publishes message| F[Pub/Sub Topic: lead-created]
        D -->|5. Writes to Firestore| G[Firestore: leads/{leadId} (arStatus: 'pending')]
        D -->|6. Publishes message| H[Pub/Sub Topic: ar-assessment-created]
    end

    subgraph Asynchronous Backend (Background Cloud Functions)
        F -->|7. Triggers| I[Cloud Function: leadMatchingWorker]
        H -->|10. Triggers| J[Cloud Function: arAnalysisWorker]
    end

    subgraph Background Processing Logic
        I -->|8. Queries| K[Firestore: contractors collection]
        I -->|9. Updates| E
        J -->|11. Calls| L[Google Gemini Vision API]
        J -->|12. Calls| M[Fal.ai Image Gen API]
        J -->|13. Updates| G
    end

    subgraph Real-time Updates
        E -->|Real-time Listener| A
        G -->|Real-time Listener| C
    end

    style F fill:#FF6D00,stroke:#333,stroke-width:2px
    style H fill:#FF6D00,stroke:#333,stroke-width:2px
    style I fill:#4285F4,stroke:#333,stroke-width:2px
    style J fill:#4285F4,stroke:#333,stroke-width:2px
5.2. Pub/Sub Topic Definitions
We will define specific topics for each major asynchronous event to ensure clear separation of concerns.

Topic Name	Message Schema (JSON)	Description
lead-created	{ "leadId": "string" }	Published when a new lead is created. Triggers the contractor matching workflow.
ar-assessment-created	{ "leadId": "string", "imageStoragePaths": ["string"], "scanFilePath": "string" }	Published after AR data is uploaded to Cloud Storage. Triggers the AI analysis and visualization workflow.
notification-dispatch	{ "userId": "string", "type": "string", "data": { ... } }	Published when a notification (email, push) needs to be sent. Triggers the notification worker.
dead-letter-queue (DLQ)	Original message from a failed topic	A centralized topic to receive messages that failed processing after all retry attempts.
5.3. Background Cloud Function Specifications
These functions are the workhorses of the platform, running independently in the background.

1. Lead Matching Worker (leadMatchingWorker)
Trigger: Pub/Sub Topic lead-created

Purpose: To analyze a new lead and find the most suitable, available contractor.

Configuration:

Memory: 512MB
Timeout: 60 seconds
Retry on failure: Enabled (Pub/Sub default exponential backoff)
IAM Permissions:

Firestore: Read access to leads and contractors collections.
Firestore: Write access to the specific lead document being processed.
Core Logic:

Idempotency Check: The function receives the message { "leadId": "..." }. It first reads the lead document from Firestore. If lead.status is not 'new', it logs a warning and exits gracefully. This prevents re-processing if the function is triggered multiple times.
Update Status: Immediately update the lead's status in Firestore to status: 'matching'. This provides real-time feedback to the homeowner.
Fetch Data: Retrieve lead details (location via ZIP code, specializations required from initial questionnaire).
Query Contractors: Fetch all contractors from the contractors collection where status === 'approved' and their serviceAreas array contains the lead's ZIP code.
Scoring Algorithm: For the filtered list, apply a scoring model:
+3 points if isCAPSCertified === true.
+2 points for each matching specialization.
+1 point for every 10 reviews (reviewCount / 10).
Score is multiplied by avgRating (e.g., a 4.5-star rating gives a 4.5x multiplier).
Select Best Match: Identify the contractor with the highest score.
Update Firestore: In a single atomic transaction:
Set lead.status to 'matched'.
Set lead.matchedContractorId to the winning contractor's ID.
Set lead.matchedAt to the current timestamp.
Trigger Notifications: Publish a message to the notification-dispatch topic for both the homeowner and the matched contractor.
Error Handling:

No Match Found: If the scoring algorithm yields no suitable contractors, the function updates the lead status to status: 'matching_failed' and logs an alert for the admin team to review.
Function Crash: If the function fails due to a transient error (e.g., temporary network issue), the Pub/Sub retry policy will automatically re-invoke it. After max retries, the message is sent to the dead-letter-queue for manual inspection.
2. AR Analysis Worker (arAnalysisWorker)
Trigger: Pub/Sub Topic ar-assessment-created

Purpose: To process uploaded AR imagery with Google Gemini for hazard detection and create "after" visualizations.

Configuration:

Memory: 2GB (to handle image data)
Timeout: 300 seconds (5 minutes, to accommodate slow API responses from AI services)
Retry on failure: Enabled
IAM Permissions:

Cloud Storage: Read access to the AR data bucket.
Cloud Storage: Write access to store "after" images.
Firestore: Write access to the specific lead document being processed.
Secret Manager: Access to API keys for Gemini and Fal.ai.
Core Logic:

Idempotency Check: Read the lead document. If lead.arAssessment.aiAnalysis.status is not 'pending', exit.
Update Status: Set lead.arAssessment.aiAnalysis.status to 'processing'.
Call Google Gemini Vision:
Download the images specified in the Pub/Sub message from Cloud Storage.
For each image, make a request to the Gemini Vision Pro model.
System Prompt:
You are an expert Certified Aging-in-Place Specialist (CAPS). Your task is to analyze images of a home and identify accessibility hazards for seniors. For each image, provide a response in structured JSON format. The JSON object should contain an array named 'findings'. Each object in the 'findings' array must have three keys: 'hazard_type' (e.g., 'Trip Hazard', 'Fall Risk', 'Poor Lighting'), 'description' (a clear explanation of the problem, e.g., 'The doorway has a 2-inch threshold that is a trip hazard for walkers'), and 'recommendation' (a specific, actionable modification, e.g., 'Replace the threshold with a zero-profile transition strip').
Call Fal.ai (or other Image Generation AI):
For the top 1-2 most critical recommendations from Gemini (e.g., "Install a walk-in shower"), construct a prompt for Fal.ai's image-to-image model.
Example Prompt: "Using the provided image of a bathroom, realistically replace the existing bathtub with a modern, white-tiled walk-in shower that includes a built-in bench and a chrome grab bar."
Upload the generated "after" image to a public-read path in Cloud Storage.
Consolidate and Update Firestore:
Aggregate all JSON responses from Gemini into a single structured object.
Create a visualizations array containing { recommendation: "...", beforeImageUrl: "...", afterImageUrl: "..." }.
Update the lead document:
Set arAssessment.aiAnalysis.status to 'completed'.
Populate arAssessment.aiAnalysis.results with the consolidated Gemini findings.
Populate arAssessment.aiAnalysis.visualizations with the image generation results.
Error Handling:

AI API Failure: If Gemini or Fal.ai returns an error, the function will log the error, update the lead's arAssessment.aiAnalysis.status to 'error', and store the error message in arAssessment.aiAnalysis.errorMessage. This makes the failure visible to the user and admins.
Dead Lettering: If the function fails repeatedly due to a code bug or persistent external issue, the message will be sent to the DLQ. An alert will be configured on the DLQ to notify developers of critical processing failures.

Here is the solid and detailed technical architecture plan for the HOMEase AI frontend, built with Next.js 15 and designed for deployment on Google Cloud Platform, explicitly avoiding Vercel.

5. Frontend Architecture: Next.js 15 on Google Cloud
This section outlines the complete architecture for the HOMEase AI client-facing application. It is built using the Next.js 15 App Router, optimized for performance, scalability, and a rich, interactive user experience. The architecture is designed to be deployed as a standalone Node.js server on Google Cloud Run, integrating seamlessly with the Firebase and Google Cloud backend services.

5.1. Core Principles & Technology Stack
Framework: Next.js 15 (App Router)
Language: TypeScript
UI Components: Shadcn/UI (built on Radix UI & Tailwind CSS) for accessible, composable components.
State Management:
URL State: nuqs for managing filters, sorting, and pagination state in the URL.
Real-time Data: Firebase Client SDK for live data synchronization with Firestore.
Component State: React useState, useReducer for local UI state.
Session State: NextAuth.js useSession hook for client-side access to user data.
Data Fetching:
Server Components (RSC): Direct data fetching for initial page loads.
Client Components: Firebase Client SDK for real-time listeners and mutations via Firebase Callable Functions.
Styling: Tailwind CSS for utility-first styling.
Deployment Target: Docker container running on Google Cloud Run.
5.2. Project Directory Structure
A feature-driven directory structure will be used to ensure maintainability and clear separation of concerns.

/homease-app
├── public/                  # Static assets (images, fonts)
├── src/
│   ├── app/
│   │   ├── (auth)/          # Group for auth routes (login, signup)
│   │   │   ├── login/
│   │   │   └── signup/
│   │   ├── (dashboard)/     # Group for protected routes
│   │   │   ├── dashboard/
│   │   │   │   ├── homeowner/
│   │   │   │   │   ├── leads/
│   │   │   │   │   │   ├── [leadId]/
│   │   │   │   │   │   │   ├── assess/page.tsx  # AR Assessment Upload
│   │   │   │   │   │   │   └── page.tsx         # Lead Details & Chat
│   │   │   │   │   │   └── page.tsx             # Homeowner Lead List
│   │   │   │   │   └── page.tsx                 # Homeowner Dashboard
│   │   │   │   ├── contractor/
│   │   │   │   │   ├── leads/
│   │   │   │   │   │   ├── [leadId]/page.tsx    # Contractor Lead View
│   │   │   │   │   │   └── page.tsx             # Contractor Lead List
│   │   │   │   │   └── page.tsx                 # Contractor Dashboard
│   │   │   │   └── admin/
│   │   │   │       └── ...
│   │   │   └── layout.tsx       # Shared layout for all dashboards
│   │   ├── api/
│   │   │   └── auth/[...nextauth]/route.ts # NextAuth.js handler
│   │   ├── layout.tsx           # Root layout
│   │   └── page.tsx             # Landing page
│   ├── components/
│   │   ├── ar/                  # AR-related components
│   │   │   ├── ARUploader.tsx
│   │   │   └── ARResultViewer.tsx
│   │   ├── chat/
│   │   │   ├── ChatWindow.tsx
│   │   │   └── ChatMessageInput.tsx
│   │   ├── leads/
│   │   │   ├── LeadCard.tsx
│   │   │   ├── LeadFilterControls.tsx
│   │   │   └── LeadScopeBuilder.tsx
│   │   ├── shared/              # Reusable across features (Header, Footer)
│   │   └── ui/                  # Shadcn/UI components (Button, Card, etc.)
│   ├── hooks/
│   │   ├── useFirestoreQuery.ts # Custom hook for real-time queries
│   │   └── useCallableFunction.ts # Wrapper for calling Firebase Functions
│   ├── lib/
│   │   ├── firebase.ts          # Firebase client SDK initialization
│   │   ├── auth.ts              # NextAuth.js v5 configuration
│   │   └── zod.ts               # Zod schemas for client-side validation
│   └── middleware.ts            # Route protection middleware
├── Dockerfile                   # For building the deployment image
├── next.config.mjs
└── package.json
5.3. Component Strategy: RSC vs. Client Components
The architecture will strategically leverage both React Server Components (RSC) and Client Components to optimize performance and functionality.

Default to Server Components (RSC): All pages (page.tsx), layouts (layout.tsx), and data-display components that do not require user interaction or browser-specific APIs will be RSCs.

Benefit: Faster initial page loads, reduced client-side JavaScript bundle size, and improved SEO.
Example: app/(dashboard)/contractor/leads/page.tsx will be an RSC that fetches the initial list of leads for the contractor, passing the data down to other components.
'use client' for Interactivity: Components will be marked with 'use client' only when necessary.

When to use:
Event Listeners: Components with onClick, onChange, etc. (e.g., <Button>, form inputs).
State and Lifecycle Hooks: Components using useState, useEffect, useContext.
Browser-only APIs: Components accessing window, localStorage, or the Firebase Client SDK.
Custom Hooks: Any component that uses a hook relying on the above (e.g., useSession, useQueryState).
Example: ARUploader.tsx must be a Client Component to handle file selection events and use the Firebase Storage SDK to upload files.
Pattern: Server Component Wrappers: To keep client-side JS minimal, a common pattern will be for an RSC to fetch data and pass it as props to a "dumber" Client Component that handles the interaction.

// app/.../page.tsx (Server Component)
import { ClientComponentWithInteraction } from '@/components/..';
import { getLeadData } from '@/lib/data-access';

export default async function LeadDetailPage({ params }) {
  // 1. Data fetched on the server
  const lead = await getLeadData(params.leadId);

  // 2. Data passed as props to a Client Component
  return <ClientComponentWithInteraction lead={lead} />;
}
5.4. State Management Strategy
State is managed at the most appropriate level to avoid unnecessary complexity and re-renders.

URL State (nuqs): This is the primary method for managing UI state that should be bookmarkable and shareable, such as filters and sorting on the contractor dashboard.

Implementation: The LeadFilterControls.tsx component will use the useQueryState hook from nuqs.
// components/leads/LeadFilterControls.tsx ('use client')
'use client';
import { useQueryState } from 'nuqs';

export function LeadFilterControls() {
  const [status, setStatus] = useQueryState('status'); // e.g., 'new', 'matched'

  return (
    <select value={status || ''} onChange={(e) => setStatus(e.target.value || null)}>
      {/* ...options */}
    </select>
  );
}
When the user selects a new status, nuqs updates the URL search parameters. Next.js automatically re-renders the parent Server Component, which can read the new search params and re-fetch the filtered data.

Real-time Data (Firestore SDK): For data that needs to be live, such as chat messages or lead status updates, the Firebase Client SDK will be used within Client Components to establish real-time listeners.

Implementation: A custom hook useFirestoreQuery will encapsulate the logic.
// hooks/useFirestoreQuery.ts ('use client')
import { useState, useEffect } from 'react';
import { collection, onSnapshot, query } from 'firebase/firestore';
import { db } from '@/lib/firebase';

export function useFirestoreQuery(path) {
  const [data, setData] = useState([]);
  // ...loading and error states

  useEffect(() => {
    const q = query(collection(db, path));
    const unsubscribe = onSnapshot(q, (querySnapshot) => {
      const docs = querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setData(docs);
    });
    return () => unsubscribe(); // Cleanup listener on unmount
  }, [path]);

  return { data, loading, error };
}
Session State (NextAuth.js): User authentication status and role are managed by NextAuth.js and accessed via the useSession() hook in Client Components or the auth() helper in Server Components.

5.5. Key UI Feature Implementation Details
A. AR Assessment Submission Form
Location: app/(dashboard)/homeowner/leads/[leadId]/assess/page.tsx
Primary Component: components/ar/ARUploader.tsx ('use client')
Flow:
The component displays a file input for the AR scan data (e.g., USDZ, photos).
State: Uses useState to track file, uploadProgress, isUploading, and error.
Upload Logic: On file selection, it uses the Firebase Storage Client SDK (uploadBytesResumable) to upload the file directly to a secure path like assessments/{leadId}/{fileName}. The storage rules will ensure only the lead owner can write to this path.
Progress Feedback: The on('state_changed', ...) listener from the upload task updates the uploadProgress state, driving a visual progress bar.
Backend Trigger: Upon successful upload, the component retrieves the storage path (gs://...). It then calls the createAssessment Firebase Callable Function, passing the leadId and storage paths. This is done via a custom hook (useCallableFunction) that handles loading/error states for the API call.
UI Feedback: The UI updates to show "Analysis in Progress..." and redirects the user to their lead details page, where they will see the results in real-time once the backend processing is complete.
B. Contractor Dashboard & Lead List
Location: app/(dashboard)/contractor/leads/page.tsx
Component Breakdown:
page.tsx (RSC): The main server page. It reads search params (status, sortBy) from the URL. It fetches the initial, filtered list of leads for the logged-in contractor and passes it down.
LeadFilterControls.tsx ('use client'): Contains dropdowns and date pickers. Uses nuqs to manage the filter state in the URL, as described above.
LeadList.tsx (RSC): Receives the lead data as a prop and maps over it, rendering a LeadCard.tsx for each lead.
LeadCard.tsx (RSC): A presentational component displaying a summary of a single lead (homeowner location, urgency, AR summary). It includes a <Link> to the full lead detail page.
C. Real-time Chat
Location: Integrated into the lead details page (/leads/[leadId]) for both homeowners and matched contractors.
Primary Component: components/chat/ChatWindow.tsx ('use client')
Flow:
The component receives the leadId as a prop.
Real-time Subscription: It uses the useFirestoreQuery custom hook (or a similar useEffect implementation) to subscribe to the leads/{leadId}/messages sub-collection, ordered by a timestamp field.
Display Messages: The component maps the real-time data from the hook to render the chat history.
Send Messages: A child component, ChatMessageInput.tsx, handles the text input and send button. On submit, it calls a sendChatMessage Firebase Callable Function with the leadId and message text.
Instant Update: The backend function adds the new message to the Firestore sub-collection. The onSnapshot listener in ChatWindow.tsx immediately receives the update and re-renders the message list, providing a seamless real-time experience without any manual re-fetching.