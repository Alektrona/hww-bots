"""
Discord Bot for Monitoring and Managing Were-Bot

Features:
- Posts bot logs to Discord channel
- Allows mods to restart bot via commands
- Shows bot status
- Alerts on errors
"""

import discord
from discord.ext import commands, tasks
import os
import asyncio
import aiohttp
from datetime import datetime
import json

# Configuration from environment variables
DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
DISCORD_GUILD_ID = int(os.environ.get('DISCORD_GUILD_ID', '0'))
LOG_CHANNEL_ID = int(os.environ.get('LOG_CHANNEL_ID', '0'))
ALERT_CHANNEL_ID = int(os.environ.get('ALERT_CHANNEL_ID', '0'))
PORTAINER_URL = os.environ.get('PORTAINER_URL', 'https://oracle.hufflepuff.fun:9443')
PORTAINER_API_KEY = os.environ.get('PORTAINER_API_KEY', '')
WEREBOT_CONTAINER_NAME = os.environ.get('WEREBOT_CONTAINER_NAME', 'werebot')
MOD_ROLE_NAME = os.environ.get('MOD_ROLE_NAME', 'PermaMods')

# Werebot log file path (mounted volume)
WEREBOT_LOG_FILE = os.environ.get('WEREBOT_LOG_FILE', '/shared/werebot/data/werebot.log')

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!werebot ', intents=intents)

# Track last log position
last_log_position = 0
last_error_time = None


def is_mod():
    """Check if user has mod role"""
    async def predicate(ctx):
        if not ctx.guild:
            return False
        role = discord.utils.get(ctx.guild.roles, name=MOD_ROLE_NAME)
        return role in ctx.author.roles
    return commands.check(predicate)


class PortainerAPI:
    """Helper class for Portainer API interactions"""
    
    def __init__(self, url, api_key):
        self.url = url.rstrip('/')
        self.api_key = api_key
        self.headers = {'X-API-Key': api_key}
    
    async def get_container_id(self, container_name):
        """Get container ID by name"""
        async with aiohttp.ClientSession() as session:
            # Get endpoint ID (usually 1 for local)
            endpoint_url = f"{self.url}/api/endpoints"
            async with session.get(endpoint_url, headers=self.headers, ssl=False) as resp:
                if resp.status != 200:
                    return None
                endpoints = await resp.json()
                endpoint_id = endpoints[0]['Id'] if endpoints else 1
            
            # Get containers
            containers_url = f"{self.url}/api/endpoints/{endpoint_id}/docker/containers/json?all=1"
            async with session.get(containers_url, headers=self.headers, ssl=False) as resp:
                if resp.status != 200:
                    return None
                containers = await resp.json()
                
                # Find container by name
                for container in containers:
                    names = container.get('Names', [])
                    if any(container_name in name for name in names):
                        return container['Id']
                
                return None
    
    async def restart_container(self, container_name):
        """Restart a container by name"""
        container_id = await self.get_container_id(container_name)
        if not container_id:
            return False, "Container not found"
        
        async with aiohttp.ClientSession() as session:
            # Get endpoint ID
            endpoint_url = f"{self.url}/api/endpoints"
            async with session.get(endpoint_url, headers=self.headers, ssl=False) as resp:
                if resp.status != 200:
                    return False, "Failed to get endpoint"
                endpoints = await resp.json()
                endpoint_id = endpoints[0]['Id'] if endpoints else 1
            
            # Restart container
            restart_url = f"{self.url}/api/endpoints/{endpoint_id}/docker/containers/{container_id}/restart"
            async with session.post(restart_url, headers=self.headers, ssl=False) as resp:
                if resp.status in (200, 204):
                    return True, "Container restarted successfully"
                else:
                    return False, f"Restart failed: {resp.status}"
    
    async def get_container_status(self, container_name):
        """Get container status"""
        container_id = await self.get_container_id(container_name)
        if not container_id:
            return None, "Container not found"
        
        async with aiohttp.ClientSession() as session:
            # Get endpoint ID
            endpoint_url = f"{self.url}/api/endpoints"
            async with session.get(endpoint_url, headers=self.headers, ssl=False) as resp:
                if resp.status != 200:
                    return None, "Failed to get endpoint"
                endpoints = await resp.json()
                endpoint_id = endpoints[0]['Id'] if endpoints else 1
            
            # Get container info
            inspect_url = f"{self.url}/api/endpoints/{endpoint_id}/docker/containers/{container_id}/json"
            async with session.get(inspect_url, headers=self.headers, ssl=False) as resp:
                if resp.status != 200:
                    return None, f"Failed to get status: {resp.status}"
                
                data = await resp.json()
                state = data.get('State', {})
                
                return {
                    'status': state.get('Status'),
                    'running': state.get('Running', False),
                    'started_at': state.get('StartedAt'),
                    'finished_at': state.get('FinishedAt'),
                    'exit_code': state.get('ExitCode'),
                }, None


