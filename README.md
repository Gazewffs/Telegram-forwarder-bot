# Telegram Channel Forwarder Bot

A customizable Telegram bot that forwards messages from a source channel to a destination channel with text filtering and image processing capabilities.

## Features

- Forward messages from one Telegram channel to another
- Apply text filtering (replace words, modify phrases, remove text)
- Process images (resize, enhance, add watermarks)
- Selectively replace images based on content
- Time zone conversion (GMT+14:00 format)
- Filter management through Telegram commands
- Supports multiple message types (text, photos, videos, etc.)
- Easy deployment to VPS, Railway, or Termux on Android

## Commands

- `/start` - Start the bot
- `/help` - Show help message
- `/status` - Check bot status and configuration
- `/filters` - List all active text filters
- `/addfilter pattern replacement` - Add a new text filter
- `/delfilter index` - Delete a filter by index
- `/testfilter text` - Test how a message would be filtered

## Setup

### Requirements

- Python 3.7+
- python-telegram-bot
- Pillow for image processing

### Configuration

The bot requires the following environment variables:

```
TELEGRAM_BOT_TOKEN=your_bot_token
SOURCE_CHANNEL_ID=source_channel_id
DESTINATION_CHANNEL_ID=destination_channel_id
```

## Deployment

### Railway.app (Recommended)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

The one-click button above may not work due to Railway template limitations. 

For detailed manual deployment instructions, see [MANUAL_DEPLOYMENT.md](MANUAL_DEPLOYMENT.md).

### VPS or Termux (Android)

For detailed deployment instructions on VPS or Termux, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Usage Examples

### Text Filtering

The bot can replace text patterns automatically:

- Replace specific keywords with alternative text
- Convert time formats to GMT+14:00
- Remove or modify registration links
- Add custom disclaimers

### Image Processing

For images, the bot can:

- Replace images with captions containing specific keywords
- Resize images to reduce bandwidth usage
- Add watermarks to forwarded images

## License

MIT License - feel free to modify and use for your own projects.

## Contributing

Contributions, issues, and feature requests are welcome!