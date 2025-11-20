"""
CLI interface for tokligence
"""

import click
import sys
import json
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from .gateway import Gateway
from .daemon import Daemon
from .config import load_config, save_config

console = Console()


@click.group()
@click.option('--config', help='Configuration file path')
@click.pass_context
def cli(ctx, config):
    """Tokligence Gateway - Multi-platform LLM gateway CLI"""
    ctx.ensure_object(dict)
    ctx.obj['config_path'] = config
    # Detect if called as 'tgw' or 'tokligence'
    import sys
    import os
    ctx.obj['program_name'] = os.path.basename(sys.argv[0]) if sys.argv else 'tokligence'


@cli.group()
@click.pass_context
def user(ctx):
    """User management commands"""
    pass


@user.command('create')
@click.argument('username')
@click.option('--email', help='User email address')
@click.pass_context
def user_create(ctx, username, email):
    """Create a new user"""
    gateway = Gateway(config_path=ctx.obj.get('config_path'))
    try:
        result = gateway.create_user(username, email)
        console.print(Panel(f"✅ User created: {username}", style="green"))
        if isinstance(result, dict) and 'id' in result:
            console.print(f"User ID: {result['id']}")
    except Exception as e:
        console.print(Panel(f"❌ Error: {e}", style="red"))
        sys.exit(1)


@user.command('list')
@click.option('--json', 'as_json', is_flag=True, help='Output as JSON')
@click.pass_context
def user_list(ctx, as_json):
    """List all users"""
    gateway = Gateway(config_path=ctx.obj.get('config_path'))
    try:
        users = gateway.list_users()

        if as_json:
            click.echo(json.dumps(users, indent=2))
        else:
            table = Table(title="Users")
            table.add_column("ID", style="cyan")
            table.add_column("Username", style="magenta")
            table.add_column("Email", style="green")
            table.add_column("Created", style="yellow")

            for user in users:
                table.add_row(
                    str(user.get('id', '')),
                    user.get('username', ''),
                    user.get('email', ''),
                    user.get('created_at', '')
                )

            console.print(table)
    except Exception as e:
        console.print(Panel(f"❌ Error: {e}", style="red"))
        sys.exit(1)


@cli.group()
@click.pass_context
def apikey(ctx):
    """API key management commands"""
    pass


@apikey.command('create')
@click.argument('user_id')
@click.option('--name', help='Key name/description')
@click.pass_context
def apikey_create(ctx, user_id, name):
    """Create an API key for a user"""
    gateway = Gateway(config_path=ctx.obj.get('config_path'))
    try:
        result = gateway.create_api_key(user_id, name)
        console.print(Panel("✅ API Key created", style="green"))
        if isinstance(result, dict) and 'key' in result:
            console.print(f"[bold yellow]API Key:[/bold yellow] {result['key']}")
            console.print("[dim]Please save this key securely. It won't be shown again.[/dim]")
    except Exception as e:
        console.print(Panel(f"❌ Error: {e}", style="red"))
        sys.exit(1)


@cli.command()
@click.pass_context
def init(ctx):
    """Initialize gateway configuration"""
    gateway = Gateway(config_path=ctx.obj.get('config_path'))
    try:
        if gateway.init():
            console.print(Panel("✅ Configuration initialized", style="green"))
        else:
            console.print(Panel("❌ Configuration initialization failed", style="red"))
            sys.exit(1)
    except Exception as e:
        console.print(Panel(f"❌ Error: {e}", style="red"))
        sys.exit(1)


@cli.group()
@click.pass_context
def daemon(ctx):
    """Daemon control commands"""
    pass


@daemon.command('start')
@click.option('--port', default=8081, help='Port to listen on')
@click.option('--background', is_flag=True, help='Run in background')
@click.pass_context
def daemon_start(ctx, port, background):
    """Start the gateway daemon"""
    d = Daemon(config_path=ctx.obj.get('config_path'), port=port)

    if background:
        console.print(f"Starting daemon on port {port} (background)...")
        d.start(background=True)
    else:
        console.print(f"Starting daemon on port {port}...")
        console.print("[dim]Press Ctrl+C to stop[/dim]")
        try:
            process = d.start()
            if process:
                process.wait()
        except KeyboardInterrupt:
            console.print("\n[yellow]Stopping daemon...[/yellow]")
            d.stop()


@daemon.command('stop')
@click.pass_context
def daemon_stop(ctx):
    """Stop the gateway daemon"""
    d = Daemon(config_path=ctx.obj.get('config_path'))
    d.stop()
    console.print(Panel("✅ Daemon stopped", style="green"))


@daemon.command('restart')
@click.option('--port', default=8081, help='Port to listen on')
@click.pass_context
def daemon_restart(ctx, port):
    """Restart the gateway daemon"""
    d = Daemon(config_path=ctx.obj.get('config_path'), port=port)
    console.print("Restarting daemon...")
    d.restart()
    console.print(Panel("✅ Daemon restarted", style="green"))


@daemon.command('status')
@click.pass_context
def daemon_status(ctx):
    """Check daemon status"""
    d = Daemon(config_path=ctx.obj.get('config_path'))
    status = d.status()

    if status['status'] == 'running':
        console.print(Panel(f"✅ Daemon is running", style="green"))
        if status.get('pid'):
            console.print(f"PID: {status['pid']}")
        if status.get('port'):
            console.print(f"Port: {status['port']}")
    else:
        console.print(Panel("⚠️ Daemon is not running", style="yellow"))


@cli.command()
@click.option('--user', help='Filter by user ID')
@click.option('--json', 'as_json', is_flag=True, help='Output as JSON')
@click.pass_context
def usage(ctx, user, as_json):
    """Show usage statistics"""
    gateway = Gateway(config_path=ctx.obj.get('config_path'))
    try:
        stats = gateway.get_usage(user_id=user)

        if as_json:
            click.echo(json.dumps(stats, indent=2))
        else:
            console.print(Panel("📊 Usage Statistics", style="cyan"))
            for key, value in stats.items():
                console.print(f"{key}: {value}")
    except Exception as e:
        console.print(Panel(f"❌ Error: {e}", style="red"))
        sys.exit(1)


@cli.command()
@click.pass_context
def version(ctx):
    """Show version information"""
    from . import __version__
    console.print(f"Tokligence Gateway version: {__version__}")


@cli.command()
@click.option('--model', help='Preferred LLM model to use (e.g., gpt-4, claude-sonnet-4.5)')
@click.pass_context
def chat(ctx, model):
    """Interactive AI assistant for Tokligence Gateway configuration and help

    The chat assistant helps you configure and troubleshoot Tokligence Gateway
    using an interactive AI-powered conversation. It can:

    - Answer questions about configuration
    - Help set up providers (OpenAI, Anthropic, Google)
    - Troubleshoot issues
    - Execute configuration commands
    - Search and reference official documentation

    The assistant requires a local or remote LLM endpoint (OpenAI API, Anthropic API,
    Gemini API, or local LLMs via Ollama/vLLM/LM Studio).
    """
    try:
        # Import chat module (will create it next)
        from .chat import start_chat
        start_chat(model=model)
    except ImportError:
        console.print(Panel(
            "❌ Chat feature requires additional dependencies.\n"
            "Install with: pip install tokligence[chat]",
            style="red"
        ))
        sys.exit(1)
    except Exception as e:
        console.print(Panel(f"❌ Error starting chat: {e}", style="red"))
        sys.exit(1)


def main():
    """Main entry point"""
    cli(obj={})


if __name__ == '__main__':
    main()