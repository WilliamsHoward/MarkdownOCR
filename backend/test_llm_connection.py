#!/usr/bin/env python3
"""
LLM Connection Test Script
Tests connectivity to Ollama or LM Studio before running the full application.
Supports both text and vision model testing.
"""

import base64
import io
import os
import sys
from typing import Optional

try:
    from langchain.prompts import ChatPromptTemplate
    from langchain_openai import ChatOpenAI
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Error: Required packages not installed.")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)


def create_test_image() -> str:
    """
    Creates a simple test image with text for vision model testing.

    Returns:
        Base64 encoded PNG image
    """
    # Create a simple image with text
    img = Image.new("RGB", (800, 400), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Add text to the image
    text = "Vision Model Test\n\nThis is a test image to verify\nvision model capabilities.\n\n✓ If you can read this,\n  vision processing works!"

    # Use default font
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
    except:
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24
            )
        except:
            font = ImageFont.load_default()

    # Draw text
    draw.text((50, 50), text, fill=(0, 0, 0), font=font)

    # Convert to base64
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    return base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")


def test_vision_model(
    provider: str = "ollama",
    model: str = "llava",
    ollama_url: str = "http://localhost:11434/v1",
    lm_studio_url: str = "http://localhost:1234/v1",
) -> bool:
    """
    Test connection to a vision-capable LLM.

    Args:
        provider: "ollama" or "lm_studio"
        model: Vision model name to test
        ollama_url: URL for Ollama API
        lm_studio_url: URL for LM Studio API

    Returns:
        True if connection successful, False otherwise
    """
    base_url = ollama_url if provider == "ollama" else lm_studio_url

    print(f"\n{'=' * 60}")
    print(f"Testing {provider.upper()} VISION Model Connection")
    print(f"{'=' * 60}")
    print(f"Provider: {provider}")
    print(f"Model: {model}")
    print(f"Base URL: {base_url}")
    print(f"{'=' * 60}\n")

    try:
        # Initialize the LLM client
        print("🔄 Initializing Vision LLM client...")
        llm = ChatOpenAI(
            base_url=base_url,
            api_key="not-needed",
            model_name=model,
            temperature=0,
            timeout=60,
            max_retries=2,
        )
        print("✅ Vision LLM client initialized successfully\n")

        # Create test image
        print("🔄 Creating test image...")
        image_base64 = create_test_image()
        print("✅ Test image created\n")

        # Test with a vision prompt
        print("🔄 Sending test image to vision model...")

        messages = [
            {
                "role": "system",
                "content": "You are a helpful vision assistant. Describe what you see in the image.",
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What text do you see in this image? Reply with the exact text you can read.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}",
                            "detail": "high",
                        },
                    },
                ],
            },
        ]

        response = llm.invoke(messages)

        print("✅ Received response from Vision LLM\n")
        print(f"Response: {response.content}\n")

        print(f"{'=' * 60}")
        print("✅ VISION MODEL CONNECTION TEST PASSED!")
        print(f"{'=' * 60}\n")
        print(f"Your {provider} vision model setup is working correctly.")
        print(f"You can now use vision-based PDF processing.\n")

        return True

    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)

        print(f"❌ VISION MODEL CONNECTION TEST FAILED!\n")
        print(f"Error Type: {error_type}")
        print(f"Error Message: {error_msg}\n")

        print(f"{'=' * 60}")
        print("TROUBLESHOOTING STEPS:")
        print(f"{'=' * 60}\n")

        if provider == "ollama":
            print("For Ollama Vision Models:")
            print("  1. Make sure you're using a vision-capable model:")
            print("     ollama pull llava")
            print("     ollama pull llava:13b")
            print("     ollama pull bakllava")
            print(f"\n  2. Verify the model supports vision:")
            print("     ollama show --modelfile llava\n")
            print("  3. List available models:")
            print("     ollama list\n")
        else:
            print("For LM Studio Vision Models:")
            print(
                "  1. Download a vision-capable model (look for 'vision' or 'llava' in the name)"
            )
            print("  2. Load the vision model in LM Studio")
            print("  3. Ensure the local server is configured for vision API")
            print("  4. Some models may not support the vision API format\n")

        print("Note: Vision models require more resources than text-only models.")
        print("If vision fails, the system will fallback to text extraction.\n")

        return False


