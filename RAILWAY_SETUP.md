# Deploying to Railway.app with GitHub

This guide will walk you through how to deploy the Telegram Forwarder Bot to Railway.app using GitHub integration.

## Option 1: One-Click Deployment (Easiest)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

1. Click the "Deploy on Railway" button above
2. Sign in with GitHub if prompted
3. Fill in the required environment variables:
   - `TELEGRAM_BOT_TOKEN` - Your Telegram bot token from BotFather
   - `SOURCE_CHANNEL_ID` - ID of the source channel
   - `DESTINATION_CHANNEL_ID` - ID of the destination channel
4. Click "Deploy"
5. Wait for the deployment to complete (usually 1-2 minutes)
6. Your bot is now running!

## Option 2: Manual Deployment

### Prerequisites

1. A GitHub account
2. A Railway.app account (sign up at https://railway.app/)
3. Your Telegram bot token and channel IDs

### Step 1: Fork the Repository

1. Fork this repository to your own GitHub account
2. Make sure your fork includes these files:
   - `bot_standalone.py` - The standalone bot script
   - `Procfile` - Tells Railway how to run your bot
   - `railway.json` - Configuration for Railway

### Step 2: Connect Railway to GitHub

1. Create a Railway account if you don't have one
2. From the Railway dashboard, click "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account if not already connected
5. Select your forked repository from the list

### Step 3: Configure Environment Variables

After creating your project in Railway, you need to set up the environment variables:

1. In your project dashboard, go to the "Variables" tab
2. Add the following variables:
   - `TELEGRAM_BOT_TOKEN` - Your Telegram bot token
   - `SOURCE_CHANNEL_ID` - ID of the source channel
   - `DESTINATION_CHANNEL_ID` - ID of the destination channel

### Step 4: Deployment

Railway will automatically deploy your application:

1. Railway detects the `Procfile` and knows to run: `python bot_standalone.py`
2. The service will automatically restart if it fails (configured in `railway.json`)
3. Railway provides logs to help you debug any issues

### Step 5: Verify Deployment

1. Go to the "Deployments" tab to see the deployment status
2. Check the logs to ensure the bot has started successfully
3. Try sending a message in your source channel and verify it's forwarded to the destination

## Managing Your Bot

- **Updating**: When you push changes to your GitHub repo, Railway will automatically redeploy
- **Monitoring**: Use the "Metrics" tab to monitor your bot's resource usage
- **Logs**: Check the "Logs" tab to troubleshoot any issues

## Railway Free Tier Limitations

Railway offers a free tier with limited resources:
- 512MB RAM
- Shared CPU
- 1GB of storage
- 500 hours of runtime per month

For most Telegram bots, this is more than sufficient. If you need more resources, Railway offers paid plans with higher limits.

## Troubleshooting

If your bot encounters issues:

1. Check the Railway logs for error messages
2. Verify your environment variables are set correctly
3. Make sure your bot token and channel IDs are valid
4. Check that your bot has permission to access the channels

For more help, you can check the Railway documentation at https://docs.railway.app/