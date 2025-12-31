import asyncio
import base64
import io
import os
import uuid
from typing import Dict, List, Optional

import fitz  # PyMuPDF
import httpx
from app.core.config import settings
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI
from openai import OpenAI
from PIL import Image


class OCRService:
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
        self._llm = None
        self._vision_llm = None

    def _get_llm(self):
        """
        Lazy initialization of LLM client to avoid connection errors on startup.
        """
        if self._llm is None:
            try:
                # Initialize LLM client based on configuration
                base_url = (
                    settings.OLLAMA_BASE_URL
                    if settings.LLM_PROVIDER == "ollama"
                    else settings.LM_STUDIO_BASE_URL
                )

                # Create a custom HTTP client without proxies to avoid compatibility issues
                http_client = httpx.Client(
                    timeout=120.0,  # Increased timeout for vision models
                    follow_redirects=True,
                )

                self._llm = ChatOpenAI(
                    base_url=base_url,
                    api_key="not-needed",  # Local LLMs usually don't require a real key
                    model=settings.LLM_MODEL,
                    temperature=0,
                    timeout=120,
                    max_retries=2,
                    http_client=http_client,
                )
                print(
                    f"[OCR Service] Initialized LLM: {settings.LLM_MODEL} at {base_url}"
                )
            except Exception as e:
                print(f"[OCR Service] Error initializing LLM: {str(e)}")
                raise
        return self._llm

    def _get_vision_llm(self):
        """
        Lazy initialization of Vision LLM client for image-based processing.
        """
        if self._vision_llm is None:
            try:
                base_url = (
                    settings.OLLAMA_BASE_URL
                    if settings.LLM_PROVIDER == "ollama"
                    else settings.LM_STUDIO_BASE_URL
                )

                http_client = httpx.Client(
                    timeout=180.0,  # Even longer timeout for vision processing
                    follow_redirects=True,
                )

                vision_model = settings.VISION_MODEL or settings.LLM_MODEL

                self._vision_llm = ChatOpenAI(
                    base_url=base_url,
                    api_key="not-needed",
                    model=vision_model,
                    temperature=0,
                    timeout=180,
                    max_retries=2,
                    http_client=http_client,
                )
                print(
                    f"[OCR Service] Initialized Vision LLM: {vision_model} at {base_url}"
                )
            except Exception as e:
                print(f"[OCR Service] Error initializing Vision LLM: {str(e)}")
                raise
        return self._vision_llm

    async def process_pdf(self, task_id: str, file_path: str):
        """
        Processes a PDF file page by page and converts it to Markdown using LLM.
        Supports both text extraction and vision-based processing.
        """
        self.tasks[task_id]["status"] = "processing"
        doc = None

        try:
            # Test LLM connection before starting
            if settings.USE_VISION_MODEL:
                llm = self._get_vision_llm()
                print(
                    f"[OCR Service] Using VISION MODEL for processing (DPI: {settings.PDF_DPI})"
                )
            else:
                llm = self._get_llm()
                print(f"[OCR Service] Using TEXT EXTRACTION for processing")

            doc = fitz.open(file_path)
            full_markdown = []
            total_pages = len(doc)

            self.tasks[task_id]["total_pages"] = total_pages
            print(f"[OCR Service] Processing {total_pages} pages for task {task_id}")

            previous_context = ""
            for page_num in range(total_pages):
                self.tasks[task_id]["current_page"] = page_num + 1
                page = doc.load_page(page_num)

                # Choose processing method based on configuration
                if settings.USE_VISION_MODEL:
                    # Vision-based processing: render page as image
                    markdown_page = await self._process_page_with_vision(
                        page, page_num, previous_context
                    )
                else:
                    # Text-based processing: extract text
                    text_content = page.get_text("text")

                    # Skip empty pages
                    if not text_content or text_content.strip() == "":
                        print(f"[OCR Service] Skipping empty page {page_num + 1}")
                        continue

                    markdown_page = await self._convert_page_to_markdown(
                        text_content, page_num, previous_context
                    )

                if markdown_page and markdown_page.strip():
                    full_markdown.append(markdown_page)

                    # Keep the last 500 characters of the current page as context for the next
                    previous_context = (
                        markdown_page[-500:]
                        if len(markdown_page) > 500
                        else markdown_page
                    )

            # Combine all pages
            final_content = "\n\n---\n\n".join(full_markdown)

            # Save output file
            output_filename = f"{task_id}.md"
            output_path = os.path.join(settings.OUTPUT_DIR, output_filename)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(final_content)

            self.tasks[task_id]["status"] = "completed"
            self.tasks[task_id]["output_file"] = output_filename
            print(f"[OCR Service] Task {task_id} completed successfully")

        except Exception as e:
            error_msg = str(e)
            print(f"[OCR Service] Error processing task {task_id}: {error_msg}")
            self.tasks[task_id]["status"] = "failed"
            self.tasks[task_id]["error"] = error_msg
        finally:
            if doc:
                doc.close()

    def _render_page_to_image(self, page, dpi: int = None) -> bytes:
        """
        Renders a PDF page to an image at the specified DPI.

        Args:
            page: PyMuPDF page object
            dpi: Dots per inch for rendering (default from settings)

        Returns:
            Image bytes in the configured format
        """
        if dpi is None:
            dpi = settings.PDF_DPI

        # Calculate zoom factor from DPI (72 DPI is the base)
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)

        # Render page to pixmap
        pix = page.get_pixmap(matrix=mat, alpha=False)

        # Convert to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        img_format = settings.IMAGE_FORMAT.upper()
        if img_format == "JPEG":
            img.save(img_byte_arr, format="JPEG", quality=95, optimize=True)
        else:
            img.save(img_byte_arr, format="PNG", optimize=True)

        img_byte_arr.seek(0)
        return img_byte_arr.getvalue()

    def _encode_image_to_base64(self, image_bytes: bytes) -> str:
        """
        Encodes image bytes to base64 string.

        Args:
            image_bytes: Raw image bytes

        Returns:
            Base64 encoded string
        """
        return base64.b64encode(image_bytes).decode("utf-8")

    async def _process_page_with_vision(
        self, page, page_num: int, previous_context: str = ""
    ) -> str:
        """
        Processes a PDF page using vision model by rendering it as an image.

        Args:
            page: PyMuPDF page object
            page_num: Page number (0-indexed)
            previous_context: Context from previous page for continuity

        Returns:
            Markdown formatted content of the page
        """
        try:
            # Render page to image
            print(f"[OCR Service] Rendering page {page_num + 1} as image...")
            image_bytes = self._render_page_to_image(page)
            image_base64 = self._encode_image_to_base64(image_bytes)

            # Determine image MIME type
            mime_type = (
                "image/jpeg" if settings.IMAGE_FORMAT.lower() == "jpeg" else "image/png"
            )

            # Create vision prompt
            system_msg = (
                "You are an expert document OCR and conversion assistant with vision capabilities. "
                "Your task is to analyze the provided PDF page image and convert ALL content into clean, "
                "well-structured Markdown format.\n\n"
                "IMPORTANT GUIDELINES:\n"
                "1. **Tables**: Convert to standard Markdown table syntax with proper alignment. "
                "Preserve all columns, headers, and cell content.\n"
                "2. **Code Blocks**: Identify code snippets and wrap them in proper fenced code blocks "
                "with language identifiers (e.g., ```python, ```javascript).\n"
                "3. **Mathematical Formulas**: Convert equations to LaTeX syntax using $ for inline "
                "and $$ for display formulas.\n"
                "4. **Structure**: Preserve document hierarchy using headers (# ## ###), lists (- * 1.), "
                "bold (**text**), and italic (*text*).\n"
                "5. **Images/Diagrams**: Describe visual elements that cannot be represented in text, "
                "using format: ![Description of image/diagram]()\n"
                "6. **Layout**: Maintain the logical reading order and flow of the content.\n"
                "7. **Continuity**: Ensure content flows naturally from the previous page context.\n\n"
                "CRITICAL: Extract ALL visible text and content from the image. "
                "Do not summarize or skip any content. "
                "Return ONLY the Markdown content - no conversational text, no explanations."
            )

            messages = []

            # Add system message
            messages.append({"role": "system", "content": system_msg})

            # Add context from previous page if available
            if previous_context:
                context_msg = (
                    f"Context from previous page (for continuity):\n"
                    f"---\n{previous_context}\n---\n\n"
                    f"Now process the current page (page {page_num + 1}), "
                    f"ensuring the content flows naturally from the context above."
                )
                messages.append({"role": "user", "content": context_msg})

            # Add the image with instruction
            image_msg = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Convert this PDF page (page {page_num + 1}) to Markdown format. "
                        "Extract all text, tables, code, formulas, and describe any images or diagrams:",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_base64}",
                            "detail": "high",
                        },
                    },
                ],
            }
            messages.append(image_msg)

            # Call vision LLM
            print(f"[OCR Service] Sending page {page_num + 1} to vision model...")
            llm = self._get_vision_llm()

            # Use the invoke method with proper message format
            response = await asyncio.to_thread(
                llm.invoke,
                messages,
            )

            markdown_content = response.content
            print(
                f"[OCR Service] Successfully processed page {page_num + 1} with vision model "
                f"({len(markdown_content)} characters)"
            )

            return markdown_content

        except Exception as e:
            error_msg = f"Error processing page {page_num + 1} with vision: {str(e)}"
            print(f"[OCR Service] {error_msg}")

            # Fallback to text extraction if vision fails
            print(
                f"[OCR Service] Falling back to text extraction for page {page_num + 1}"
            )
            try:
                text_content = page.get_text("text")
                if text_content and text_content.strip():
                    return await self._convert_page_to_markdown(
                        text_content, page_num, previous_context
                    )
                else:
                    return f"\n\n> [Error processing page {page_num + 1}: {str(e)}]\n\n"
            except Exception as fallback_error:
                return f"\n\n> [Error processing page {page_num + 1}: {str(e)} | Fallback also failed: {str(fallback_error)}]\n\n"

    async def _convert_page_to_markdown(
        self, text_content: str, page_num: int, previous_context: str = ""
    ) -> str:
        """
        Uses the LLM to format extracted text into high-quality Markdown,
        considering context from the previous page for continuity.
        This is the fallback method for text-only processing.
        """
        system_msg = (
            "You are an expert OCR and document conversion assistant. "
            "Your task is to convert the following text extracted from a PDF page into clean, well-structured Markdown. "
            "Maintain the following:\n"
            "1. Tables: Use standard Markdown table syntax. Preserve columns and headers.\n"
            "2. Code Blocks: Identify code and use proper syntax highlighting (e.g., ```python).\n"
            "3. Math: Use LaTeX for equations if detected ($ for inline, $$ for display).\n"
            "4. Structure: Preserve headers (# ##), lists (- 1.), and bold/italic text.\n"
            "5. Continuity: Ensure the flow makes sense for page {page_num}. "
            "Use the provided context from the previous page to maintain consistency in formatting and sentence flow."
            "\n\nIf the text looks like garbage or is empty, return an empty string. "
            "Do not add any conversational text, only return the Markdown content."
        )

        messages = [
            ("system", system_msg),
        ]

        if previous_context:
            messages.append(
                (
                    "human",
                    f"Context from previous page:\n---\n{previous_context}\n---",
                )
            )

        messages.append(("human", "Current page text to convert:\n---\n{text}\n---"))

        prompt = ChatPromptTemplate.from_messages(messages)

        try:
            llm = self._get_llm()
            chain = prompt | llm

            # Running LLM call in a thread to avoid blocking if the library is synchronous
            response = await asyncio.to_thread(
                chain.invoke, {"text": text_content, "page_num": page_num + 1}
            )
            return response.content
        except Exception as e:
            error_msg = f"Error processing page {page_num + 1}: {str(e)}"
            print(f"[OCR Service] {error_msg}")
            # Return the original text with error note on failure
            return f"\n\n> [Error: {str(e)}]\n\n{text_content}"

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        return self.tasks.get(task_id)

    def create_task(self, filename: str) -> str:
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            "id": task_id,
            "filename": filename,
            "status": "pending",
            "current_page": 0,
            "total_pages": 0,
            "output_file": None,
            "error": None,
        }
        return task_id


ocr_service = OCRService()
