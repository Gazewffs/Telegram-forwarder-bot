# Telegram Forwarder Bot - Render Deployment Guide

This guide explains how to deploy your Telegram Forwarder Bot on Render as a **free web service** instead of a paid background worker.

## Deployment Steps

1. **Fork/Clone Repository**
   - Fork or clone this repository to your GitHub account

2. **Add the new files**
   - Make sure `webapp.py` is added to your repository
   - Update `requirements.txt` to include Flask and gunicorn

3. **Create a new Web Service on Render**
   - Go to your Render dashboard and click "New +"
   - Select "Web Service"
   - Connect your GitHub repository
   - Name your service (e.g., "telegram-forwarder-bot")

4. **Configure the Service**
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

5. **Add Environment Variables**
   - TELEGRAM_BOT_TOKEN = [Your bot token from BotFather]
   - SOURCE_CHANNEL_ID = [ID of channel to forward from]
   - DESTINATION_CHANNEL_ID = [ID of channel to forward to]

6. **Deploy**
   - Click "Create Web Service"
   - Wait for the deployment to complete

## Keeping Your Bot Running

Render's free tier web services will spin down after periods of inactivity. To prevent this:

### Set Up UptimeRobot

1. Create a free account at [UptimeRobot](https://uptimerobot.com/)
2. Add a new HTTP(s) monitor:
   - Name: [Your bot name]
   - URL: Your Render app URL (e.g., https://your-app-name.onrender.com)
   - Monitoring Interval: 5 minutes
3. Save the monitor

This will ping your application every 5 minutes, keeping it active and preventing Render from spinning it down.

## Troubleshooting

If your bot stops working:

1. Visit your Render URL in a browser to check the status
2. If needed, visit [your-app-url]/start to restart the bot thread
3. Check the Render logs for any errors
4. Make sure UptimeRobot is correctly pinging your application
5. Verify your environment variables are set correctly

## App Endpoints

- **/** - Shows the bot status
- **/health** - Health check endpoint (returns "healthy")
- **/start** - Manually starts/restarts the bot thread