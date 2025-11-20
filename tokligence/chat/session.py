"""
Chat Session

Interactive AI assistant for configuration and troubleshooting
"""

import asyncio
import sys
from typing import Optional, Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from .detector import LLMDetector, select_endpoint
from .knowledge import load_knowledge
from .client import create_client, get_model, create_streaming_chat
from .tools import TOOLS, parse_tool_calls, execute_tool_calls, get_platform_info

console = Console()


class ChatSession:
    """Interactive chat session"""

    def __init__(self, endpoint, client, model, knowledge):
        self.endpoint = endpoint
        self.client = client
        self.model = model
        self.knowledge = knowledge
        self.messages: List[Dict[str, Any]] = []

        # Initialize system prompt
        system_prompt = knowledge.build_system_prompt()
        self.messages.append({
            'role': 'system',
            'content': system_prompt
        })

    async def start(self):
        """Start the interactive chat loop"""
        platform_info = get_platform_info()

        # Display header
        console.print("\n[bold cyan]⚡ TOKLIGENCE GATEWAY ASSISTANT[/bold cyan]\n")

        console.print(f"Using: [green]{self.endpoint.name}[/green]")
        console.print(f"Model: [green]{self.model}[/green]")
        console.print(f"Platform: [blue]{platform_info['platform']}[/blue]\n")

        # Privacy & safety notice
        console.print("[dim]Privacy & safety: this assistant is designed to minimize data sent to remote LLM providers[/dim]")
        console.print("[dim](e.g. masking API keys/tokens/secrets).[/dim]")
        console.print("[dim]Do NOT paste raw API keys, tokens, passwords, or other secrets into this chat.[/dim]")
        console.print("[dim]Instead, use environment variables or local config files.[/dim]")
        console.print("[dim]Type 'exit' or 'quit' to end the session.\n[/dim]")

        # Main chat loop
        try:
            while True:
                # Get user input
                try:
                    user_input = console.input("[yellow]You:[/yellow] ").strip()
                except (EOFError, KeyboardInterrupt):
                    console.print("\n[dim]Goodbye! 👋[/dim]\n")
                    break

                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', 'q']:
                    console.print("\n[dim]Goodbye! 👋[/dim]\n")
                    break

                # Skip empty input
                if not user_input:
                    continue

                # Add user message
                self.messages.append({
                    'role': 'user',
                    'content': user_input
                })

                # Get AI response
                try:
                    await self.get_response()
                except Exception as e:
                    console.print(f"\n[red]❌ Error: {e}[/red]\n")

                console.print()  # Blank line between exchanges

        except Exception as e:
            console.print(f"\n[red]❌ Unexpected error: {e}[/red]\n")

    async def get_response(self):
        """Get AI response with tool calling support"""
        should_continue = True
        iteration_count = 0
        max_iterations = 5  # Prevent infinite loops

        while should_continue and iteration_count < max_iterations:
            iteration_count += 1

            # Show thinking indicator for iterations after first
            if iteration_count > 1:
                console.print(f"[dim]Processing (step {iteration_count})...[/dim]")

            # Create streaming chat completion
            stream = await create_streaming_chat(
                self.client,
                self.endpoint,
                self.model,
                self.messages,
                {
                    'tools': TOOLS,
                    'temperature': 0.7,
                    'maxTokens': 2048
                }
            )

            # Show Assistant label when response starts
            if iteration_count == 1:
                console.print("[cyan]Assistant:[/cyan] ", end='')

            assistant_message = ''
            tool_calls = []

            # Process stream based on endpoint type
            if self.endpoint.type == 'openai' or self.endpoint.type == 'ollama':
                # OpenAI-compatible API
                async for chunk in stream:
                    delta = chunk.choices[0].delta if chunk.choices else None

                    if delta and delta.content:
                        # Stream text content to user
                        console.print(delta.content, end='')
                        assistant_message += delta.content

                    # Handle tool calls
                    if delta and delta.tool_calls:
                        for tool_call_delta in delta.tool_calls:
                            index = tool_call_delta.index

                            if index >= len(tool_calls):
                                tool_calls.append({
                                    'id': tool_call_delta.id or '',
                                    'type': 'function',
                                    'function': {
                                        'name': '',
                                        'arguments': ''
                                    }
                                })

                            if tool_call_delta.id:
                                tool_calls[index]['id'] = tool_call_delta.id

                            if tool_call_delta.function and tool_call_delta.function.name:
                                tool_calls[index]['function']['name'] += tool_call_delta.function.name

                            if tool_call_delta.function and tool_call_delta.function.arguments:
                                tool_calls[index]['function']['arguments'] += tool_call_delta.function.arguments

                    # Check if done
                    finish_reason = chunk.choices[0].finish_reason if chunk.choices else None
                    if finish_reason == 'stop':
                        should_continue = False
                    elif finish_reason == 'tool_calls':
                        should_continue = True

            elif self.endpoint.type == 'anthropic':
                # Anthropic streaming format
                async for event in stream:
                    if event.type == 'content_block_delta':
                        if event.delta.type == 'text_delta':
                            console.print(event.delta.text, end='')
                            assistant_message += event.delta.text
                    elif event.type == 'content_block_start':
                        if event.content_block.type == 'tool_use':
                            tool_calls.append({
                                'id': event.content_block.id,
                                'type': 'function',
                                'function': {
                                    'name': event.content_block.name,
                                    'arguments': ''
                                }
                            })
                    elif event.type == 'content_block_delta' and event.delta.type == 'input_json_delta':
                        # Accumulate tool arguments
                        if tool_calls:
                            tool_calls[-1]['function']['arguments'] += event.delta.partial_json
                    elif event.type == 'message_stop':
                        should_continue = len(tool_calls) > 0

            elif self.endpoint.type == 'google':
                # Google Gemini streaming format
                async for chunk in stream:
                    chunk_text = chunk.text
                    if chunk_text:
                        console.print(chunk_text, end='')
                        assistant_message += chunk_text

                    # Handle function calls
                    if hasattr(chunk, 'function_calls') and chunk.function_calls:
                        for fc in chunk.function_calls:
                            import json
                            tool_calls.append({
                                'id': f'google_{len(tool_calls)}',
                                'type': 'function',
                                'function': {
                                    'name': fc.name,
                                    'arguments': json.dumps(dict(fc.args))
                                }
                            })

                should_continue = len(tool_calls) > 0

            console.print()  # New line after streaming

            # Build assistant message object
            message_obj = {
                'role': 'assistant',
                'content': assistant_message or None
            }

            if tool_calls:
                message_obj['tool_calls'] = tool_calls

            self.messages.append(message_obj)

            # Execute tool calls if present
            if tool_calls:
                parsed_tool_calls = parse_tool_calls(message_obj)
                tool_results = await execute_tool_calls(parsed_tool_calls)

                # Add tool results to messages
                for result in tool_results:
                    self.messages.append(result)

                # Continue the loop to get final response
                should_continue = True
            else:
                should_continue = False

        if iteration_count >= max_iterations:
            console.print("[yellow]⚠️  Maximum iterations reached. Please start a new query.[/yellow]")


