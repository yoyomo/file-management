# File Management App

A full-stack file management application with a SvelteKit frontend, FastAPI backend, MongoDB for metadata, and MinIO (S3-compatible) for file storage.

## Features

- Upload files via drag & drop or file picker
- Supported types: images, PDFs, Word docs, videos
- File metadata stored in MongoDB
- Files stored in MinIO (S3-compatible)
- View uploaded files and metadata in a table

## Tech Stack

- **Frontend:** SvelteKit, Vite, TypeScript
- **Backend:** FastAPI (Python)
- **Database:** MongoDB
- **Object Storage:** MinIO (S3 API compatible)
- **Containerization:** Docker & Docker Compose

## Development

### Prerequisites

- Docker & Docker Compose
- GNU Make

### Running the App

1. Clone the repo:
   ```sh
   git clone <repo-url>
   cd file-management
   ```

2. Start all services for development:
   ```sh
   make dev
   ```

3. In a separate terminal tab, follow backend logs:
   ```sh
   make logs
   ```

4. Alternatively, you can run frontend and backend separately:
   ```sh
   make frontend
   make backend
   ```

5. Access the app:
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API: [http://localhost:8000/api/v1](http://localhost:8000/api/v1)
   - MinIO UI: [http://localhost:9001](http://localhost:9001)

## Environment Variables

Set these in your `docker-compose.yml` or `.env`:

- `MONGO_URL` (e.g. `mongodb://mongo:27017/`)
- `MINIO_ENDPOINT` (e.g. `http://minio:9000`)
- `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY`

## License

