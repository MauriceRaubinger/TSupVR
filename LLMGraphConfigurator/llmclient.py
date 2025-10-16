import os
from abc import ABC, abstractmethod
from typing import Optional
from openai import OpenAI



# --- Configuration Management ---
class APIConfig:
    """Configuration class for managing API keys and settings"""

    def __init__(self,
                 google_api_key: Optional[str] = None,
                 openai_api_key: Optional[str] = None,
                 claude_api_key: Optional[str] = None,
                 langsmith_api_key: Optional[str] = None,
                 langsmith_tracing: str = "true"):
        """
        Initialize API configuration

        Args:
            google_api_key: Google API key (if None, uses environment variable)
            openai_api_key: OpenAI API key (if None, uses environment variable)
            claude_api_key: Claude API key (if None, uses environment variable)
            langsmith_api_key: LangSmith API key (if None, uses environment variable)
            langsmith_tracing: Enable/disable LangSmith tracing
        """
        # Set default values or get from environment
        g_key =""
        l_key= ""
        self.google_api_key = google_api_key or os.environ.get(
            "GOOGLE_API_KEY",
            g_key
        )

        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")

        self.claude_api_key = claude_api_key or os.environ.get("ANTHROPIC_API_KEY")

        self.langsmith_api_key = langsmith_api_key or os.environ.get(
            "LANGSMITH_API_KEY",
            l_key
        )

        self.langsmith_tracing = langsmith_tracing

        # Apply configuration to environment
        self._apply_to_environment()

    def _apply_to_environment(self):
        """Apply configuration values to environment variables"""
        os.environ["GOOGLE_API_KEY"] = self.google_api_key

        if self.openai_api_key:
            os.environ["OPENAI_API_KEY"] = self.openai_api_key

        if self.claude_api_key:
            os.environ["ANTHROPIC_API_KEY"] = self.claude_api_key

        os.environ["LANGSMITH_API_KEY"] = self.langsmith_api_key
        os.environ["LANGSMITH_TRACING"] = self.langsmith_tracing

    def update_google_key(self, api_key: str):
        """Update Google API key"""
        self.google_api_key = api_key
        os.environ["GOOGLE_API_KEY"] = api_key

    def update_openai_key(self, api_key: str):
        """Update OpenAI API key"""
        self.openai_api_key = api_key
        os.environ["OPENAI_API_KEY"] = api_key

    def update_claude_key(self, api_key: str):
        """Update Claude API key"""
        self.claude_api_key = api_key
        os.environ["ANTHROPIC_API_KEY"] = api_key

    def __str__(self):
        """String representation showing which keys are configured"""
        google_status = "✓" if self.google_api_key else "✗"
        openai_status = "✓" if self.openai_api_key else "✗"
        claude_status = "✓" if self.claude_api_key else "✗"
        langsmith_status = "✓" if self.langsmith_api_key else "✗"

        return f"""API Configuration:
  Google API Key: {google_status}
  OpenAI API Key: {openai_status}
  Claude API Key: {claude_status}
  LangSmith API Key: {langsmith_status}
  LangSmith Tracing: {self.langsmith_tracing}"""


def initialize_api_keys():
    """Initialize API keys with default configuration"""
    return APIConfig()


# --- LLM Client Framework ---
class LLMClient(ABC):
    """Abstract base class for LLM clients"""

    @abstractmethod
    def invoke(self, messages) -> str:
        """Send messages and return the assistant reply"""
        pass


class GoogleLLMClient(LLMClient):
    """Google Gemini LLM Client"""

    def __init__(self, model_name: str = "gemini-2.0-flash-lite"):
        from langchain.chat_models import init_chat_model
        self.model_name = model_name
        self.client = init_chat_model(model_name, model_provider="google_genai")

    def invoke(self, messages) -> str:
        """
        Invoke Google Gemini model

        Args:
            messages: Can be string, list of strings, or LangChain message objects

        Returns:
            str: Model response content
        """
        # Convert string messages to proper format if needed
        if isinstance(messages, str):
            from langchain_core.messages import HumanMessage
            messages = [HumanMessage(content=messages)]
        elif isinstance(messages, list) and len(messages) > 0 and isinstance(messages[0], str):
            from langchain_core.messages import HumanMessage
            messages = [HumanMessage(content=messages[0])]

        response = self.client.invoke(messages)
        return response.content


class OpenAIClient(LLMClient):
    """OpenAI GPT Client"""

    def __init__(self, model_name: str = None, api_key: str = None):
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")

        self.client = OpenAI(api_key=key)
        self.model_name = model_name or "gpt-3.5-turbo"

    def invoke(self, messages) -> str:
        """
        Invoke OpenAI model

        Args:
            messages: Can be string, list of strings, or OpenAI message format

        Returns:
            str: Model response content
        """
        # Convert string to proper message format
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        elif isinstance(messages, list) and len(messages) > 0 and isinstance(messages[0], str):
            messages = [{"role": "user", "content": messages[0]}]

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0
        )
        return response.choices[0].message.content