def test_llm_connection(
    provider: str = "ollama",
    model: str = "llama3",
    ollama_url: str = "http://localhost:11434/v1",
    lm_studio_url: str = "http://localhost:1234/v1",
) -> bool:
    """
    Test connection to the specified LLM provider.

    Args:
        provider: "ollama" or "lm_studio"
        model: Model name to test
        ollama_url: URL for Ollama API
        lm_studio_url: URL for LM Studio API

    Returns:
        True if connection successful, False otherwise
    """
    base_url = ollama_url if provider == "ollama" else lm_studio_url

    print(f"\n{'=' * 60}")
    print(f"Testing {provider.upper()} Connection")
    print(f"{'=' * 60}")
    print(f"Provider: {provider}")
    print(f"Model: {model}")
    print(f"Base URL: {base_url}")
    print(f"{'=' * 60}\n")

    try:
        # Initialize the LLM client
        print("🔄 Initializing LLM client...")
        llm = ChatOpenAI(
            base_url=base_url,
            api_key="not-needed",
            model_name=model,
            temperature=0,
            timeout=30,
            max_retries=2,
        )
        print("✅ LLM client initialized successfully\n")

        # Test with a simple prompt
        print("🔄 Sending test prompt...")
        test_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful assistant. Respond with exactly: 'Connection successful!'",
                ),
                ("human", "Test connection"),
            ]
        )

        chain = test_prompt | llm
        response = chain.invoke({})

        print("✅ Received response from LLM\n")
        print(f"Response: {response.content}\n")

        print(f"{'=' * 60}")
        print("✅ CONNECTION TEST PASSED!")
        print(f"{'=' * 60}\n")
        print(f"Your {provider} setup is working correctly.")
        print(f"You can now run the application with this configuration.\n")

        return True

    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)

        print(f"❌ CONNECTION TEST FAILED!\n")
        print(f"Error Type: {error_type}")
        print(f"Error Message: {error_msg}\n")

        print(f"{'=' * 60}")
        print("TROUBLESHOOTING STEPS:")
        print(f"{'=' * 60}\n")

        if provider == "ollama":
            print("For Ollama:")
            print("  1. Check if Ollama is running:")
            print("     curl http://localhost:11434/api/tags\n")
            print("  2. If not running, start it:")
            print("     ollama serve\n")
            print(f"  3. Pull the model if not available:")
            print(f"     ollama pull {model}\n")
            print("  4. List available models:")
            print("     ollama list\n")
        else:
            print("For LM Studio:")
            print("  1. Open LM Studio application")
            print("  2. Go to the 'Local Server' tab")
            print("  3. Click 'Start Server' (port 1234)")
            print("  4. Load a model from your library")
            print("  5. Verify server is running at http://localhost:1234\n")

        print("If running in Docker:")
        print("  - On macOS/Windows: Use host.docker.internal instead of localhost")
        print("  - On Linux: Use 172.17.0.1 instead of localhost")
        print(f"  - Example: http://host.docker.internal:11434/v1\n")

        return False


def main():
    """Main function to run LLM connection tests."""

    # Read from environment or use defaults
    provider = os.getenv("LLM_PROVIDER", "ollama")
    model = os.getenv("LLM_MODEL", "llama3")
    vision_model = os.getenv("VISION_MODEL", "llava")
    use_vision = os.getenv("USE_VISION_MODEL", "true").lower() == "true"
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    lm_studio_url = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")

    print("\n" + "=" * 60)
    print("MarkDown OCR - LLM Connection Test")
    print("=" * 60)
    print("\nThis script will test your local LLM configuration.")
    print("Make sure your LLM provider is running before proceeding.\n")

    success = True

    # Test text model
    print("📝 Testing TEXT model...")
    text_success = test_llm_connection(
        provider=provider,
        model=model,
        ollama_url=ollama_url,
        lm_studio_url=lm_studio_url,
    )

    success = success and text_success

    # Test vision model if enabled
    if use_vision:
        print("\n👁️  Testing VISION model...")
        vision_success = test_vision_model(
            provider=provider,
            model=vision_model,
            ollama_url=ollama_url,
            lm_studio_url=lm_studio_url,
        )

        success = success and vision_success

        if not vision_success:
            print(
                "\n⚠️  Vision model test failed, but you can still use text extraction."
            )
            print("Set USE_VISION_MODEL=false to disable vision processing.\n")
    else:
        print("\n⏭️  Vision model testing skipped (USE_VISION_MODEL=false)")
        print("The system will use text extraction only.\n")

    # Final summary
    print("=" * 60)
    if success:
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYour system is ready for PDF to Markdown conversion.")
        if use_vision:
            print("Vision processing is ENABLED for better accuracy.\n")
        else:
            print("Text extraction mode is ENABLED.\n")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("=" * 60)
        print("\nPlease fix the issues above before using the application.")
        print("Check the troubleshooting steps for each failed test.\n")

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
