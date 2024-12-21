# DRIZDOTPC - Software Download Portal

A modern web application for downloading software, games, and multimedia content.

## Features

- Clean, modern interface
- Multiple categories: Software, Games, Movies, Multimedia, Development
- Search functionality
- Download tracking
- Responsive design
- Compressed assets for fast loading
- Cache system for better performance

## Tech Stack

- Python 3.12
- Flask 3.0.0
- Gunicorn (WSGI server)
- Flask-Compress for asset compression
- Flask-Caching for performance
- Modern HTML5/CSS3

## Deployment

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
gunicorn app:app
```

The application will be available at `http://localhost:8000`

## Environment Variables

- `PORT`: Port number (default: 5000)
- `FLASK_ENV`: Environment (production/development)

## Production Optimizations

- Asset compression enabled
- Long-term caching configured
- Static file serving optimized
- Error handling implemented
- Security headers configured
