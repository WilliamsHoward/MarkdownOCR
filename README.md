# MarkDown OCR

A web-based OCR system designed to convert PDF documents into high-quality Markdown using local Large Language Models (LLMs) via Ollama or LM Studio.

> **⚡ Quick Start**: New to this project? Check out [QUICKSTART.md](QUICKSTART.md) for a 5-minute setup guide!

## Features

- **🔒 Local AI Processing**: Keep your documents private by using local LLMs.
- **👁️ Vision Model Support**: Process PDF pages as images for enhanced accuracy (NEW!)
  - Better table recognition and complex layouts
  - OCR for scanned documents
  - Image and diagram description
  - Improved formula detection
- **📋 Format Preservation**: Specifically designed to handle:
  - Complex Tables
  - Code Blocks with syntax highlighting
  - Mathematical equations (LaTeX)
  - Section hierarchies and lists
- **🔄 Context-Aware Conversion**: Maintains logical flow and continuity between pages.
- **👀 Real-time Preview**: View the converted Markdown directly in the browser.
- **💾 Downloadable Output**: Export your results as standard Markdown files.

## Project Structure

- `backend/`: FastAPI server for PDF processing and LLM orchestration.
- `frontend/`: Next.js web application with a modern, intuitive interface.

## Prerequisites

- Python 3.9+
- Node.js 18+
- [Ollama](https://ollama.com/) or [LM Studio](https://lmstudio.ai/) running locally
- (Optional) Vision-capable model like `llava` for enhanced processing

## Getting Started

### Prerequisites Check

Before starting, ensure you have:
- ✅ Docker installed (for containerized setup)
- ✅ Ollama or LM Studio running locally
- ✅ A model downloaded (e.g., `ollama pull llama3` or `ollama pull llava` for vision)

**Test your LLM connection first:**
```bash
# Linux/Mac
./test-llm.sh

# Windows
test-llm.bat

# Or manually
cd backend
python test_llm_connection.py
```

### Using Docker (Recommended)

The easiest way to run the application is using Docker Compose:

```bash
docker-compose up --build
```

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000

*Note: The Docker setup is configured to communicate with Ollama/LM Studio running on your host machine via `host.docker.internal`.*

### Manual Setup

#### 1. Setup the Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Start the backend server:
```bash
python app/main.py
```
The API will be available at `http://localhost:8000`.

### 2. Setup the Frontend

```bash
cd frontend
npm install
```

Start the development server:
```bash
npm run dev
```
The web app will be available at `http://localhost:3000`.

### Verify Everything is Working

1. Check the health endpoint: `curl http://localhost:8000/health`
2. Open the web interface: http://localhost:3000
3. Check the API docs: http://localhost:8000/docs

## Configuration

### Environment Variables

Copy the example configuration and customize:
```bash
cp backend/.env.example backend/.env
```

You can configure the LLM provider via environment variables:

- `LLM_PROVIDER`: "ollama" (default) or "lm_studio"
- `OLLAMA_BASE_URL`: Default `http://localhost:11434/v1`
- `LM_STUDIO_BASE_URL`: Default `http://localhost:1234/v1`
- `LLM_MODEL`: The model name to use (e.g., `llama3`, `mistral`, `llava`)

## How it Works

1. **Upload**: User uploads a PDF through the Next.js frontend.
2. **Processing**: The backend processes each page using one of two methods:
   - **Vision Mode** (Default): Renders pages as images and uses a vision-capable LLM to extract all content
   - **Text Mode**: Extracts text using PyMuPDF (faster but less accurate)
3. **LLM Processing**: Each page is sent to the local LLM with a specialized prompt to convert content into structured Markdown, passing context from previous pages to ensure continuity.
4. **Preview & Download**: The user monitors progress in real-time and can preview or download the final Markdown file.

> **💡 New Feature**: Vision model support is now enabled by default! See [VISION_GUIDE.md](VISION_GUIDE.md) for details.

## Troubleshooting

### LLM Connection Issues

If you encounter errors when starting conversion, the backend may not be able to connect to your local LLM:

**Check LLM Status:**
```bash
# Test the health endpoint
curl http://localhost:8000/health
```

**Common Issues:**

1. **Ollama not running:**
   ```bash
   # Start Ollama
   ollama serve
   
   # Verify it's running
   curl http://localhost:11434/api/tags
   ```

2. **Model not available:**
   ```bash
   # Pull the model you want to use
   ollama pull llama3
   ```

3. **Docker connectivity:**
   - On **Linux**, you may need to use `http://172.17.0.1:11434/v1` instead of `host.docker.internal`
   - Update `docker-compose.yml`:
     ```yaml
     environment:
       - OLLAMA_BASE_URL=http://172.17.0.1:11434/v1
     ```

4. **LM Studio not configured:**
   - Open LM Studio
   - Go to the local server tab
   - Start the server on port 1234
   - Load a model

### Viewing Backend Logs

To see detailed logs from the Docker containers:
```bash
docker-compose logs -f backend
```

### Testing Without Docker

If Docker networking is causing issues, you can run the services locally:

**Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## Configuration Options

You can customize the LLM provider and model by editing `docker-compose.yml`:

```yaml
environment:
  - LLM_PROVIDER=ollama          # or "lm_studio"
  - LLM_MODEL=llama3             # Change to your preferred model
  - OLLAMA_BASE_URL=http://host.docker.internal:11434/v1
```

Available models (Ollama examples):
- `llava` - **Recommended**: Vision-capable for best accuracy (7B)
- `llava:13b` - Higher quality vision model (13B)
- `llama3` - Text-only, general purpose, good balance
- `mistral` - Text-only, faster, lighter model
- `codellama` - Text-only, better for documents with code

> **💡 Tip**: Use `llava` for vision processing or `llama3` for fast text-only mode.

## Performance Tips

- **Vision vs Text Mode**: Enable vision for better accuracy, or disable for faster processing
  ```bash
  USE_VISION_MODEL=true   # Better quality (default)
  USE_VISION_MODEL=false  # Faster processing
  ```
- **Adjust Image Quality**: For vision mode, balance quality and speed
  ```bash
  PDF_DPI=150  # Recommended balance
  PDF_DPI=100  # Faster
  PDF_DPI=200  # Higher quality
  ```
- **Use GPU acceleration**: If you have a GPU, configure Ollama/LM Studio to use it for faster processing
- **Adjust model size**: Smaller models (7B) are faster but less accurate than larger ones (13B, 34B)
- **Batch processing**: Process multiple PDFs by uploading them one after another

For detailed vision model configuration, see [VISION_GUIDE.md](VISION_GUIDE.md).