# Randomized Presence Checker

A macOS tool that sends notifications at random intervals to collect survey responses, designed for experience sampling or presence checking.

## Features

- Sends notifications at truly randomized intervals (1-6 hours)
- **Activity Detection**: Only triggers when you've been active at your computer within the last 30 seconds
- Automatically opens survey in browser when notification appears
- Plays notification sound (Hero)
- Auto-dismisses notifications after 5 minutes to prevent pile-up
- Runs continuously in the background

## Setup

1. **Configure your survey URL**:
   ```bash
   cp .env.example .env
   # Edit .env and replace the survey URL with your actual Google Form link
   ```

2. **Run setup**:
   ```bash
   chmod +x setup.sh && ./setup.sh
   ```

## Manual Usage

```bash
# Run directly (uses .env file for survey URL)
python3 presence_checker.py

# Or override with command line argument
python3 presence_checker.py "https://your-survey-url-here"
```

## How Activity Detection Works

The system uses a two-step process:

1. **Timer Phase**: Waits for a random interval (1-6 hours)
2. **Activity Check**: When timer expires, checks if you've used mouse/keyboard in last 30 seconds
3. **Decision**: Only sends notification if you're actively using the computer

**Important**: This means you'll receive fewer notifications than the raw timer intervals suggest. If you're away from your computer when a timer expires, that notification opportunity is skipped and a new random timer begins.

## Environment Variables

The script loads configuration from a `.env` file:

- `SURVEY_URL` - Your Google Form or survey URL (required)
- `MIN_INTERVAL` - Minimum seconds between notifications (default: 3600 = 1 hour)
- `MAX_INTERVAL` - Maximum seconds between notifications (default: 21600 = 6 hours)
- `NOTIFICATION_TIMEOUT` - Seconds before auto-dismissal (default: 300 = 5 minutes)

## Control the Service

```bash
# Stop the background service
launchctl unload ~/Library/LaunchAgents/com.user.presencechecker.plist

# Start the background service
launchctl load ~/Library/LaunchAgents/com.user.presencechecker.plist

# Check if running
launchctl list | grep presencechecker
```

## Logs

- Output: `presence_checker.log`
- Errors: `presence_checker_error.log`

## Customization

Edit `presence_checker.py` to modify:
- `min_interval`: Minimum time between notifications (default: 30 minutes)
- `max_interval`: Maximum time between notifications (default: 4 hours)
- `notification_timeout`: How long before auto-dismissal (default: 5 minutes)