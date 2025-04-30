# Telegram Forwarder Bot Deployment Guide

This guide will help you deploy the Telegram Forwarder Bot on a VPS or using Termux on Android.

## Requirements

- Python 3.6+
- python-telegram-bot
- Pillow (for image processing)
- Flask (for web interface, optional)

## Setup in Termux (Android)

1. Install Termux from the Play Store or F-Droid
2. Open Termux and run the following commands:

```bash
# Update and install required packages
pkg update
pkg upgrade
pkg install python

# Install pip and development tools
pkg install python-pip
pkg install git
pkg install libffi-dev
pkg install libjpeg-turbo-dev
pkg install zlib-dev

# Clone the repository or upload files to your device
# For example:
cd storage/shared/TelegramForwarder  # Navigate to your files

# Install Python dependencies
pip install python-telegram-bot pillow
```

3. Set up environment variables:

```bash
# Set your bot token
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export SOURCE_CHANNEL_ID="your_source_channel_id_here"
export DESTINATION_CHANNEL_ID="your_destination_channel_id_here"
```

4. Run the bot:

```bash
python main.py
```

## Setup on VPS

1. Connect to your VPS using SSH
2. Update and install dependencies:

```bash
# For Debian/Ubuntu
sudo apt update
sudo apt upgrade
sudo apt install python3 python3-pip python3-dev git
sudo apt install libffi-dev libjpeg-dev zlib1g-dev

# For CentOS/RHEL
sudo yum update
sudo yum install python3 python3-pip python3-devel git
sudo yum install libffi-devel libjpeg-devel zlib-devel
```

3. Clone the repository or upload your files:

```bash
git clone https://github.com/yourusername/TelegramForwarder.git
cd TelegramForwarder
```

4. Install Python dependencies:

```bash
pip3 install python-telegram-bot pillow flask gunicorn
```

5. Set up environment variables:

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export SOURCE_CHANNEL_ID="your_source_channel_id_here"
export DESTINATION_CHANNEL_ID="your_destination_channel_id_here"
```

6. Run the bot:

```bash
# Run just the bot
python3 main.py

# Or run with web interface
gunicorn -b 0.0.0.0:5000 "main:main()"
```

## Running the Bot in the Background

To keep the bot running after you close the terminal:

### Using Screen (recommended for VPS and Termux)

```bash
# Install screen
apt install screen  # Debian/Ubuntu/Termux
yum install screen  # CentOS/RHEL

# Start a new screen session
screen -S telegram-bot

# Run your bot
python main.py

# Detach from the screen session by pressing Ctrl+A, then D

# To reconnect to your session later
screen -r telegram-bot
```

### Using nohup (alternative for VPS)

```bash
nohup python main.py > bot.log 2>&1 &
```

## Making the Bot Start at Boot (VPS only)

Create a systemd service:

```bash
sudo nano /etc/systemd/system/telegram-forwarder.service
```

Add the following content:

```
[Unit]
Description=Telegram Forwarder Bot
After=network.target

[Service]
User=your_username
WorkingDirectory=/path/to/TelegramForwarder
Environment="TELEGRAM_BOT_TOKEN=your_bot_token_here"
Environment="SOURCE_CHANNEL_ID=your_source_channel_id_here"
Environment="DESTINATION_CHANNEL_ID=your_destination_channel_id_here"
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable telegram-forwarder
sudo systemctl start telegram-forwarder
```

Check status:

```bash
sudo systemctl status telegram-forwarder
```

## Troubleshooting

- **Error: No module named 'telegram'**: Run `pip install python-telegram-bot`
- **Error: No module named 'PIL'**: Run `pip install pillow`
- **Image processing issues**: Make sure you have installed the image libraries with `pkg install libjpeg-turbo-dev` (Termux) or `apt install libjpeg-dev` (Debian/Ubuntu)
- **Permission errors**: Ensure the directories exist and have proper permissions
- **Bot doesn't receive messages**: Verify your bot token and channel IDs are correct
- **Bot crashes with memory error**: Termux may have limited resources; try reducing the image processing quality