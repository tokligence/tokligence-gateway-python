#!/usr/bin/env python3
"""
Example of using the gateway as an OpenAI-compatible API client
"""

import requests
import json
import os
from typing import Dict, Any, List


class GatewayClient:
    """Simple client for interacting with the Tokligence Gateway API."""

    def __init__(self, base_url: str = "http://localhost:8081", api_key: str = None):
        """
        Initialize the gateway client.

        Args:
            base_url: Base URL of the gateway
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.environ.get('TOKGATEWAY_API_KEY')
        self.headers = {}

        if self.api_key:
            self.headers['Authorization'] = f'Bearer {self.api_key}'

    def chat_completion(self,
                        model: str,
                        messages: List[Dict[str, str]],
                        **kwargs) -> Dict[str, Any]:
        """
        Create a chat completion.

        Args:
            model: Model to use (e.g., 'gpt-3.5-turbo')
            messages: List of message dictionaries
            **kwargs: Additional parameters

        Returns:
            Completion response
        """
        url = f"{self.base_url}/v1/chat/completions"

        data = {
            'model': model,
            'messages': messages,
            **kwargs
        }

        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def streaming_chat_completion(self,
                                  model: str,
                                  messages: List[Dict[str, str]],
                                  **kwargs):
        """
        Create a streaming chat completion.

        Args:
            model: Model to use
            messages: List of message dictionaries
            **kwargs: Additional parameters

        Yields:
            Streaming response chunks
        """
        url = f"{self.base_url}/v1/chat/completions"

        data = {
            'model': model,
            'messages': messages,
            'stream': True,
            **kwargs
        }

        response = requests.post(
            url,
            json=data,
            headers=self.headers,
            stream=True
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        break
                    yield json.loads(data)

    def list_models(self) -> Dict[str, Any]:
        """
        List available models.

        Returns:
            Models response
        """
        url = f"{self.base_url}/v1/models"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def create_embedding(self,
                        model: str,
                        input: Any,
                        **kwargs) -> Dict[str, Any]:
        """
        Create embeddings.

        Args:
            model: Model to use (e.g., 'text-embedding-ada-002')
            input: Text or list of texts to embed
            **kwargs: Additional parameters

        Returns:
            Embedding response
        """
        url = f"{self.base_url}/v1/embeddings"

        data = {
            'model': model,
            'input': input,
            **kwargs
        }

        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()


def main():
    """Example usage of the gateway client."""

    print("Tokligence Gateway Client Example")
    print("=" * 40)

    # Initialize client
    client = GatewayClient()

    # 1. List available models
    print("\n1. Listing available models...")
    try:
        models = client.list_models()
        print("Available models:")
        for model in models.get('data', []):
            print(f"  - {model.get('id', 'unknown')}")
    except Exception as e:
        print(f"Error listing models: {e}")
        print("(Gateway might not be running or models endpoint not implemented)")

    # 2. Simple chat completion
    print("\n2. Creating chat completion...")
    try:
        response = client.chat_completion(
            model='gpt-3.5-turbo',  # or 'loopback' for testing
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': 'What is 2+2?'}
            ],
            temperature=0.7,
            max_tokens=100
        )

        print("Response:")
        if 'choices' in response and response['choices']:
            content = response['choices'][0]['message']['content']
            print(f"  {content}")
        else:
            print(f"  {response}")

    except Exception as e:
        print(f"Error: {e}")

    # 3. Streaming chat completion
    print("\n3. Creating streaming chat completion...")
    try:
        print("Streaming response: ", end='')
        for chunk in client.streaming_chat_completion(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'user', 'content': 'Count from 1 to 5'}
            ]
        ):
            if 'choices' in chunk and chunk['choices']:
                delta = chunk['choices'][0].get('delta', {})
                if 'content' in delta:
                    print(delta['content'], end='', flush=True)
        print()  # New line after streaming

    except Exception as e:
        print(f"\nError: {e}")

    # 4. Create embeddings
    print("\n4. Creating embeddings...")
    try:
        response = client.create_embedding(
            model='text-embedding-ada-002',
            input='Hello, world!'
        )

        if 'data' in response and response['data']:
            embedding = response['data'][0]['embedding']
            print(f"Embedding dimension: {len(embedding)}")
            print(f"First 5 values: {embedding[:5]}")
        else:
            print(f"Response: {response}")

    except Exception as e:
        print(f"Error: {e}")
        print("(Embeddings endpoint might not be implemented)")

    print("\n" + "=" * 40)
    print("Example complete!")


if __name__ == '__main__':
    main()