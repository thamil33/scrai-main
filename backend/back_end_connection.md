# Backend API Connection Information

This document provides the default connection information for the backend services.

## FastAPI Backend API

*   **URL:** `http://127.0.0.1:8000`
*   **Description:** This is the main endpoint for the backend API. The application is built with FastAPI and run with Uvicorn, which defaults to this address.

## PostgreSQL Database

*   **Host:** `localhost`
*   **Port:** `5432`
*   **Username:** `user`
*   **Password:** `admin`
*   **Database Name:** `scrai_db`
*   **Description:** This is the main database for the application.

## Redis

*   **Host:** `localhost`
*   **Port:** `6379`
*   **Description:** Used for caching and as an event bus.
