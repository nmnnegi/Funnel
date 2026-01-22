# Lead CRM Frontend

Modern React frontend for the Lead CRM system built with Vite, TypeScript, and TailwindCSS.

## Tech Stack

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite 7** - Build tool and dev server
- **TailwindCSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Redux Toolkit** - State management
- **React Query** - Server state management
- **Axios** - HTTP client
- **Lucide React** - Icon library

## Features

- 📊 **Dashboard** - Overview of leads, stages, and analytics
- 👥 **Leads Management** - Kanban board with drag-and-drop functionality
- 📋 **Stages View** - Visual representation of workflow stages
- ⚙️ **Settings** - Workflow configuration and preferences
- 🎨 **Modern UI** - Clean, responsive design with TailwindCSS
- 🔄 **Real-time Updates** - React Query for efficient data fetching
- 📱 **Mobile Responsive** - Works on all device sizes

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running on http://localhost:8000

### Installation

```bash
npm install
npm run dev
```

The application will be available at http://localhost:5173

## Environment Variables

Create a .env file:

```env
VITE_API_URL=http://localhost:8000/api
```

## Project Structure

- **components/** - Reusable UI components
- **pages/** - Application pages
- **services/** - API integration
- **store/** - Redux state management
- **hooks/** - Custom React hooks
- **types/** - TypeScript definitions

## Development

```bash
npm run dev      # Start dev server
npm run build    # Build for production
npm run preview  # Preview production build
```

## License

ISC
