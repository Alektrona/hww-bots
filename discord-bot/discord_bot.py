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
from datetime import datetime
import json

# Configuration from environment variables
DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
DISCORD_GUILD_ID = int(os.environ.get('DISCORD_GUILD_ID', '0'))
LOG_CHANNEL_ID = int(os.environ.get('LOG_CHANNEL_ID', '0'))
ALERT_CHANNEL_ID = int(os.environ.get('ALERT_CHANNEL_ID', '0'))
WEREBOT_CONTAINER_NAME = os.environ.get('WEREBOT_CONTAINER_NAME', 'werebot')
MOD_ROLE_NAMES = os.environ.get('MOD_ROLE_NAMES', 'PermaMods,AlumniMods').split(',')  # Multiple mod roles

# Werebot log file path (mounted volume)
WEREBOT_LOG_FILE = os.environ.get('WEREBOT_LOG_FILE', '/shared/werebot/data/werebot.log')

# Werebot feature flags file (shared volume)
WEREBOT_FEATURES_FILE = os.environ.get('WEREBOT_FEATURES_FILE', '/shared/werebot/data/feature_flags.json')

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
    """Check if user has any mod role (PermaMods or AlumniMods)"""
    async def predicate(ctx):
        if not ctx.guild:
            return False
        # Check if user has any of the mod roles
        for role_name in MOD_ROLE_NAMES:
            role = discord.utils.get(ctx.guild.roles, name=role_name.strip())
            if role and role in ctx.author.roles:
                return True
        return False
    return commands.check(predicate)


class DockerManager:
    """Helper class for Docker command interactions"""
    
    async def run_command(self, command):
        """Run a shell command and return output"""
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        return proc.returncode, stdout.decode(), stderr.decode()
    
    async def get_container_id(self, container_name):
        """Get container ID by name"""
        returncode, stdout, stderr = await self.run_command(
            f"docker ps -a --filter name={container_name} --format '{{{{.ID}}}}'"
        )
        
        if returncode != 0 or not stdout.strip():
            return None
        
        # Return first matching container ID
        return stdout.strip().split('\n')[0]
    
    async def restart_container(self, container_name):
        """Restart a container by name"""
        # First check if container exists
        container_id = await self.get_container_id(container_name)
        if not container_id:
            return False, "Container not found"
        
        # Restart the container
        returncode, stdout, stderr = await self.run_command(f"docker restart {container_name}")
        
        if returncode == 0:
            return True, "Container restarted successfully"
        else:
            return False, f"Restart failed: {stderr}"
    
    async def stop_container(self, container_name):
        """Stop a container by name"""
        # First check if container exists
        container_id = await self.get_container_id(container_name)
        if not container_id:
            return False, "Container not found"
        
        # Stop the container
        returncode, stdout, stderr = await self.run_command(f"docker stop {container_name}")
        
        if returncode == 0:
            return True, "Container stopped successfully"
        else:
            return False, f"Stop failed: {stderr}"
    
    async def start_container(self, container_name):
        """Start a container by name"""
        # First check if container exists
        container_id = await self.get_container_id(container_name)
        if not container_id:
            return False, "Container not found"
        
        # Start the container
        returncode, stdout, stderr = await self.run_command(f"docker start {container_name}")
        
        if returncode == 0:
            return True, "Container started successfully"
        else:
            return False, f"Start failed: {stderr}"
    
    async def get_container_status(self, container_name):
        """Get container status"""
        container_id = await self.get_container_id(container_name)
        if not container_id:
            return None, "Container not found"
        
        # Get container inspect data
        returncode, stdout, stderr = await self.run_command(
            f"docker inspect {container_name}"
        )
        
        if returncode != 0:
            return None, f"Failed to get status: {stderr}"
        
        try:
            import json
            data = json.loads(stdout)[0]
            state = data.get('State', {})
            
            return {
                'status': state.get('Status'),
                'running': state.get('Running', False),
                'started_at': state.get('StartedAt'),
                'finished_at': state.get('FinishedAt'),
                'exit_code': state.get('ExitCode'),
            }, None
        except (json.JSONDecodeError, IndexError, KeyError) as e:
            return None, f"Failed to parse status: {e}"


docker_manager = DockerManager()


