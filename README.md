# NutriGenie – AI-Powered Personalized Nutrition Agent

## Overview

NutriGenie is an AI-powered personalized nutrition assistant designed to help users make informed dietary decisions through personalized meal planning, nutrition analysis, food logging and intelligent feedback.

The project combines Agentic AI, Retrieval-Augmented Generation (RAG), IBM Granite, IBM watsonx.ai, IBM Bob and IBM Cloud to create a modular and context-aware nutrition solution.

---

## Problem Statement

Good nutrition is essential for maintaining a healthy lifestyle, but individuals often struggle with diet planning, portion control and tracking nutritional intake.

NutriGenie addresses these challenges by providing personalized dietary guidance based on user information, dietary preferences, fitness goals and nutritional requirements.

---

## Objectives

- Generate personalized diet plans
- Retrieve relevant nutrition information using RAG
- Analyze logged meals
- Provide nutritional feedback
- Support preventive nutrition guidance
- Use specialized AI agents for different nutrition tasks
- Provide a foundation for nutrition tracking and visualization

---

## Key Features

### Personalized User Profile
Stores user-specific information such as age, height, weight, activity level, dietary preference, fitness goals and cuisine preferences.

### Personalized Meal Planning
Generates meal recommendations based on the user's profile and nutrition goals.

### Food Logging
Allows users to record food items, quantities and meal types.

### Nutrition Analysis
Analyzes logged meals and provides nutritional insights.

### RAG-Based Knowledge Retrieval
Uses a nutrition knowledge base and vector retrieval to provide relevant information for AI responses.

### Multi-Agent Architecture
The system is organized around specialized agents for different nutrition tasks.

---

## Multi-Agent System

### Nutrition Knowledge Agent
Retrieves and summarizes relevant nutritional information.

### Diet Recommendation Agent
Generates personalized meal plans based on user requirements.

### Health Advisory Agent
Provides preventive nutrition-oriented guidance.

### Food Log & Feedback Agent
Analyzes logged meals and provides nutritional feedback.

---

## Technology Stack

- IBM Bob
- IBM Granite
- IBM watsonx.ai
- IBM Cloud
- Python
- FastAPI
- ChromaDB
- Retrieval-Augmented Generation (RAG)
- HTML
- CSS
- JavaScript

---

## Architecture

User

↓

NutriGenie Frontend

↓

FastAPI Backend

↓

Agent Orchestrator

↓

Specialized Nutrition Agents

↓

RAG / ChromaDB

↓

IBM Granite through watsonx.ai

↓

Personalized Response

---

## Project Structure

NutriGenie/

├── backend/

├── frontend/

├── data/

├── scripts/

├── tests/

├── screenshots/

├── certificates/

├── documentation/

├── requirements.txt

├── .env.example

├── AGENTS.md

└── PROJECT_BLUEPRINT.md

---

## IBM Bob

IBM Bob was used during project planning and implementation to develop the project architecture, implementation structure and application components.

The repository contains screenshots documenting the IBM Bob development process.

---

## Project Outputs

The project demonstrates:

- Personalized user profile
- Personalized meal planning
- Food logging
- Nutrition analysis
- AI-oriented nutrition assistance

Project screenshots are available in:

`screenshots/Project_Output/`

---

## Documentation

The `documentation/` folder contains:

- Project presentation
- Nutrition Agent problem statement

---

## Certificates

The `certificates/` folder contains IBM SkillsBuild learning credentials.

---

## Future Scope

### Wearable Integration

Future versions can integrate smartwatches and fitness trackers to use activity, calorie expenditure, heart-rate and sleep information.

### Voice and Multilingual Support

The system can be extended with voice interaction and support for multiple languages.

### Advanced Food Recognition

Future versions can analyze food images to identify meals and estimate nutritional information.

---

## Security

Sensitive credentials such as IBM Cloud API keys are not included in this repository.

Use `.env.example` as the configuration template and create a local `.env` file for private credentials.

---

## Disclaimer

NutriGenie is an educational AI project and does not replace professional medical or dietary advice.

---

## Author

**Aarush Singh**

NutriGenie – AI-Powered Personalized Nutrition Agent
