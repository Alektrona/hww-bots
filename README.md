# Hidden Werewolves Bot Suite

Reddit and Discord bots for the r/HiddenWerewolves gaming community.

## Bots Included

### Werebot
Reddit bot for tagging users in game threads with advanced features.

**Features:**
- User tagging (mention 4+ users at once)
- Vote tracking (declare and tally votes)
- K9 mode (cryptic emoji messages)
- Random picker
- Thread-specific snooze
- Nickname mapping via Google Sheets
- Subscribe/unsubscribe

[Were-Bot Documentation](./werebot/README.md)

### HWWBot
Reddit bot for managing AutoModerator configurations.

**Features:**
- Update AutoMod rules via Reddit comments
- Template management
- Version control for configs

[HWWBot Documentation](./hwwbot/)

### Discord Monitor Bot
Discord bot for monitoring and managing the Reddit bots.

**Features:**
- Real-time log posting to Discord
- Error alerts
- Remote bot restart (mods only)
- Status checks

[Discord Bot Documentation](./discord-bot/README.md)

## Quick Start

### Prerequisites

- Python 3.11+
- Reddit app credentials
- Discord bot token (for monitoring)
- Portainer access (for deployment)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/hww-bots.git
cd hww-bots
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up credentials:**
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. **Deploy to Portainer:**

See [Portainer Deployment Guide](./deployment/PORTAINER_DEPLOYMENT_GUIDE.md)

## Repository Structure

```
hww-bots/
├── werebot/              # Were-Bot (user tagging)
├── hwwbot/               # HWWBot (AutoMod manager)
├── discord-bot/          # Discord monitoring bot
├── deployment/           # Deployment guides
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore rules
└── .env.example         # Environment variables template
```

## Configuration

All bots use environment variables for configuration. See `.env.example` for required variables.

**Never commit:**
- `.env` file
- `creds*.json` files
- Any files with credentials

## Deployment

The bots are designed to run in Docker containers via Portainer.

See the [Portainer Deployment Guide](./deployment/PORTAINER_DEPLOYMENT_GUIDE.md) for complete setup instructions.

### Docker Compose

A complete `docker-compose.yml` is provided for deploying all bots together.

## Development

### Making Changes

1. Edit bot files locally
2. Test changes
3. Commit to git
4. Deploy to server (via git pull or file upload)
5. Restart containers in Portainer

### Adding Features

Each bot has its own directory with documentation. See individual README files for bot-specific development info.

## Documentation

- **Were-Bot:** [werebot/README.md](./werebot/README.md)
  - [Vote Tracking Guide](./werebot/WEREBOT_VOTE_TRACKING_GUIDE.md)
  - [K9 Mode Guide](./werebot/WEREBOT_K9_MODE_UPDATED.md)
  - [Snooze Guide](./werebot/WEREBOT_SNOOZE_GUIDE.md)
  - [Random Picker Guide](./werebot/WEREBOT_RANDOM_GUIDE.md)
  - [Nickname Mapping](./werebot/NICKNAME_MAPPING_GUIDE.md)

- **Discord Bot:** [discord-bot/README.md](./discord-bot/README.md)

- **Deployment:** [deployment/PORTAINER_DEPLOYMENT_GUIDE.md](./deployment/PORTAINER_DEPLOYMENT_GUIDE.md)

## Support

For issues or questions about the bots, please:
1. Check the documentation
2. Review the bot logs in Portainer or Discord
3. Open an issue on GitHub

## License

This project is for use by the Hidden Werewolves community.

## Credits

Created by /u/pezes

Updates and discord integration by /u/Penultima

Maintained by the r/HiddenWerewolves mod team.

Special thanks to /u/K9moonmoon for inspiring the K9 mode feature! 