portainer = PortainerAPI(PORTAINER_URL, PORTAINER_API_KEY)


@bot.event
async def on_ready():
    global last_log_position
    
    print(f'{bot.user} has connected to Discord!')
    print(f'Monitoring Werebot logs at: {WEREBOT_LOG_FILE}')
    
    # Seek to end of log file so we don't repost old logs
    if os.path.exists(WEREBOT_LOG_FILE):
        with open(WEREBOT_LOG_FILE, 'r') as f:
            f.seek(0, 2)  # Seek to end
            last_log_position = f.tell()
        print(f'Starting log monitoring from position: {last_log_position}')
    
    # Start background tasks
    check_logs.start()
    
    # Send startup message
    if LOG_CHANNEL_ID:
        channel = bot.get_channel(LOG_CHANNEL_ID)
        if channel:
            embed = discord.Embed(
                title="Discord Bot Online",
                description="Werebot monitoring active (monitoring new logs only)",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            await channel.send(embed=embed)


@tasks.loop(seconds=10)
async def check_logs():
    """Check Were-Bot logs and post new entries to Discord"""
    global last_log_position
    
    if not LOG_CHANNEL_ID:
        return
    
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if not channel:
        return
    
    try:
        # Check if log file exists
        if not os.path.exists(WEREBOT_LOG_FILE):
            return
        
        # Read new log entries
        with open(WEREBOT_LOG_FILE, 'r') as f:
            f.seek(last_log_position)
            new_lines = f.readlines()
            last_log_position = f.tell()
        
        if not new_lines:
            return
        
        # Group lines and send
        batch = []
        for line in new_lines:
            line = line.strip()
            if not line:
                continue
            
            batch.append(line)
            
            # Send batch if it's getting large
            if len(batch) >= 10:
                await send_log_batch(channel, batch)
                batch = []
        
        # Send remaining
        if batch:
            await send_log_batch(channel, batch)
    
    except Exception as e:
        print(f"Error checking logs: {e}")


async def send_log_batch(channel, lines):
    """Send a batch of log lines to Discord"""
    global last_error_time
    
    # Check for errors
    has_error = any('ERROR' in line or 'CRITICAL' in line for line in lines)
    has_warning = any('WARNING' in line for line in lines)
    
    # Combine lines
    log_text = '\n'.join(lines)
    
    # Truncate if too long
    if len(log_text) > 1900:
        log_text = log_text[:1900] + '\n... (truncated)'
    
    # Color based on severity
    if has_error:
        color = discord.Color.red()
        title = "🔴 Werebot Error"
    elif has_warning:
        color = discord.Color.orange()
        title = "⚠️ Werebot Warning"
    else:
        color = discord.Color.blue()
        title = "Werebot Logs"
    
    embed = discord.Embed(
        title=title,
        description=f"```\n{log_text}\n```",
        color=color,
        timestamp=datetime.utcnow()
    )
    
    await channel.send(embed=embed)
    
    # Send alert for errors
    if has_error and ALERT_CHANNEL_ID:
        alert_channel = bot.get_channel(ALERT_CHANNEL_ID)
        if alert_channel:
            # Rate limit alerts (don't spam)
            now = datetime.utcnow()
            if last_error_time is None or (now - last_error_time).total_seconds() > 300:
                last_error_time = now
                
                alert_embed = discord.Embed(
                    title="Werebot Error Alert",
                    description="An error was detected in Werebot logs. Check the log channel for details.",
                    color=discord.Color.red(),
                    timestamp=datetime.utcnow()
                )
                await alert_channel.send(embed=alert_embed)


@bot.command(name='status')
async def bot_status(ctx):
    """Check Werebot status"""
    status, error = await portainer.get_container_status(WEREBOT_CONTAINER_NAME)
    
    if error:
        embed = discord.Embed(
            title="Error",
            description=error,
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Format status
    running = status.get('running', False)
    state = status.get('status', 'unknown')
    
    if running:
        color = discord.Color.green()
        emoji = "✅"
    else:
        color = discord.Color.red()
        emoji = "❌"
    
    embed = discord.Embed(
        title=f"{emoji} Were-Bot Status",
        color=color,
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(name="Status", value=state.upper(), inline=True)
    embed.add_field(name="Running", value="Yes" if running else "No", inline=True)
    
    if status.get('started_at'):
        embed.add_field(name="Started At", value=status['started_at'], inline=False)
    
    await ctx.send(embed=embed)


@bot.command(name='restart')
@is_mod()
async def restart_bot(ctx):
    """Restart Werebot (Mods only)"""
    # Send initial message
    msg = await ctx.send("Restarting Werebot...")
    
    # Restart container
    success, message = await portainer.restart_container(WEREBOT_CONTAINER_NAME)
    
    if success:
        embed = discord.Embed(
            title="Restart Successful",
            description=message,
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Restarted by {ctx.author.display_name}")
    else:
        embed = discord.Embed(
            title="Restart Failed",
            description=message,
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
    
    await msg.edit(content=None, embed=embed)
    
    # Log to channel
    if LOG_CHANNEL_ID:
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="Bot Restart Triggered",
                description=f"Werebot restarted by {ctx.author.mention}",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            await log_channel.send(embed=log_embed)


@bot.command(name='tail')
@is_mod()
async def tail_logs(ctx, lines: int = 20):
    """Show last N lines of Werebot logs (Mods only)"""
    if lines > 50:
        lines = 50
    
    try:
        if not os.path.exists(WEREBOT_LOG_FILE):
            await ctx.send("Log file not found")
            return
        
        # Read last N lines
        with open(WEREBOT_LOG_FILE, 'r') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:]
        
        log_text = ''.join(recent_lines)
        
        # Truncate if needed
        if len(log_text) > 1900:
            log_text = log_text[-1900:]
            log_text = "... (truncated)\n" + log_text
        
        embed = discord.Embed(
            title=f"Last {lines} Log Lines",
            description=f"```\n{log_text}\n```",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        await ctx.send(embed=embed)
    
    except Exception as e:
        await ctx.send(f"Error reading logs: {e}")


@bot.command(name='bothelp')
async def bot_help(ctx):
    """Show available commands"""
    embed = discord.Embed(
        title="Werebot Manager Commands",
        description="Available commands for managing Werebot",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="!werebot status",
        value="Check if Werebot is running",
        inline=False
    )
    
    embed.add_field(
        name="!werebot restart",
        value="Restart Werebot (Mods only)",
        inline=False
    )
    
    embed.add_field(
        name="!werebot tail [lines]",
        value="Show last N lines of logs (Mods only, default 20, max 50)",
        inline=False
    )
    
    embed.add_field(
        name="!werebot help",
        value="Show this help message",
        inline=False
    )
    
    embed.set_footer(text="Logs are automatically posted to the log channel")
    
    await ctx.send(embed=embed)


@restart_bot.error
@tail_logs.error
async def mod_command_error(ctx, error):
    """Handle errors for mod-only commands"""
    if isinstance(error, commands.CheckFailure):
        await ctx.send("This command requires the Moderator role")
    else:
        await ctx.send(f"An error occurred: {error}")


def main():
    if not DISCORD_TOKEN:
        print("ERROR: DISCORD_BOT_TOKEN environment variable not set")
        return
    
    if not PORTAINER_API_KEY:
        print("WARNING: PORTAINER_API_KEY not set, restart functionality will not work")
    
    print("Starting Discord bot...")
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()