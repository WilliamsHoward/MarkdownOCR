#!/usr/bin/env python3
"""
LLM Connection Test Script
Tests connectivity to Ollama or LM Studio before running the full application.
"""

import os
import sys
from typing import Optional

try:
    from langchain.prompts import ChatPromptTemplate
    from langchain_openai import ChatOpenAI
except ImportError:
    print("Error: Required packages not installed.")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)


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
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    lm_studio_url = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")

    print("\n" + "=" * 60)
    print("MarkDown OCR - LLM Connection Test")
    print("=" * 60)
    print("\nThis script will test your local LLM configuration.")
    print("Make sure your LLM provider is running before proceeding.\n")

    # Test the configured provider
    success = test_llm_connection(
        provider=provider,
        model=model,
        ollama_url=ollama_url,
        lm_studio_url=lm_studio_url,
    )

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
