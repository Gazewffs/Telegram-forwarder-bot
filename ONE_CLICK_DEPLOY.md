# One-Click Deployment for Telegram Channel Forwarder Bot

Deploy your Telegram Channel Forwarder Bot to Railway.app with just one click!

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

## What This Does

Clicking the "Deploy on Railway" button above will:

1. Create a new project on Railway
2. Set up and deploy your Telegram Forwarder Bot
3. Prompt you to enter the required environment variables

## Required Information

Before clicking the deploy button, make sure you have:

1. **Telegram Bot Token** - Get this by talking to [@BotFather](https://t.me/botfather) on Telegram
2. **Source Channel ID** - The ID of the channel you want to forward messages from
3. **Destination Channel ID** - The ID of the channel you want to forward messages to

## How to Find Channel IDs

To get a channel ID, you can:

1. Forward a message from the channel to [@userinfobot](https://t.me/userinfobot)
2. The bot will reply with the channel ID (usually in the format `-100xxxxxxxxxx`)
3. Or add the bot [@username_to_id_bot](https://t.me/username_to_id_bot) to your channel, it will show the channel ID

## After Deployment

Once deployed, your bot will automatically:

1. Start running on Railway's servers
2. Connect to Telegram using your bot token
3. Begin forwarding messages from your source channel to your destination channel
4. Apply any text filters or image modifications you've configured

## Manage Your Bot

After deployment, you can:

1. Check logs in the Railway dashboard
2. Use Telegram commands to manage your bot:
   - `/start` - Start the bot
   - `/help` - Show help message
   - `/status` - Check bot status and configuration
   - `/filters` - List all active text filters
   - `/addfilter pattern replacement` - Add a new text filter
   - `/delfilter index` - Delete a filter by index
   - `/testfilter text` - Test how a message would be filtered

## Troubleshooting

If your bot isn't working after deployment:

1. Verify that you've entered the correct environment variables
2. Make sure your bot has been added to both source and destination channels
3. Ensure the bot has admin rights in both channels
4. Check the logs in the Railway dashboard for any error messages

For more detailed deployment instructions, see [RAILWAY_SETUP.md](RAILWAY_SETUP.md).