# Funnel

A modern Lead Management System with Django REST Framework backend and React frontend, designed for managing leads through customizable workflow stages.

## 🚀 Features

- **Kanban Board**: Visual lead management with drag-and-drop functionality
- **Custom Workflows**: Create and manage multiple lead workflows with configurable stages
- **Dashboard Analytics**: Real-time statistics and lead distribution charts
- **MongoDB Integration**: Scalable NoSQL database with separate collections
- **Modern UI**: Responsive design built with React 19 and TailwindCSS
- **Type-Safe**: Full TypeScript support on the frontend
- **REST API**: Complete RESTful API with Django REST Framework

## 📋 Tech Stack

### Backend
- **Django 6.0.1** - Web framework
- **Django REST Framework 3.16.1** - API development
- **MongoDB Atlas** - Database
- **Pydantic 2.12.5** - Data validation
- **Python 3.x** - Programming language

### Frontend
- **React 19.2.0** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **TanStack Query 5.90.19** - Data fetching
- **Redux Toolkit 2.11.2** - State management
- **Axios 1.13.2** - HTTP client

## 🛠️ Local Development Setup

### Prerequisites
- Python 3.8+
- Node.js 18+
- MongoDB Atlas account

### Backend Setup

1. Navigate to the Backend directory:
```bash
cd Backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file with your MongoDB URI:
```env
MONGODB_URI=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/?appName=leads
```

5. Run the development server:
```bash
python manage.py runserver
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the Frontend directory:
```bash
cd Frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file:
```env
VITE_API_BASE_URL=http://localhost:8000/api
```

4. Run the development server:
```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

### Add Sample Data (Optional)

```bash
cd Backend
python add_sample_leads.py
```

## 🌐 Deployment

### Deploying Backend to Render

1. Create a new Web Service on [Render](https://render.com)
2. Connect your GitHub repository
3. Configure the service:
   - **Root Directory**: `Backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn lead_crm.wsgi:application`
   - **Environment**: Python 3

4. Add environment variables:
   - `MONGODB_URI`: Your MongoDB Atlas connection string
   - `DJANGO_SECRET_KEY`: Generate a secure secret key
   - `DJANGO_ALLOWED_HOSTS`: Your Render domain (e.g., `your-app.onrender.com`)
   - `CORS_ALLOWED_ORIGINS`: Your frontend URL (e.g., `https://your-app.vercel.app`)

5. Add `requirements.txt` (should already exist):
```txt
django==6.0.1
djangorestframework==3.16.1
django-cors-headers==4.8.0
pydantic==2.12.5
pymongo==4.16.0
python-dotenv==1.1.0
gunicorn==21.2.0
```

6. Deploy and note your backend URL

### Deploying Frontend to Vercel

1. Install Vercel CLI (optional):
```bash
npm i -g vercel
```

2. Deploy via Vercel Dashboard:
   - Go to [Vercel](https://vercel.com)
   - Import your GitHub repository
   - Configure project:
     - **Framework Preset**: Vite
     - **Root Directory**: `Frontend`
     - **Build Command**: `npm run build`
     - **Output Directory**: `dist`

3. Add environment variable:
   - `VITE_API_BASE_URL`: Your Render backend URL (e.g., `https://your-app.onrender.com/api`)

4. Deploy!

### Post-Deployment

1. Update Backend CORS settings in `Backend/lead_crm/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend.vercel.app",
]
```

2. Redeploy backend after updating CORS

## 📁 Project Structure

```
Lead_CRM/
├── Backend/
│   ├── lead_crm/          # Django project settings
│   │   ├── settings.py    # Configuration
│   │   ├── urls.py        # URL routing
│   │   └── database.py    # MongoDB connection
│   ├── leads/             # Main app
│   │   ├── models.py      # Pydantic models
│   │   ├── views.py       # API endpoints
│   │   ├── services.py    # Business logic
│   │   └── serializers.py # DRF serializers
│   ├── manage.py
│   ├── requirements.txt
│   └── add_sample_leads.py
├── Frontend/
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API clients
│   │   ├── store/         # Redux store
│   │   ├── types/         # TypeScript interfaces
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 🔌 API Endpoints

Base URL: `http://localhost:8000/api/`

- `GET /configs/` - List all workflow configurations
- `GET /stages/?config=<config_name>` - List stages for a workflow
- `GET /leads/?config=<config_name>` - List leads with filters
- `POST /leads/` - Create a new lead
- `GET /leads/{uid}/` - Get lead details
- `PUT /leads/{uid}/` - Update a lead
- `DELETE /leads/{uid}/` - Delete a lead

## 📝 Environment Variables

### Backend (.env)
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?appName=leads
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=.onrender.com,localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🐛 Known Issues

- Django migrations warnings can be ignored (SQLite not used)
- Drag-and-drop feature requires frontend implementation

## 📧 Support

For issues or questions, please open an issue on GitHub.

---

Built with ❤️ using Django and React
