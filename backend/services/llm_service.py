"""
LLM service with support for multiple providers and LoRA fine-tuning
"""
from typing import List, Dict, Any, Optional, Tuple
import logging
import json
import os
from abc import ABC, abstractmethod

from backend.config import get_settings

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate text from prompt, returns (text, metadata)"""
        pass

    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check if LLM service is healthy"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider"""

    def __init__(self, api_key: str, model: str, embedding_model: str):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("openai not installed. Run: pip install openai")

        self.model = model
        self.embedding_model = embedding_model
        logger.info(f"Initialized OpenAI provider with model: {model}")

    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate text using OpenAI"""
        settings = get_settings()

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens or settings.llm_max_tokens,
            temperature=temperature or settings.llm_temperature,
            top_p=settings.llm_top_p
        )

        text = response.choices[0].message.content
        metadata = {
            "model": self.model,
            "tokens": response.usage.total_tokens,
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "finish_reason": response.choices[0].finish_reason
        }

        logger.info(f"Generated {metadata['tokens']} tokens with OpenAI")
        return text, metadata

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI"""
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        return response.data[0].embedding

    def batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=texts
        )
        return [item.embedding for item in response.data]

    def health_check(self) -> bool:
        """Check OpenAI health"""
        try:
            self.client.models.retrieve(self.model)
            return True
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return False


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider"""

    def __init__(self, api_key: str, model: str):
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("anthropic not installed. Run: pip install anthropic")

        self.model = model
        logger.info(f"Initialized Anthropic provider with model: {model}")

    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate text using Anthropic"""
        settings = get_settings()

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens or settings.llm_max_tokens,
            temperature=temperature or settings.llm_temperature,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.content[0].text
        metadata = {
            "model": self.model,
            "tokens": response.usage.input_tokens + response.usage.output_tokens,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "stop_reason": response.stop_reason
        }

        logger.info(f"Generated {metadata['tokens']} tokens with Anthropic")
        return text, metadata

    def generate_embedding(self, text: str) -> List[float]:
        """Anthropic doesn't provide embeddings, use OpenAI or other service"""
        raise NotImplementedError("Anthropic does not provide embedding API. Use OpenAI embeddings.")

    def health_check(self) -> bool:
        """Check Anthropic health"""
        try:
            # Simple test generation
            self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Test"}]
            )
            return True
        except Exception as e:
            logger.error(f"Anthropic health check failed: {e}")
            return False


class LLMService:
    """
    Unified LLM service with support for multiple providers
    Includes fine-tuning capabilities with LoRA
    """

    def __init__(self):
        self.settings = get_settings()
        self.provider = self._create_provider()
        self.embedding_provider = self._create_embedding_provider()
        self.current_model_version = "base"

    def _create_provider(self) -> LLMProvider:
        """Create LLM provider based on configuration"""
        provider_type = self.settings.llm_provider.lower()

        if provider_type == "openai":
            return OpenAIProvider(
                api_key=self.settings.llm_api_key,
                model=self.settings.llm_model,
                embedding_model=self.settings.embedding_model
            )
        elif provider_type == "anthropic":
            return AnthropicProvider(
                api_key=self.settings.llm_api_key,
                model=self.settings.llm_model
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider_type}")

    def _create_embedding_provider(self) -> LLMProvider:
        """Create embedding provider (may be different from text generation)"""
        embedding_provider = self.settings.embedding_provider.lower()

        if embedding_provider == "openai":
            return OpenAIProvider(
                api_key=self.settings.llm_api_key,
                model=self.settings.llm_model,
                embedding_model=self.settings.embedding_model
            )
        else:
            # Fallback to main provider if it supports embeddings
            return self.provider

    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        return_confidence: bool = True
    ) -> Dict[str, Any]:
        """
        Generate text from prompt with optional confidence score

        Returns:
            {
                "text": generated text,
                "confidence": confidence score (0-1),
                "metadata": additional metadata
            }
        """
        text, metadata = self.provider.generate(prompt, max_tokens, temperature)

        # Calculate confidence score (simplified - can be enhanced)
        confidence = self._calculate_confidence(text, metadata)

        return {
            "text": text,
            "confidence": confidence,
            "metadata": metadata,
            "model_version": self.current_model_version
        }

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        return self.embedding_provider.generate_embedding(text)

    def batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if hasattr(self.embedding_provider, 'batch_generate_embeddings'):
            return self.embedding_provider.batch_generate_embeddings(texts)
        else:
            # Fallback to individual generation
            return [self.generate_embedding(text) for text in texts]

    def _calculate_confidence(self, text: str, metadata: Dict) -> float:
        """
        Calculate confidence score for generated text

        Heuristics:
        - Length of response
        - Finish reason (completed vs truncated)
        - Token usage ratio
        """
        confidence = 1.0

        # Check finish reason
        finish_reason = metadata.get("finish_reason") or metadata.get("stop_reason")
        if finish_reason in ["length", "max_tokens"]:
            confidence *= 0.8  # Truncated response

        # Check response length (very short responses may indicate low confidence)
        if len(text) < 50:
            confidence *= 0.7

        # Normalize to 0-1 range
        confidence = max(0.0, min(1.0, confidence))

        return round(confidence, 3)

    def health_check(self) -> bool:
        """Check LLM service health"""
        return self.provider.health_check()

    def load_fine_tuned_model(self, model_path: str, version: str) -> bool:
        """
        Load a fine-tuned model (LoRA adapters)

        Args:
            model_path: Path to fine-tuned model checkpoint
            version: Model version identifier

        Returns:
            True if successful
        """
        logger.info(f"Loading fine-tuned model from {model_path}")

        try:
            # For API-based providers, this might involve updating the model name
            # For local models, this would load the LoRA adapters

            if self.settings.llm_provider == "openai":
                # OpenAI fine-tuned models have format: ft:gpt-3.5-turbo:org:name:id
                # Update the model in the provider
                if os.path.exists(model_path):
                    with open(os.path.join(model_path, "model_info.json"), "r") as f:
                        model_info = json.load(f)
                        fine_tuned_model_id = model_info.get("model_id")
                        if fine_tuned_model_id:
                            self.provider.model = fine_tuned_model_id
                            self.current_model_version = version
                            logger.info(f"Loaded OpenAI fine-tuned model: {fine_tuned_model_id}")
                            return True

            # For local models with LoRA adapters
            # This would use PEFT library to load adapters
            # Placeholder for local model loading
            self.current_model_version = version
            logger.info(f"Loaded model version: {version}")
            return True

        except Exception as e:
            logger.error(f"Failed to load fine-tuned model: {e}")
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """Get current model information"""
        return {
            "provider": self.settings.llm_provider,
            "model": self.settings.llm_model,
            "embedding_model": self.settings.embedding_model,
            "current_version": self.current_model_version,
            "healthy": self.health_check()
        }


