# 🌧️ IDFLab - Backend API

This repository contains the backend source code for the Intensity-Duration-Frequency (IDF) Analysis Platform. This system serves as the core engine for managing data orchestration, scientific computations, and API interactions.

Built with Python and FastAPI, this backend is designed to efficiently handle computationally intensive climate analyses without compromising API response times, utilizing an asynchronous architecture.

## ✨ Core Responsibilities & Features

 - RESTful API & Security: Exposes secure endpoints for the frontend, protected by JWT (JSON Web Token) authentication.

 - Automated Data Acquisition: Connects directly to official APIs (INMET and CEMADEN) to download raw meteorological time-series data.

 - Scientific Computing Engine: Utilizes libraries like Pandas, SciPy, and Scikit-learn for:

     - Automated gap filling in time series using the Random Forest algorithm.

     - Consistency verification (e.g., Double Mass Curve calculations).

     - Statistical distribution fitting for historical IDF curve generation.

     - Bias correction techniques for future climate scenarios (CLIMBra dataset).

 - Asynchronous Processing: Long-running scientific tasks (like data downloading and gap filling) are delegated to background workers using Celery and Redis, preventing HTTP request blocking and allowing real-time status monitoring.

 - Time-Series Data Management: Stores structured user and station data, along with vast amounts of rainfall observations, in a PostgreSQL database optimized with the TimescaleDB extension.

 - Object Storage Integration: Manages large climate projection datasets and intermediate analysis files using CloudFlare R2.

## 🛠️ Technology Stack

 - Framework: FastAPI (Python)

 - Task Queue & Workers: Celery

 - Message Broker: Redis

 - Database: PostgreSQL + TimescaleDB

 - Object Storage: CloudFlare R2

 - Scientific Libraries: Pandas, SciPy, Scikit-learn

Architectural Context: This backend serves an Angular frontend.