class FeatureManager:
    """Helper class for managing Werebot feature flags"""
    
    DEFAULT_FEATURES = {
        'vote_system': True,
        'random': True,
        'k9_mode': True,
        'easter_eggs': True,
        'tagging': True
    }
    
    FEATURE_DESCRIPTIONS = {
        'vote_system': 'Vote tracking (VOTE, UNVOTE, TALLY commands)',
        'random': 'Random picker (RANDOM command)',
        'k9_mode': 'K9 emoji mode (K9 command)',
        'easter_eggs': 'Fun easter egg responses',
        'tagging': 'User tagging system (main WEREBOT functionality)'
    }
    
    def get_features(self):
        """Load feature flags from file"""
        if not os.path.exists(WEREBOT_FEATURES_FILE):
            return self.DEFAULT_FEATURES.copy()
        
        try:
            with open(WEREBOT_FEATURES_FILE, 'r') as f:
                features = json.load(f)
                # Merge with defaults to ensure all features exist
                return {**self.DEFAULT_FEATURES, **features}
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading features: {e}")
            return self.DEFAULT_FEATURES.copy()
    
    def save_features(self, features):
        """Save feature flags to file"""
        try:
            with open(WEREBOT_FEATURES_FILE, 'w') as f:
                json.dump(features, f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving features: {e}")
            return False
    
    def toggle_feature(self, feature_name, enabled):
        """Enable or disable a feature"""
        if feature_name not in self.DEFAULT_FEATURES:
            return False, f"Unknown feature: {feature_name}"
        
        features = self.get_features()
        features[feature_name] = enabled
        
        if self.save_features(features):
            state = "enabled" if enabled else "disabled"
            return True, f"Feature '{feature_name}' {state}"
        else:
            return False, "Failed to save feature flags"


feature_manager = FeatureManager()


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
    status, error = await docker_manager.get_container_status(WEREBOT_CONTAINER_NAME)
    
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
    msg = await ctx.send("🔄 Restarting Werebot...")
    
    # Restart container
    success, message = await docker_manager.restart_container(WEREBOT_CONTAINER_NAME)
    
    if success:
        embed = discord.Embed(
            title="✅ Restart Successful",
            description=message,
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Restarted by {ctx.author.display_name}")
    else:
        embed = discord.Embed(
            title="❌ Restart Failed",
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
                title="🔄 Bot Restart Triggered",
                description=f"Werebot restarted by {ctx.author.mention}",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            await log_channel.send(embed=log_embed)


@bot.command(name='stop')
@is_mod()
async def stop_bot(ctx):
    """Stop Werebot (Emergency kill switch - Mods only)"""
    # Send initial message
    msg = await ctx.send("🛑 Stopping Werebot...")
    
    # Stop container
    success, message = await docker_manager.stop_container(WEREBOT_CONTAINER_NAME)
    
    if success:
        embed = discord.Embed(
            title="🛑 Bot Stopped",
            description=f"{message}\n\n⚠️ Use `!werebot start` to restart the bot.",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Stopped by {ctx.author.display_name}")
    else:
        embed = discord.Embed(
            title="❌ Stop Failed",
            description=message,
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
    
    await msg.edit(content=None, embed=embed)
    
    # Log to channel
    if success and LOG_CHANNEL_ID:
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="🛑 Bot Stopped",
                description=f"⚠️ Werebot stopped by {ctx.author.mention}",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            await log_channel.send(embed=log_embed)


@bot.command(name='start')
@is_mod()
async def start_bot(ctx):
    """Start Werebot (Mods only)"""
    # Send initial message
    msg = await ctx.send("▶️ Starting Werebot...")
    
    # Start container
    success, message = await docker_manager.start_container(WEREBOT_CONTAINER_NAME)
    
    if success:
        embed = discord.Embed(
            title="✅ Bot Started",
            description=message,
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Started by {ctx.author.display_name}")
    else:
        embed = discord.Embed(
            title="❌ Start Failed",
            description=message,
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
    
    await msg.edit(content=None, embed=embed)
    
    # Log to channel
    if success and LOG_CHANNEL_ID:
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="▶️ Bot Started",
                description=f"Werebot started by {ctx.author.mention}",
                color=discord.Color.green(),
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


@bot.command(name='features')
async def list_features(ctx):
    """Show current feature status"""
    features = feature_manager.get_features()
    
    embed = discord.Embed(
        title="🎛️ Werebot Features",
        description="Current feature toggle states",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )
    
    for feature, enabled in sorted(features.items()):
        status = "✅ Enabled" if enabled else "❌ Disabled"
        description = feature_manager.FEATURE_DESCRIPTIONS.get(feature, "No description")
        embed.add_field(
            name=f"{status} - {feature}",
            value=description,
            inline=False
        )
    
    embed.set_footer(text="Use !werebot enable/disable <feature> to toggle")
    await ctx.send(embed=embed)


@bot.command(name='enable')
@is_mod()
async def enable_feature(ctx, feature: str):
    """Enable a Werebot feature (Mods only)"""
    success, message = feature_manager.toggle_feature(feature, True)
    
    if success:
        embed = discord.Embed(
            title="✅ Feature Enabled",
            description=message,
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Enabled by {ctx.author.display_name}")
    else:
        embed = discord.Embed(
            title="❌ Error",
            description=message,
            color=discord.Color.red()
        )
    
    await ctx.send(embed=embed)
    
    # Log to channel
    if success and LOG_CHANNEL_ID:
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="Feature Toggled",
                description=f"{ctx.author.mention} enabled '{feature}'",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            await log_channel.send(embed=log_embed)


@bot.command(name='disable')
@is_mod()
async def disable_feature(ctx, feature: str):
    """Disable a Werebot feature (Mods only)"""
    success, message = feature_manager.toggle_feature(feature, False)
    
    if success:
        embed = discord.Embed(
            title="❌ Feature Disabled",
            description=message,
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Disabled by {ctx.author.display_name}")
    else:
        embed = discord.Embed(
            title="❌ Error",
            description=message,
            color=discord.Color.red()
        )
    
    await ctx.send(embed=embed)
    
    # Log to channel
    if success and LOG_CHANNEL_ID:
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="Feature Toggled",
                description=f"{ctx.author.mention} disabled '{feature}'",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            await log_channel.send(embed=log_embed)


@bot.command(name='bothelp')
async def bot_help(ctx):
    """Show available commands"""
    embed = discord.Embed(
        title="🤖 Werebot Manager Commands",
        description="Available commands for managing Werebot",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="!werebot status",
        value="Check if Werebot is running",
        inline=False
    )
    
    embed.add_field(
        name="!werebot stop",
        value="🛑 Stop Werebot (Emergency kill switch - Mods only)",
        inline=False
    )
    
    embed.add_field(
        name="!werebot start",
        value="▶️ Start Werebot (Mods only)",
        inline=False
    )
    
    embed.add_field(
        name="!werebot restart",
        value="🔄 Restart Werebot (Mods only)",
        inline=False
    )
    
    embed.add_field(
        name="!werebot tail [lines]",
        value="Show last N lines of logs (Mods only, default 20, max 50)",
        inline=False
    )
    
    embed.add_field(
        name="!werebot features",
        value="Show all features and their current status",
        inline=False
    )
    
    embed.add_field(
        name="!werebot enable <feature>",
        value="Enable a Werebot feature (Mods only)",
        inline=False
    )
    
    embed.add_field(
        name="!werebot disable <feature>",
        value="Disable a Werebot feature (Mods only)",
        inline=False
    )
    
    embed.add_field(
        name="!werebot bothelp",
        value="Show this help message",
        inline=False
    )
    
    embed.set_footer(text="Logs are automatically posted to the log channel")
    
    await ctx.send(embed=embed)


@restart_bot.error
@stop_bot.error
@start_bot.error
@tail_logs.error
@enable_feature.error
@disable_feature.error
async def mod_command_error(ctx, error):
    """Handle errors for mod-only commands"""
    if isinstance(error, commands.CheckFailure):
        await ctx.send("❌ This command requires the PermaMods or AlumniMods role")
    else:
        await ctx.send(f"An error occurred: {error}")


def main():
    if not DISCORD_TOKEN:
        print("ERROR: DISCORD_BOT_TOKEN environment variable not set")
        return
    
    print("Starting Discord bot...")
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()