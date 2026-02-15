# Multi-stage build for both Frontend and Backend

# Stage 1: Backend (Python FastAPI)
FROM python:3.12-slim as backend

WORKDIR /app

# Install dependencies
COPY requirements.txt api/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r api/requirements.txt

# Copy source code
COPY src/ src/
COPY api/ api/

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]


# Stage 2: Frontend (Next.js)
FROM node:18-alpine as builder

WORKDIR /app

# Copy frontend
COPY showcase/package*.json ./
RUN npm ci

COPY showcase/ .

# Build Next.js
RUN npm run build


# Stage 3: Runtime Frontend
FROM node:18-alpine

WORKDIR /app

COPY showcase/package*.json ./
RUN npm ci --only=production

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

EXPOSE 3000

ENV NODE_ENV=production

CMD ["npm", "start"]
