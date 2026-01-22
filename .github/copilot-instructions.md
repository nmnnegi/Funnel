# Lead CRM Project - Copilot Instructions

## Project Overview
Lead CRM system with Django REST backend and React frontend.

## Technology Stack

### Backend (Django)
- Django 6.0.1 + Django REST Framework
- MongoDB Atlas with Pydantic models
- Separate collections: leads, stages, configs
- No Django ORM migrations needed

### Frontend (Vite + React)
- React 19 with TypeScript
- TailwindCSS for styling
- React Router for navigation
- Axios for API calls
- React Query for data fetching
- Redux Toolkit for state management

## API Endpoints
Base URL: http://localhost:8000/api/

- `/configs/` - Workflow configurations
- `/stages/` - Workflow stages
- `/leads/` - Lead management

## Development Status
- [x] Backend setup complete
- [x] MongoDB collections configured
- [x] Frontend project scaffolding
- [x] UI components implementation
- [x] API integration
- [x] Redux store setup
- [x] Routing configured
- [x] TypeScript errors fixed
- [x] Development servers running

## Running the Application

### Backend
```bash
cd Backend
source venv/bin/activate
python manage.py runserver
```
Server: http://localhost:8000

### Frontend
```bash
cd Frontend
npm run dev
```
Server: http://localhost:5173

## Key Features Implemented

- Dashboard with analytics and stats
- Kanban board for leads management with drag-and-drop
- Stages visualization
- Settings page with workflow selection
- Modern, responsive UI with TailwindCSS
- Redux state management for client state
- React Query for server state caching
- Full TypeScript support