class ClaudeClient(LLMClient):
    """Anthropic Claude API Client"""

    def __init__(self, model_name: str = "claude-3-5-sonnet-20241022", api_key: str = None):
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic package is required for Claude client. Install with: pip install anthropic")

        key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise ValueError(
                "Claude API key is required. Set ANTHROPIC_API_KEY environment variable or pass api_key parameter."
            )

        self.client = anthropic.Anthropic(api_key=key)
        self.model_name = model_name

    def invoke(self, messages) -> str:
        """
        Invoke Claude model

        Args:
            messages: Can be string, list of strings, or Anthropic message format

        Returns:
            str: Model response content
        """
        # Convert string to proper message format
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        elif isinstance(messages, list) and len(messages) > 0 and isinstance(messages[0], str):
            messages = [{"role": "user", "content": messages[0]}]

        # Handle LangChain message objects
        elif isinstance(messages, list) and len(messages) > 0:
            formatted_messages = []
            for msg in messages:
                if hasattr(msg, 'type') and hasattr(msg, 'content'):
                    # LangChain message object
                    role = "user" if msg.type == "human" else "assistant" if msg.type == "ai" else "user"
                    formatted_messages.append({"role": role, "content": msg.content})
                elif isinstance(msg, dict):
                    # Already in correct format
                    formatted_messages.append(msg)
                else:
                    # Fallback - treat as user message
                    formatted_messages.append({"role": "user", "content": str(msg)})
            messages = formatted_messages

        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=4096,
                temperature=0,
                messages=messages
            )
            return response.content[0].text
        except Exception as e:
            raise RuntimeError(f"Error calling Claude API: {str(e)}")


class GrokClient(LLMClient):
    """xAI Grok API Client"""

    def __init__(self, model_name: str = "grok-3", endpoint: str = None, api_token: str = None):
        self.model_name = model_name
        self.endpoint = endpoint or os.getenv("GROK_ENDPOINT")
        self.api_key = api_token or os.getenv("XAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "xAI API key is required. Set XAI_API_KEY environment variable or pass api_token parameter."
            )
        os.environ["XAI_API_KEY"] = self.api_key
        #self.client = ChatXAI(
        #    model=self.model_name,
         #   api_base=self.endpoint if self.endpoint else None
        #)

    def invoke(self, messages) -> str:
        """
        Invoke xAI Grok model

        Args:
            messages: Can be string, list of strings, or LangChain message objects

        Returns:
            str: Model response content
        """
        if isinstance(messages, str):
            from langchain_core.messages import HumanMessage
            messages = [HumanMessage(content=messages)]
        elif isinstance(messages, list) and len(messages) > 0 and isinstance(messages[0], str):
            from langchain_core.messages import HumanMessage
            messages = [HumanMessage(content=messages[0])]

        response = self.client.invoke(messages)
        return response.content


class QwenClient(LLMClient):
    """Alibaba Qwen API Client"""

    def __init__(self, model_name: str = "qwen-turbo", api_key: str = None):
        from langchain_community.chat_models.tongyi import ChatTongyi
        self.model_name = model_name
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "DashScope API key is required for Qwen. Set DASHSCOPE_API_KEY environment variable or pass api_key parameter."
            )
        os.environ["DASHSCOPE_API_KEY"] = self.api_key
        self.client = ChatTongyi(model=self.model_name)

    def invoke(self, messages) -> str:
        """
        Invoke Alibaba Qwen model

        Args:
            messages: Can be string, list of strings, or LangChain message objects

        Returns:
            str: Model response content
        """
        if isinstance(messages, str):
            from langchain_core.messages import HumanMessage
            messages = [HumanMessage(content=messages)]
        elif isinstance(messages, list) and len(messages) > 0 and isinstance(messages[0], str):
            from langchain_core.messages import HumanMessage
            messages = [HumanMessage(content=messages[0])]

        response = self.client.invoke(messages)
        return response.content


def get_llm_client(provider: str = "google", **kwargs) -> LLMClient:
    if provider == "google":
        model_name = kwargs.get("model_name", "gemini-2.0-flash")
        return GoogleLLMClient(model_name)
    elif provider == "openai":
        model_name = kwargs.get("model_name")
        api_key = kwargs.get("api_key")
        return OpenAIClient(model_name, api_key)
    elif provider == "claude":
        model_name = kwargs.get("model_name", "claude-3-5-sonnet-20241022")
        api_key = kwargs.get("api_key")
        return ClaudeClient(model_name=model_name, api_key=api_key)
    elif provider == "grok":
        model_name = kwargs.get("model_name", "grok-3")
        endpoint = kwargs.get("endpoint")
        api_token = kwargs.get("api_token")
        return GrokClient(model_name=model_name, endpoint=endpoint, api_token=api_token)
    elif provider == "qwen":
        model_name = kwargs.get("model_name", "qwen-turbo")
        api_key = kwargs.get("api_key")
        return QwenClient(model_name=model_name, api_key=api_key)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


# Example usage:
if __name__ == "__main__":
    # Initialize API configuration with your Claude key
    config = APIConfig(claude_api_key="antropic_key")
    print(config)

    # Create Claude client
    claude_client = get_llm_client("claude")

    # Test the client
    response = claude_client.invoke("Hello! How are you?")
    print(f"Claude response: {response}")