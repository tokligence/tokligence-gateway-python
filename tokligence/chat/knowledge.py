"""
Knowledge Base Loader

Loads documentation from local snapshot (bundled with package)
and provides links to latest online documentation.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any

KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"
META_FILE = KNOWLEDGE_DIR / "_meta.json"


class KnowledgeBase:
    """Manages documentation knowledge base"""

    def __init__(self):
        self.meta: Dict[str, Any] = {}
        self.docs: Dict[str, str] = {}
        self.links: Dict[str, str] = {
            'github': 'https://github.com/tokligence/tokligence-gateway',
            'pypi': 'https://pypi.org/project/tokligence/',
            'website': 'https://tokligence.ai',
            'wiki': 'https://github.com/tokligence/tokligence-gateway/wiki',
            'issues': 'https://github.com/tokligence/tokligence-gateway/issues'
        }

    def load(self) -> 'KnowledgeBase':
        """Load all documentation from local knowledge base"""
        # Load metadata if exists
        if META_FILE.exists():
            try:
                with open(META_FILE, 'r', encoding='utf-8') as f:
                    self.meta = json.load(f)
            except Exception as e:
                print(f'⚠️  Failed to load knowledge metadata: {e}')

        # Load all markdown files
        if KNOWLEDGE_DIR.exists():
            for md_file in KNOWLEDGE_DIR.glob('*.md'):
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        name = md_file.stem
                        self.docs[name] = content
                except Exception as e:
                    print(f'⚠️  Failed to load {md_file}: {e}')

        return self

    def search_docs(self, query: str) -> List[Dict[str, Any]]:
        """
        Search documentation for keywords

        Args:
            query: Search query

        Returns:
            List of matching sections with context
        """
        results = []
        query_lower = query.lower()

        for doc_name, content in self.docs.items():
            lines = content.split('\n')
            current_section = ''

            for i, line in enumerate(lines):
                # Track sections (markdown headers)
                if line.startswith('#'):
                    current_section = line.lstrip('#').strip()

                # Check if line matches query
                if query_lower in line.lower():
                    results.append({
                        'doc': doc_name,
                        'section': current_section,
                        'line': i + 1,
                        'content': line.strip()
                    })

        return results

    def get_doc(self, name: str) -> Optional[str]:
        """
        Get documentation content by name

        Args:
            name: Document name (without .md extension)

        Returns:
            Document content or None if not found
        """
        return self.docs.get(name)

    def build_system_prompt(self) -> str:
        """
        Generate system prompt with knowledge base

        Returns:
            System prompt for the LLM
        """
        doc_summary = (
            f"You have access to the following local documentation:\n"
            f"{chr(10).join(f'- {d}' for d in self.docs.keys())}"
            if self.docs
            else "No local documentation available."
        )

        version_info = (
            f"\nDocumentation version: {self.meta['version']}"
            if self.meta.get('version')
            else ''
        )

        prompt = f"""You are the Tokligence Gateway Assistant, helping users configure and use Tokligence Gateway.

Tokligence Gateway is a unified API gateway that provides:
- Unified API interface for multiple LLM providers (OpenAI, Anthropic, Google Gemini, etc.)
- Bidirectional protocol translation (OpenAI ↔ Anthropic)
- Token management and cost tracking
- Request routing and load balancing
- Caching and rate limiting
- Production-ready features (Prometheus metrics, health checks, rate limiting)

{doc_summary}{version_info}

Online Resources:
- GitHub: {self.links['github']}
- PyPI Package: {self.links['pypi']}
- Website: {self.links['website']}
- Documentation: {self.links['wiki']}

Your role:
1. Answer questions about Tokligence Gateway configuration and usage.
2. Help users configure their gateway settings.
3. Provide troubleshooting assistance.
4. Execute configuration commands when requested.
5. Always refer to official documentation for latest information.

Safety & accuracy guidelines (very important):
- Never invent or guess user-specific configuration values, API keys, emails, base URLs, prices, or model names.
- Assume LLM calls may go to remote providers; treat any configuration or log data as sensitive and minimize what you expose.
- The local tools deliberately MASK or SUMMARIZE sensitive data (API keys, secrets, tokens, emails, names): you never see raw secret values in tool results, only redacted placeholders, lengths, prefixes, or boolean flags like "*_configured".
- When you call tools like get_config/get_status, treat their JSON result as the only source of truth about the user's current gateway state.
- If a value is NOT present in tool output, say you don't know or that it is not visible, instead of assuming it.
- Clearly distinguish between:
  • General capabilities of Tokligence Gateway (use phrasing like "Tokligence Gateway supports..."), and
  • This user's current configuration (only describe what you actually see in tool results).
- Do not claim that a specific upstream provider, model family, or price is configured unless that string appears in the tool result or the user explicitly told you.
- When summarizing full configuration, prefer high-level categories (e.g. which features are enabled/disabled) instead of fabricating detailed, per-field narratives.
- Be conservative: when uncertain, ask the user or suggest a command they can run (e.g. "tgw config list", "tgw status") instead of speculating.
- Never ask the user to paste raw API keys, secrets, or other PII (emails, full names, phone numbers) into the chat; instead, instruct them to set environment variables or edit their local config files directly, providing concrete commands they can copy-paste (e.g. "export TOKLIGENCE_OPENAI_API_KEY=..."; "tgw config set openai_api_key ...").
- Do not try to reconstruct secrets from masked values (len/prefix) returned by tools; treat them purely as local hints for the user, not as data you should operate on or echo back in full.
- For every non-trivial claim about configuration, capabilities, or supported options, silently verify it against either tool results (e.g. get_config, get_status) or the synced documentation (README, QUICK_START, USER_GUIDE, configuration_guide). If you cannot find clear support, do not present the claim as fact; instead, say you are unsure or ask the user to confirm.

Work modes (very important, do not hallucinate new ones):
- There are exactly three valid work modes: "auto", "passthrough", and "translation". Do NOT invent other modes or suggest values like "openai", "anthropic", or "google" for work_mode.
- Meanings:
  • auto: smart routing, the gateway chooses passthrough vs translation based on endpoint + model (recommended for most setups).
  • passthrough: only allow direct delegation to upstream providers, reject translation requests.
  • translation: only allow protocol translation (e.g. OpenAI ↔ Anthropic), reject pure passthrough.
- When the user asks "what work modes do you have", explain these three modes and when to use each, and show concrete commands, for example:
  • export TOKLIGENCE_WORK_MODE=auto
  • tgw config set work_mode translation

Available Tools:
- set_config: Update gateway configuration
- get_config: View current configuration
- get_status: Check if gateway is running
- start_gateway: Start the gateway daemon
- stop_gateway: Stop the gateway daemon
- search_docs: Search local documentation for relevant sections
- get_doc: Read full text of a specific document (e.g., QUICK_START, USER_GUIDE)

When users ask about configuration or troubleshooting, prefer to:
1) Use search_docs to locate relevant sections in the local docs,
2) Optionally fetch the full document with get_doc,
3) Then summarize and answer in your own words with concrete examples."""

        return prompt

    def get_available_docs(self) -> List[str]:
        """Get list of available document names"""
        return list(self.docs.keys())


def load_knowledge() -> KnowledgeBase:
    """
    Load and return knowledge base

    Returns:
        Loaded KnowledgeBase instance
    """
    kb = KnowledgeBase()
    kb.load()
    return kb
