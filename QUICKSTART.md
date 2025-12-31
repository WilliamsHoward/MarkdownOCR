# Quick Start Guide

Get MarkDown OCR up and running in 5 minutes!

## Prerequisites

Before you begin, make sure you have:

- ✅ [Docker](https://www.docker.com/get-started) installed
- ✅ [Ollama](https://ollama.com/) or [LM Studio](https://lmstudio.ai/) installed and running
- ✅ A model downloaded in your LLM provider

## Step 1: Setup Your LLM

### Option A: Using Ollama (Recommended)

```bash
# Install Ollama from https://ollama.com/

# Pull a vision model (RECOMMENDED for best results)
ollama pull llava         # Vision-capable: Best accuracy, handles all content types
ollama pull llava:13b     # Alternative: Even better quality, slower

# OR pull a text-only model (faster but less accurate)
ollama pull llama3        # Text-only: Good balance of speed and quality
ollama pull mistral       # Text-only: Faster, lighter model

# Start Ollama server
ollama serve
```

Verify it's running:
```bash
curl http://localhost:11434/api/tags
```

### Option B: Using LM Studio

1. Download and open [LM Studio](https://lmstudio.ai/)
2. Download a model from the "Discover" tab
3. Go to "Local Server" tab
4. Click "Start Server" (default port: 1234)
5. Select your model from the dropdown

## Step 2: Configure Vision Support (Optional)

Create `backend/.env` to customize settings:

```bash
# Enable vision model (default: true)
USE_VISION_MODEL=true

# Vision model name
VISION_MODEL=llava

# Image quality (DPI) - 150 is recommended
PDF_DPI=150

# Image format
IMAGE_FORMAT=png
```

Or use text-only mode for faster processing:
```bash
USE_VISION_MODEL=false
LLM_MODEL=llama3
```

> **💡 Tip**: Vision mode is enabled by default for better accuracy. See [VISION_GUIDE.md](VISION_GUIDE.md) for details.

## Step 3: Test Your LLM Connection (Optional but Recommended)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python test_llm_connection.py
```

If you see "✅ CONNECTION TEST PASSED!", you're good to go!

## Step 4: Start the Application

### Using Docker (Easiest)

```bash
# From the project root directory
docker-compose up --build
```

Wait for the build to complete (first time takes 2-5 minutes).

### Using Manual Setup

**Terminal 1 - Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Step 5: Access the Application

Open your browser and go to:
- **Web Interface**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Step 6: Convert Your First PDF

1. Click or drag a PDF file to upload
2. Click "Start Conversion"
3. Watch the progress bar as pages are processed
4. Preview the Markdown in the browser
5. Download your converted file

## Common Issues

### "Cannot connect to LLM"

**For Ollama:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve
```

**For LM Studio:**
- Make sure the local server is started in LM Studio
- Verify a model is loaded
- Check port 1234 is not blocked

### Docker Can't Connect to Host LLM

**On Linux**, update `docker-compose.yml`:
```yaml
environment:
  - OLLAMA_BASE_URL=http://172.17.0.1:11434/v1
```

**On macOS/Windows**, the default `host.docker.internal` should work.

### "Model not found"

Make sure you've pulled the model:
```bash
# For Ollama
ollama list                    # List available models
ollama pull llama3             # Pull the model you want

# For LM Studio
# Download the model through the UI first
```

## Next Steps

- Read the full [README.md](README.md) for detailed configuration
- Check [Requirement_Plan.md](Requirement_Plan.md) for feature details
- Adjust `docker-compose.yml` to use different models
- Try different LLM models for better quality or speed

## Tips for Best Results

- 👁️ **Vision Mode**: Enabled by default for best accuracy with all document types
- 📊 **Tables**: Vision models excel at complex table structures
- 💻 **Code**: Excellent at preserving code blocks with syntax highlighting
- 📐 **Math**: Converts formulas to LaTeX notation
- 🖼️ **Images/Diagrams**: Vision models can describe visual elements
- ⚡ **Speed**: Set `USE_VISION_MODEL=false` for 3-5x faster processing
- 🎯 **Quality**: Use `llava:13b` for even better accuracy than default `llava`
- 🔍 **Scanned PDFs**: Vision mode can OCR text from images

## Need Help?

1. Check the [Troubleshooting](README.md#troubleshooting) section
2. Read the [VISION_GUIDE.md](VISION_GUIDE.md) for vision model details
3. Run `python backend/test_llm_connection.py` to diagnose issues
4. View backend logs: `docker-compose logs -f backend`
5. Test the health endpoint: `curl http://localhost:8000/health`

Happy converting! 🎉