async def start_chat(model: Optional[str] = None):
    """
    Start interactive chat session

    Args:
        model: Optional preferred model name

    Raises:
        RuntimeError: If no LLM endpoints are available
    """
    try:
        console.print("[bold]\n🚀 Starting Tokligence Gateway Chat...\n[/bold]")

        # Step 1: Detect available LLM endpoints
        console.print("🔍 Detecting available LLM endpoints...")
        detector = LLMDetector()
        await detector.detect_all()

        available = detector.get_available_endpoints()
        if not available:
            raise RuntimeError(
                "No LLM endpoints available. Please configure at least one:\n"
                "  - OpenAI: export TOKLIGENCE_OPENAI_API_KEY=sk-...\n"
                "  - Anthropic: export TOKLIGENCE_ANTHROPIC_API_KEY=sk-ant-...\n"
                "  - Google Gemini: export TOKLIGENCE_GOOGLE_API_KEY=...\n"
                "  - Or run a local LLM (Ollama, vLLM, LM Studio)"
            )

        console.print(f"   Found {len(available)} endpoint(s):")
        for ep in available:
            console.print(f"   • {ep.name} ({'local' if ep.local else 'remote'})")

        # Step 2: Select the best endpoint
        endpoint = await select_endpoint(detector)
        console.print(f"\n✓ Selected: [green]{endpoint.name}[/green]")

        # Step 3: Create client
        console.print("🔧 Creating LLM client...")
        client = create_client(endpoint)
        model_name = get_model(endpoint, model)

        # Step 4: Load knowledge base
        console.print("📚 Loading knowledge base...")
        knowledge = load_knowledge()
        console.print(f"   Loaded {len(knowledge.get_available_docs())} documents")

        # Step 5: Start chat session
        session = ChatSession(endpoint, client, model_name, knowledge)
        await session.start()

    except Exception as e:
        console.print(f"\n[red]❌ Failed to start chat: {e}[/red]\n")

        # Provide helpful guidance
        platform_info = get_platform_info()
        console.print("[yellow]Troubleshooting:[/yellow]")

        if platform_info['isWindows']:
            console.print("  [dim]• Check if Ollama/vLLM/LM Studio is running[/dim]")
            console.print("  [dim]• Verify environment variables in System Properties[/dim]")
            console.print("  [dim]• Try running as Administrator[/dim]")
        else:
            console.print("  [dim]• Check if Ollama/vLLM/LM Studio is running[/dim]")
            console.print("  [dim]• Verify environment variables: printenv | grep TOKLIGENCE[/dim]")
            console.print("  [dim]• Check file permissions in ~/.tokligence/[/dim]")

        console.print("\n[dim]For more help, visit: https://github.com/tokligence/tokligence-gateway[/dim]\n")
        sys.exit(1)


def main():
    """Main entry point for testing"""
    asyncio.run(start_chat())


if __name__ == '__main__':
    main()
