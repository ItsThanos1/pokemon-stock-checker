# Quick Setup Instructions 🚀

## ⚠️ IMPORTANT: Discord Token Issue

The token you provided appears to be a webhook token, not a bot token. Here's what you need to do:

### For Webhook Notifications ONLY (No Commands)

If you only want notifications without bot commands, the current webhook URL will work fine! The bot will still send alerts when Pokemon are in stock.

### For Bot Commands (Recommended)

To use bot commands like `!check`, `!history`, etc., you need to:

1. **Create a Discord Bot Application:**
   - Go to https://discord.com/developers/applications
   - Click "New Application"
   - Give it a name (e.g., "Pokemon Stock Bot")
   - Go to the "Bot" section
   - Click "Add Bot"
   - Under "Privileged Gateway Intents", enable:
     - ✅ Message Content Intent
     - ✅ Server Members Intent (optional)
   - Copy the Bot Token (starts with something like `MTAy...`)

2. **Invite the Bot to Your Server:**
   - Go to OAuth2 → URL Generator
   - Select scopes: `bot`
   - Select permissions: 
     - Send Messages
     - Read Message History
     - Use Slash Commands
   - Copy the generated URL and open it in browser
   - Select your server and authorize

3. **Update the Code:**
   - Replace `DISCORD_BOT_TOKEN` in the code with your actual bot token

### Webhook vs Bot Token

- **Webhook Token**: For sending messages TO Discord (one-way)
- **Bot Token**: For sending AND receiving messages (two-way, needed for commands)

## Quick Install 📥

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python pokemonv1.py
```

## First Time Setup Checklist ✅

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Discord webhook URL configured (for notifications)
- [ ] Discord bot token configured (for commands) - OPTIONAL
- [ ] Zip code set in code (default: 90210)
- [ ] Bot invited to your Discord server (if using commands)

## Testing 🧪

### Test Webhook (No Bot Token Needed)
1. Run the script
2. You should see a "Bot Started" message in Discord
3. Wait for scan notifications

### Test Bot Commands (Requires Bot Token)
1. Run the script
2. In Discord, type: `!help`
3. Try: `!check 6548368`
4. Try: `!status`

## Configuration Options ⚙️

Edit these in `pokemonv1.py`:

```python
# Line 11-12: Discord Configuration
DISCORD_WEBHOOK_URL = "your_webhook_url_here"
DISCORD_BOT_TOKEN = "your_bot_token_here"  # Different from webhook!

# Line 48: Default search location
DEFAULT_ZIP_CODE = "90210"  # Change to your area

# Line 51: How often to check (in seconds)
CHECK_INTERVAL = 300  # 5 minutes
```

## Common Zip Codes 📍

Some popular areas:
- Los Angeles: `90210`
- New York: `10001`
- Chicago: `60601`
- Houston: `77001`
- Phoenix: `85001`
- Miami: `33101`

## Stopping the Bot 🛑

Press `Ctrl+C` in the terminal to stop the bot gracefully. It will send a shutdown notification to Discord.

## What Happens When Running? 🔄

1. **Startup** (0-5 seconds)
   - Discord bot connects
   - Sends "Bot Started" notification
   - Lists configuration

2. **First Scan** (0-60 seconds)
   - Checks all 26 SKUs in batches of 5
   - Each batch takes ~5-10 seconds
   - Sends notifications for any in-stock items

3. **Wait Period** (5 minutes)
   - Bot waits until next scan
   - Discord commands still work during this time
   - Sends "Scan Complete - Waiting" notification

4. **Repeat** 
   - Process repeats every 5 minutes
   - Runs indefinitely until you stop it

## Expected Console Output 📺

```
================================================================================
🎮 POKEMON STOCK MONITOR - BEST BUY
================================================================================
📦 Monitoring 26 Pokemon SKUs
📍 Default Zip Code: 90210
⏱️ Check Interval: 5 minutes
🔄 Batch Size: 5 SKUs at a time
================================================================================

🤖 Starting Discord bot...
✅ Discord bot logged in as Pokemon Stock Bot#1234
🤖 Bot is ready to receive commands!

🔍 Starting stock monitoring...
✅ Discord notification sent: 🟢 Bot Started

================================================================================
🔍 Starting new scan at 2025-10-19 14:30:00
================================================================================

📦 Processing batch 1/6...
❌ Out of Stock: 151 Alakazam ex box (SKU: 6548368)
❌ Out of Stock: 151 Zapdos ex box (SKU: 6548370)
✅ IN STOCK: Crown Zenith Booster Bundle 6pk (SKU: 6595705)
...
```

## Performance 📊

- **Check Time per SKU**: ~1-2 seconds
- **Full Scan (26 SKUs)**: ~45-60 seconds
- **Memory Usage**: ~50-100 MB
- **Network Usage**: Minimal (only API calls)

## Need Help? 🆘

1. Check console for error messages
2. Verify internet connection
3. Test webhook URL separately
4. Make sure all dependencies installed
5. Check Discord server permissions

---

Good luck with your Pokemon hunting! 🎴🔥

