import asyncio
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


class OCRService:
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
        self._llm = None

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
                    timeout=60.0,
                    follow_redirects=True,
                )

                self._llm = ChatOpenAI(
                    base_url=base_url,
                    api_key="not-needed",  # Local LLMs usually don't require a real key
                    model=settings.LLM_MODEL,
                    temperature=0,
                    timeout=60,
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

    async def process_pdf(self, task_id: str, file_path: str):
        """
        Processes a PDF file page by page and converts it to Markdown using LLM.
        """
        self.tasks[task_id]["status"] = "processing"
        doc = None

        try:
            # Test LLM connection before starting
            llm = self._get_llm()

            doc = fitz.open(file_path)
            full_markdown = []
            total_pages = len(doc)

            self.tasks[task_id]["total_pages"] = total_pages
            print(f"[OCR Service] Processing {total_pages} pages for task {task_id}")

            previous_context = ""
            for page_num in range(total_pages):
                self.tasks[task_id]["current_page"] = page_num + 1
                page = doc.load_page(page_num)

                # Extract text as a baseline
                text_content = page.get_text("text")

                # Skip empty pages
                if not text_content or text_content.strip() == "":
                    print(f"[OCR Service] Skipping empty page {page_num + 1}")
                    continue

                # In a more advanced version, we would extract images/tables
                # or use a Vision LLM if the local provider supports it.
                # For now, we send the text and structure information to the LLM.

                markdown_page = await self._convert_page_to_markdown(
                    text_content, page_num, previous_context
                )
                full_markdown.append(markdown_page)

                # Keep the last 500 characters of the current page as context for the next
                previous_context = (
                    markdown_page[-500:] if len(markdown_page) > 500 else markdown_page
                )

            # Combine all pages
            final_content = "\n\n".join(full_markdown)

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

    async def _convert_page_to_markdown(
        self, text_content: str, page_num: int, previous_context: str = ""
    ) -> str:
        """
        Uses the LLM to format extracted text into high-quality Markdown,
        considering context from the previous page for continuity.
        """
        system_msg = (
            "You are an expert OCR and document conversion assistant. "
            "Your task is to convert the following text extracted from a PDF page into clean, well-structured Markdown. "
            "Maintain the following:\n"
            "1. Tables: Use standard Markdown table syntax. Preserve columns and headers.\n"
            "2. Code Blocks: Identify code and use proper syntax highlighting (e.g., ```python).\n"
            "3. Math: Use LaTeX for equations if detected.\n"
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
                ("human", f"Context from previous page:\n---\n{previous_context}\n---")
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
