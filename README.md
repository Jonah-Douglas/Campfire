# Campfire - Backend

## Spark Connections Through Shared Experiences

Campfire API is a backend service for an event aggregation and exploration application. The primary goal is to help users discover events, connect with others based on shared event interests, and facilitate communication around those events.

**Core MVP Vision:**
*   Users can register and authenticate.
*   Users can create new events.
*   The system can also source and display events from other platforms (future enhancement).
*   Users can express interest or "match" with events.
*   Upon matching with an event, users are entered into a group messaging channel specific to that event.
*   Users can manage their profiles and application settings.
*   Users can manage a friends list to facilitate event invitations and joint event creation.

**Project Lead:** Jonah Douglas

---

## Table of Contents

*   [Features](#features)
*   [Tech Stack](#tech-stack)
*   [Project Structure](#project-structure)
*   [Getting Started](#getting-started)
    *   [Prerequisites](#prerequisites)
    *   [Installation & Environment Setup](#installation--environment-setup)
    *   [Database Setup](#database-setup)
    *   [Running the Application](#running-the-application)
*   [API Documentation](#api-documentation)
*   [Running Tests](#running-tests)
*   [Roadmap & Future Enhancements](#roadmap--future-enhancements)
*   [Contributing](#contributing) (Optional - if you plan for this)

---

## Features

### Current & In-Progress:
*   **User Management:** Registration, login (OTP-based), profile management, user settings (dark mode, preferences).
*   **Authentication & Authorization:** Secure JWT-based authentication (access and refresh tokens), OTP verification for login/registration.
*   **Event Management (Basic):**
    *   User creation of events.
    *   (Foundation for event discovery and details).
*   **Friendship/Connections System:**
    *   Ability for users to send, accept, and manage friend requests.
    *   Viewing friends lists.
*   **API Standards:** Defined standards for consistency (see `API_Standards.txt`).

### Planned for MVP:
*   **Event Matching:** Logic for users to indicate interest in events.
*   **Event-Based Group Messaging Integration:** Placeholder/setup for creating messaging groups for matched events (actual messaging service TBD or via external integration).
*   **Event Invitations:** Allow users to invite friends to events.
*   **Joint Event Creation:** Allow friends to create events together.
*   **Mutual Friends Viewing:** Ability to see mutual friends with other users.

---

## Tech Stack

*   **Framework:** FastAPI
*   **Database:** PostgreSQL
*   **ORM:** SQLAlchemy (with Pydantic for data validation/serialization)
*   **Migrations:** Alembic
*   **Authentication:** OAuth2 with JWTs, Passlib for hashing
*   **Environment Management:** Python `venv`
*   **Linting/Formatting:** (e.g., Flake8, Black, isort - *add these if you use them*)
*   **Testing:** Pytest (Planned)
*   **Deployment (Planned):** Docker, AWS (e.g., ECS, RDS)

---

## Project Structure

The project follows a feature-based organization for modularity and clarity:

project_root/<br>
├── app/<br>
│&emsp;├── auth/                     # Feature: Authentication<br>
│&emsp;│&emsp;├── api/               # FastAPI routes for auth<br>
│&emsp;│&emsp;│&emsp;&nbsp;└── routes_auth.py<br>
│&emsp;│&emsp;├── models/               # FastAPI Models for auth<br>
│&emsp;│&emsp;│&emsp;&nbsp;└── pending_otp.py<br>
│&emsp;│&emsp;├── repositories/         # FastAPI DL for auth<br>
│&emsp;│&emsp;│&emsp;&nbsp;└── pending_otps_repository.py<br>
│&emsp;│&emsp;├── schema/               # FastAPI Schema for auth<br>
│&emsp;│&emsp;│&emsp;&nbsp;└── pending_otp.py<br>
│&emsp;│&emsp;├── services/             # FastAPI BL for auth<br>
│&emsp;│&emsp;│&emsp;&nbsp;└── pending_otp.py<br>
│&emsp;│&emsp;└── dependencies.py       # Pydantic schemas for auth<br>
│&emsp;│<br>
│&emsp;# ... other feature folders ...<br>
│&emsp;│<br>
│&emsp;├── core/                     # SHARED: Global configuration and security utilities<br>
│&emsp;└── db/                       # SHARED: Database setup and base definitions<br>
│<br>
├── alembic/                      # Alembic migrations (manages all models that use app.db.base.Base)<br>
│&emsp;└── versions/<br>
├── tests/                        # Top-level tests directory, mirrors app structure<br>
│&emsp;├── auth/...<br>
│&emsp;└── users/...<br>
│<br>
├── requirements.in<br>
├── requirements.txt<br>
└── README.md<br>

---

## Roadmap & Future Enhancements

*   **MVP Completion:**
    *   [X] User Auth
    *   [X] User Profiles
    *   [ ] Full Event Matching Logic
    *   [ ] Event-Based Group Messaging Integration (Core functionality)
    *   [ ] Event Invitations
    *   [ ] Joint Event Creation
    *   [ ] Mutual Friends Viewing
*   **Post-MVP / Future:**
    *   [ ] Real-time notifications (e.g., WebSockets for friend requests, event updates)
    *   [ ] Advanced event filtering and search (location-based, categories, tags)
    *   [ ] System-sourced events (scraping/API integration from other platforms)
    *   [ ] User reviews and ratings for events/organizers
    *   [ ] Calendar integration
    *   [ ] Admin panel for moderation and management
    *   [ ] Comprehensive test suite
    *   [ ] Dockerization for easier deployment and development consistency
    *   [ ] CI/CD pipeline setup
    *   [ ] Deployment to AWS

---

## Contributing

Currently, this is a solo project. However, if you are interested in contributing in the future, feel free to reach out.

---

This `README.md` should be a living document. Please update it as the project evolves, new features are added, or setup instructions change.
