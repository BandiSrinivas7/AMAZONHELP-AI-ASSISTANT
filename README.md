# AmazonHelp AI Assistant

An AI-powered customer support assistant designed to handle common e-commerce support issues such as refunds, returns, deliveries, damaged products, payments, account access, and membership problems.

The project combines a modern Amazon-inspired frontend with a FastAPI backend, machine-learning based intent classification, retrieval-based evidence, and Docker containerization.

## Features

- 🤖 AI-powered customer support assistant
- 🧠 Machine-learning intent classification
- 🔎 Retrieval-based supporting evidence
- 💬 Interactive chat-style frontend
- 📦 Order, delivery, refund, and return support
- 🔐 Account and sign-in issue handling
- ⚠️ Escalation decisions for sensitive cases
- 📊 Intent confidence scoring
- 🐳 Dockerized frontend and backend
- 🚀 FastAPI REST API
- 🌐 Nginx frontend server
- ❤️ Health-check endpoint

## Architecture

```text
                    User
                     │
                     ▼
          ┌─────────────────────┐
          │   AmazonHelp UI     │
          │ HTML / CSS / JS     │
          │      Nginx          │
          └──────────┬──────────┘
                     │
                     │ HTTP
                     ▼
          ┌─────────────────────┐
          │    FastAPI API      │
          │      :8000          │
          └──────────┬──────────┘
                     │
              ┌──────▼──────┐
              │ AI Support  │
              │   Agent     │
              └──────┬──────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
   Intent Classifier       Retrieval
          │                     │
          └──────────┬──────────┘
                     ▼
             Support Decision
                     │
                     ▼
              Draft Response