class LoRAFineTuner:
    """
    Service for fine-tuning LLMs using LoRA (Low-Rank Adaptation)
    """

    def __init__(self):
        self.settings = get_settings()
        logger.info("Initialized LoRA Fine-Tuner")

    def prepare_training_data(
        self,
        examples: List[Dict[str, str]],
        output_path: str
    ) -> str:
        """
        Prepare training data in the required format

        Args:
            examples: List of {"prompt": ..., "completion": ...} dicts
            output_path: Path to save training data

        Returns:
            Path to saved training data file
        """
        logger.info(f"Preparing {len(examples)} training examples")

        # Format depends on the model provider
        if self.settings.llm_provider == "openai":
            # OpenAI fine-tuning format (JSONL)
            formatted_data = []
            for example in examples:
                formatted_data.append({
                    "messages": [
                        {"role": "user", "content": example["prompt"]},
                        {"role": "assistant", "content": example["completion"]}
                    ]
                })

            with open(output_path, "w") as f:
                for item in formatted_data:
                    f.write(json.dumps(item) + "\n")

        else:
            # Generic format for local models
            with open(output_path, "w") as f:
                json.dump(examples, f, indent=2)

        logger.info(f"Saved training data to {output_path}")
        return output_path

    def train_lora(
        self,
        training_data_path: str,
        output_dir: str,
        model_name: str
    ) -> Dict[str, Any]:
        """
        Train LoRA adapters on the provided data

        This is a placeholder implementation. Full implementation would:
        1. Load base model
        2. Prepare LoRA configuration
        3. Train adapters
        4. Save checkpoints
        5. Evaluate and return metrics

        Args:
            training_data_path: Path to training data
            output_dir: Directory to save model
            model_name: Name for the fine-tuned model

        Returns:
            Training results and metrics
        """
        logger.info(f"Starting LoRA training for {model_name}")

        try:
            # For OpenAI, create fine-tuning job via API
            if self.settings.llm_provider == "openai":
                return self._train_openai_fine_tune(training_data_path, output_dir, model_name)

            # For local models, use transformers + PEFT
            # This would involve:
            # - Loading model with PEFT
            # - Configuring LoRA parameters
            # - Training loop
            # - Saving adapters

            # Placeholder return
            return {
                "model_name": model_name,
                "output_dir": output_dir,
                "status": "training_started",
                "message": "Training job initiated"
            }

        except Exception as e:
            logger.error(f"LoRA training failed: {e}")
            raise

    def _train_openai_fine_tune(
        self,
        training_data_path: str,
        output_dir: str,
        model_name: str
    ) -> Dict[str, Any]:
        """Train fine-tuned model via OpenAI API"""
        from openai import OpenAI

        client = OpenAI(api_key=self.settings.llm_api_key)

        # Upload training file
        with open(training_data_path, "rb") as f:
            file_response = client.files.create(
                file=f,
                purpose="fine-tune"
            )

        # Create fine-tuning job
        job = client.fine_tuning.jobs.create(
            training_file=file_response.id,
            model=self.settings.llm_model
        )

        # Save job info
        os.makedirs(output_dir, exist_ok=True)
        job_info = {
            "job_id": job.id,
            "model_name": model_name,
            "base_model": self.settings.llm_model,
            "status": job.status,
            "created_at": job.created_at
        }

        with open(os.path.join(output_dir, "job_info.json"), "w") as f:
            json.dump(job_info, f, indent=2)

        logger.info(f"Created OpenAI fine-tuning job: {job.id}")

        return job_info

    def check_training_status(self, job_id: str) -> Dict[str, Any]:
        """Check status of training job"""
        if self.settings.llm_provider == "openai":
            from openai import OpenAI
            client = OpenAI(api_key=self.settings.llm_api_key)

            job = client.fine_tuning.jobs.retrieve(job_id)

            return {
                "job_id": job.id,
                "status": job.status,
                "fine_tuned_model": job.fine_tuned_model,
                "trained_tokens": job.trained_tokens,
                "error": job.error if hasattr(job, 'error') else None
            }

        return {"status": "unknown"}
