# 4-Panel Manga Generator

A web application that generates 4-panel manga using Google Gemini API with character and layout references.

## Features

- Generate 4-panel manga with AI
- Upload reference images for characters and layouts
- Customize each panel with scene descriptions
- Adjust aspect ratio for output images
- View AI thought process
- Retry generation with different options

## Tech Stack

- **Backend:** Python, FastAPI
- **AI:** Google Gemini API (`gemini-3-pro-image-preview`)
- **Frontend:** Vanilla JavaScript, HTML, CSS

## Project Structure

```
project_root/
├── main.py                 # FastAPI server
├── config.py               # Configuration settings
├── models.py               # Data models
├── utils.py                # Utility functions
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── doc/                    # Documentation
│   ├── DESIGN.md           # Detailed design specifications
│   └── initial-plan.me     # Initial project plan
├── static/
│   ├── index.html          # Frontend UI
│   ├── app.js              # Client-side logic
│   ├── style.css           # Styling
│   ├── layout_refs/        # Layout reference images
│   ├── char_refs/          # Character reference images
│   └── outputs/            # Generated images
```

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd 4-panels-manga-generator
```

### 2. Create Python virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your Google Gemini API key:

```
GEMINI_API_KEY=your_actual_api_key_here
```

### 5. Run the application

```bash
python main.py
```

Or use the startup script:

```bash
./start.sh  # On Unix-like systems
# or
start.bat   # On Windows
```

### 6. Open in browser

Navigate to: `http://localhost:8000/static/index.html`

## Documentation

- [Design Specifications](doc/DESIGN.md) - Detailed implementation guide with Gemini API integration
- [Initial Plan](doc/initial-plan.me) - Original project planning document

## Development

### Running the server in development mode

The server runs with auto-reload enabled by default when `DEBUG=True` in `.env`.

### API Endpoints

- `GET /` - Root endpoint
- `GET /api/files/layout` - Get layout reference files
- `GET /api/files/characters` - Get character reference files
- `POST /api/generate` - Generate manga panels
- `GET /health` - Health check

### Adding reference images

Place your reference images in:
- `static/layout_refs/` for layout references
- `static/char_refs/` for character references

## Usage

1. Select aspect ratio for output image
2. Choose or upload layout reference image
3. Add characters with names and reference images
4. Fill in scene descriptions for each of the 4 panels
5. Describe character states and background objects for each panel
6. Click "Generate Image"
7. View results and download generated image

## Current Status

This is a development harness with:
- Complete project structure
- Basic API endpoints (placeholder implementation)
- Full frontend UI
- Configuration management
- Error handling framework

### TODO

- Implement actual Gemini API integration
- Add image upload functionality
- Implement retry mechanisms
- Add streaming support for thought process
- Add tests
- Add logging

## License

MIT
