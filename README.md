# Learning-Management-System

## Backend

This repository includes a FastAPI backend under `backend/`.

### Setup

1. Create a virtual environment and install requirements:

   ```bash
   python -m venv .venv
   source .venv/Scripts/activate   # PowerShell: .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Start the server:

   ```bash
   uvicorn backend.main:app --reload
   ```

The API will be available at http://127.0.0.1:8000 and the automatic docs at http://127.0.0.1:8000/docs.

### Features

- **Create course**: `POST /courses` with `{title, description}`
- **List courses**: `GET /courses`
- **Enroll student**: `POST /courses/{course_id}/enroll` with `{name, email}`
- **Create assignment**: `POST /courses/{course_id}/assignments` with `{title, description, due_date}`
- **List assignments**: `GET /courses/{course_id}/assignments`
- **Submit assignment**: `POST /assignments/{assignment_id}/submissions` with `{student_id, content}`
- **View submissions**: `GET /assignments/{assignment_id}/submissions`
