import google.generativeai as genai
import anthropic
from openai import OpenAI
from mistralai import Mistral
from abc import ABC, abstractmethod


class LLMResponse:
    """Standardized response object from all LLM API calls"""
    def __init__(self, text="", error=None, provider=None):
        self.text = text
        self.error = error
        self.provider = provider
        self.success = error is None
        
    @property
    def is_error(self):
        return self.error is not None
        
    def __str__(self):
        if self.is_error:
            return f"Error from {self.provider}: {self.error}"
        return self.text


class BaseLLMClient(ABC):
    """Abstract base class for all LLM clients"""
    def __init__(self, api_key, model_version, provider_name):
        self.api_key = api_key
        self.model_version = model_version
        self.provider_name = provider_name
        
    @abstractmethod
    def generate(self, prompt, max_tokens=500, temperature=0.4):
        """Generate text from the LLM given a prompt"""
        pass
        
    def validate(self):
        """Check if client is properly configured"""
        return bool(self.api_key)
        
    def _create_error_response(self, error_msg):
        """Helper to create error response"""
        return LLMResponse(
            text="",
            error=error_msg,
            provider=self.provider_name
        )


class OpenAIClient(BaseLLMClient):
    """Client for OpenAI's GPT models"""
    def __init__(self, api_key, model_version, system_prompt="You are a helpful assistant."):
        super().__init__(api_key, model_version, "OpenAI")
        self.system_prompt = system_prompt
        self.client = None
        
        if api_key:
            self.client = OpenAI(api_key=api_key)
        
    def generate(self, prompt, max_tokens=500, temperature=0.4):
        if not self.validate():
            return self._create_error_response("Missing API key")
            
        try:
            response = self.client.chat.completions.create(
                model=self.model_version,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return LLMResponse(
                text=response.choices[0].message.content.strip(),
                provider=self.provider_name
            )
        except Exception as e:
            return self._create_error_response(str(e))


class AnthropicClient(BaseLLMClient):
    """Client for Anthropic's Claude models"""
    def __init__(self, api_key, model_version):
        super().__init__(api_key, model_version, "Anthropic")
        self.client = None
        
        if api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
        
    def generate(self, prompt, max_tokens=500, temperature=0.4):
        if not self.validate():
            return self._create_error_response("Missing API key")
            
        try:
            message = self.client.messages.create(
                model=self.model_version,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Handle different response formats
            if isinstance(message.content, list):
                text_fragments = []
                for block in message.content:
                    if hasattr(block, "text"):
                        text_fragments.append(block.text)
                    else:
                        text_fragments.append(str(block))
                combined_text = " ".join(text_fragments).strip()
            else:
                combined_text = str(message.content).strip()
                
            return LLMResponse(
                text=combined_text,
                provider=self.provider_name
            )
        except Exception as e:
            return self._create_error_response(str(e))


class GeminiClient(BaseLLMClient):
    """Client for Google's Gemini models"""
    def __init__(self, api_key, model_version):
        super().__init__(api_key, model_version, "Gemini")
        self.is_configured = False
        
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.is_configured = True
            except Exception:
                pass
        
    def validate(self):
        """Check if client is properly configured"""
        return self.is_configured and bool(self.api_key)
        
    def generate(self, prompt, max_tokens=500, temperature=0.4):
        if not self.validate():
            return self._create_error_response("Missing API key or configuration failed")
            
        try:
            model = genai.GenerativeModel(self.model_version)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    candidate_count=1,
                    stop_sequences=[],
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                )
            )
            return LLMResponse(
                text=response.text.strip() if response.text else "",
                provider=self.provider_name
            )
        except Exception as e:
            return self._create_error_response(str(e))


class GrokClient(BaseLLMClient):
    """Client for Grok AI models"""
    def __init__(self, api_key, model_version, system_prompt="You are a helpful assistant."):
        super().__init__(api_key, model_version, "Grok")
        self.system_prompt = system_prompt
        self.client = None
        
        if api_key:
            self.client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
        
    def generate(self, prompt, max_tokens=500, temperature=0.4):
        if not self.validate():
            return self._create_error_response("Missing API key")
            
        try:
            response = self.client.chat.completions.create(
                model=self.model_version,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return LLMResponse(
                text=response.choices[0].message.content.strip(),
                provider=self.provider_name
            )
        except Exception as e:
            return self._create_error_response(str(e))


class MistralClient(BaseLLMClient):
    """Client for Mistral AI models"""
    def __init__(self, api_key, model_version):
        super().__init__(api_key, model_version, "Mistral")
        self.client = None
        
        if api_key:
            self.client = Mistral(api_key=api_key)
        
    def generate(self, prompt, max_tokens=500, temperature=0.4):
        if not self.validate():
            return self._create_error_response("Missing API key")
            
        try:
            chat_response = self.client.chat.complete(
                model=self.model_version,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return LLMResponse(
                text=chat_response.choices[0].message.content.strip(),
                provider=self.provider_name
            )
        except Exception as e:
            return self._create_error_response(str(e))


def create_llm_client(provider, api_key, model_version, system_prompt=None):
    """Factory function to create appropriate LLM client based on provider"""
    provider = provider.lower()
    
    if "chad" in provider or "gpt" in provider or "openai" in provider:
        return OpenAIClient(api_key, model_version, system_prompt=system_prompt or "You are a helpful assistant.")
    
    elif "claud" in provider or "anthropic" in provider:
        return AnthropicClient(api_key, model_version)
    
    elif "gem" in provider or "google" in provider or "gianna" in provider:
        return GeminiClient(api_key, model_version)
    
    elif "grok" in provider or "xai" in provider or "greg" in provider:
        return GrokClient(api_key, model_version, system_prompt=system_prompt or "You are a helpful assistant.")
    
    elif "mistral" in provider or "marie" in provider or "mariel" in provider:
        return MistralClient(api_key, model_version)
    
    else:
        raise ValueError(f"Unsupported provider: {provider}")