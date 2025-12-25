"""
LLM Service - Interface for Large Language Models
Supports Ollama (local), OpenAI, and other LLM providers
"""
import requests
import json
import os


class LLMService:
    """
    Unified interface for working with different LLM providers
    """
    
    def __init__(self, provider='ollama', model=None, api_key=None):
        """
        Initialize LLM service
        
        Args:
            provider: 'ollama', 'openai', 'anthropic', or 'huggingface'
            model: Model name (e.g., 'llama3', 'gpt-3.5-turbo')
            api_key: API key for cloud providers
        """
        self.provider = provider.lower()
        self.api_key = api_key or os.environ.get(f'{provider.upper()}_API_KEY')
        
        # Configuration
        self.ollama_url = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
        self.max_tokens = 1000
        self.temperature = 0.7
        
        # Set model - try to auto-detect if Ollama and model not specified
        if model:
            self.model = model
        elif self.provider == 'ollama':
            # Try to get from env, then auto-detect, then default
            env_model = os.environ.get('OLLAMA_MODEL')
            if env_model:
                self.model = env_model
            else:
                # Auto-detect available models
                available_models = self._get_available_ollama_models()
                if available_models:
                    # Prefer llama3, then mistral, then phi, then first available
                    preferred = ['llama3', 'mistral', 'phi']
                    for pref in preferred:
                        matching = [m for m in available_models if pref in m.lower()]
                        if matching:
                            self.model = matching[0]
                            break
                    else:
                        self.model = available_models[0]
                else:
                    self.model = 'llama3'  # Fallback default
        else:
            self.model = self._get_default_model()
    
    def _get_available_ollama_models(self):
        """Get list of available Ollama models"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
        except:
            pass
        return []
    
    def _get_default_model(self):
        """Get default model based on provider"""
        defaults = {
            'ollama': 'llama3',  # Default to llama3
            'openai': 'gpt-3.5-turbo',
            'anthropic': 'claude-2',
            'huggingface': 'meta-llama/Llama-2-7b-chat-hf'
        }
        return defaults.get(self.provider, 'llama3')
    
    def generate(self, prompt, context=None, system_prompt=None):
        """
        Generate text using the LLM
        
        Args:
            prompt: User's question/prompt
            context: Additional context (e.g., retrieved documents)
            system_prompt: System instructions for the LLM
            
        Returns:
            Generated text response
        """
        if self.provider == 'ollama':
            return self._generate_ollama(prompt, context, system_prompt)
        elif self.provider == 'openai':
            return self._generate_openai(prompt, context, system_prompt)
        elif self.provider == 'anthropic':
            return self._generate_anthropic(prompt, context, system_prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _generate_ollama(self, prompt, context=None, system_prompt=None):
        """Generate text using Ollama (local LLM)"""
        try:
            # Build the full prompt
            full_prompt = self._build_prompt(prompt, context, system_prompt)
            
            # Ollama API endpoint
            url = f"{self.ollama_url}/api/generate"
            
            # Request payload
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            }
            
            # Make request
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            return result.get('response', '').strip()
            
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                "Could not connect to Ollama. "
                "Make sure Ollama is running (ollama serve) and accessible at "
                f"{self.ollama_url}"
            )
        except requests.exceptions.Timeout:
            raise TimeoutError("Ollama request timed out. Try a shorter prompt or increase timeout.")
        except Exception as e:
            raise Exception(f"Error generating response with Ollama: {e}")
    
    def _generate_openai(self, prompt, context=None, system_prompt=None):
        """Generate text using OpenAI API"""
        try:
            import openai
            
            if not self.api_key:
                raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
            
            openai.api_key = self.api_key
            
            messages = []
            
            # Add system message
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            else:
                messages.append({
                    "role": "system",
                    "content": "You are a helpful academic assistant. Answer questions based on the provided context."
                })
            
            # Add context if provided
            if context:
                messages.append({
                    "role": "system",
                    "content": f"Context:\n{context}"
                })
            
            # Add user prompt
            messages.append({"role": "user", "content": prompt})
            
            # Make request
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except ImportError:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")
        except Exception as e:
            raise Exception(f"Error generating response with OpenAI: {e}")
    
    def _generate_anthropic(self, prompt, context=None, system_prompt=None):
        """Generate text using Anthropic Claude API"""
        try:
            import anthropic
            
            if not self.api_key:
                raise ValueError("Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable.")
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            # Build full prompt
            full_prompt = self._build_prompt(prompt, context, system_prompt)
            
            # Make request
            response = client.completions.create(
                model=self.model,
                prompt=f"{anthropic.HUMAN_PROMPT} {full_prompt}{anthropic.AI_PROMPT}",
                max_tokens_to_sample=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.completion.strip()
            
        except ImportError:
            raise ImportError("Anthropic library not installed. Install with: pip install anthropic")
        except Exception as e:
            raise Exception(f"Error generating response with Anthropic: {e}")
    
    def _build_prompt(self, prompt, context=None, system_prompt=None):
        """Build the full prompt with context and system instructions"""
        parts = []
        
        # Add system prompt
        if system_prompt:
            parts.append(f"[SYSTEM]\n{system_prompt}\n")
        else:
            parts.append(
                "[SYSTEM]\n"
                "You are a helpful academic assistant for university students. "
                "Answer questions clearly and concisely based on the provided context. "
                "If the context doesn't contain enough information, say so.\n"
            )
        
        # Add context (retrieved documents)
        if context:
            parts.append(f"[CONTEXT]\n{context}\n")
        
        # Add user question
        parts.append(f"[QUESTION]\n{prompt}\n")
        parts.append("\n[ANSWER]")
        
        return "\n".join(parts)
    
    def generate_rag_response(self, question, retrieved_docs):
        """
        Generate response for RAG (Retrieval-Augmented Generation)
        
        Args:
            question: User's question
            retrieved_docs: List of retrieved document objects
            
        Returns:
            Generated answer with citations
        """
        if not retrieved_docs:
            return {
                'answer': "I apologize, but I couldn't find relevant information in my knowledge base to answer your question. Please try rephrasing your question or ask about topics related to courses, schedules, academic information, or university policies.",
                'confidence': 'low'
            }
        
        # Build context from retrieved documents
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            context_parts.append(
                f"Document {i}: {doc.Title}\n"
                f"Category: {doc.Category}\n"
                f"Content: {doc.Content}\n"
            )
        
        context = "\n---\n".join(context_parts)
        
        # Custom system prompt for RAG
        system_prompt = (
            "You are a knowledgeable university assistant. "
            "Use the provided documents to answer the student's question. "
            "Be specific and cite information from the documents. "
            "If the documents don't fully answer the question, acknowledge the limitations. "
            "Keep your response concise but informative (2-4 paragraphs max)."
        )
        
        try:
            # Generate answer
            answer = self.generate(question, context, system_prompt)
            
            # Determine confidence based on number of docs
            if len(retrieved_docs) >= 2:
                confidence = 'high'
            elif len(retrieved_docs) == 1:
                confidence = 'medium'
            else:
                confidence = 'low'
            
            return {
                'answer': answer,
                'confidence': confidence
            }
            
        except Exception as e:
            print(f"Error generating RAG response: {e}")
            # Fallback to simple concatenation
            answer = f"Based on the available information:\n\n{retrieved_docs[0].Content}"
            return {
                'answer': answer,
                'confidence': 'medium'
            }
    
    def is_available(self):
        """Check if the LLM service is available"""
        if self.provider == 'ollama':
            try:
                response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
                return response.status_code == 200
            except:
                return False
        elif self.provider == 'openai':
            return bool(self.api_key)
        elif self.provider == 'anthropic':
            return bool(self.api_key)
        return False
    
    def list_available_models(self):
        """List available models for the current provider"""
        if self.provider == 'ollama':
            try:
                response = requests.get(f"{self.ollama_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    return [model['name'] for model in data.get('models', [])]
            except:
                pass
        return []
    
    def pull_model(self, model_name):
        """Download/pull a model (Ollama only)"""
        if self.provider != 'ollama':
            raise ValueError("Model pulling is only supported for Ollama")
        
        try:
            url = f"{self.ollama_url}/api/pull"
            payload = {"name": model_name}
            
            response = requests.post(url, json=payload, stream=True, timeout=300)
            
            # Stream the progress
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    status = data.get('status', '')
                    print(f"Pulling {model_name}: {status}")
            
            return True
        except Exception as e:
            print(f"Error pulling model: {e}")
            return False


# Convenience function
def get_llm_service(provider=None, model=None):
    """
    Get LLM service instance with auto-configuration
    
    Returns the first available provider in this order:
    1. Ollama (if running locally)
    2. OpenAI (if API key is set)
    3. Fallback to template-based (returns None)
    """
    # Try provider from environment or parameter
    provider = provider or os.environ.get('LLM_PROVIDER', 'ollama')
    
    # Try to create service
    try:
        service = LLMService(provider=provider, model=model)
        
        if service.is_available():
            print(f"[LLM] Using {provider} with model: {service.model}")
            return service
        else:
            print(f"[LLM] {provider} is not available")
    except Exception as e:
        print(f"[LLM] Error initializing {provider}: {e}")
    
    # Try fallback providers
    if provider != 'ollama':
        try:
            service = LLMService(provider='ollama')
            if service.is_available():
                print(f"[LLM] Falling back to Ollama")
                return service
        except:
            pass
    
    print("[LLM] No LLM provider available, using template-based responses")
    return None


# Test function
if __name__ == "__main__":
    print("Testing LLM Service...")
    print("-" * 60)
    
    # Test Ollama
    print("\n1. Testing Ollama connection...")
    try:
        llm = LLMService(provider='ollama', model='llama2')
        
        if llm.is_available():
            print("✓ Ollama is available")
            
            # List models
            models = llm.list_available_models()
            print(f"  Available models: {', '.join(models) if models else 'None'}")
            
            # Test generation
            print("\n2. Testing text generation...")
            response = llm.generate(
                prompt="What is machine learning in one sentence?",
                system_prompt="You are a helpful AI assistant. Be concise."
            )
            print(f"  Response: {response}")
            
        else:
            print("✗ Ollama is not available")
            print("\nTo install and run Ollama:")
            print("1. Download from: https://ollama.ai/download")
            print("2. Install Ollama")
            print("3. Run: ollama pull llama2")
            print("4. Run: ollama serve")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 60)
