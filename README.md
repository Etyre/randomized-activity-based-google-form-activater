# Randomized Presence Checker

A macOS tool that sends notifications at random intervals to collect survey responses, designed for experience sampling or presence checking.

## Features

- Opens the survey at truly randomized intervals (default 1–2 hours; see Environment Variables)
- **Screen-on check**: only opens the survey if the display is awake — if the screen is asleep when the timer fires, that survey is skipped and a fresh random timer starts
- Opens the survey in a new **Google Chrome** window
- Plays a notification sound (Hero) when the survey opens
- Runs continuously in the background via a launchd agent

## Requirements

- macOS with **Google Chrome** installed (the browser is hardcoded in `presence_checker.py`)
- `pyobjc-framework-Quartz` for the screen-on check:
  ```bash
  /usr/bin/python3 -m pip install --user pyobjc-framework-Quartz
  ```
  Without it the script still runs but assumes the screen is always on.

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

## How Triggering Works

The main loop repeats:

1. **Timer Phase**: Waits a random interval between `MIN_INTERVAL` and `MAX_INTERVAL` (currently 1–2 hours).
2. **Screen Check**: When the timer expires, checks whether the display is awake (via Quartz `CGDisplayIsAsleep`).
3. **Decision**: If the screen is on, plays the sound and opens the survey in Chrome. If the screen is asleep, the survey is skipped.
4. A fresh random interval is chosen and the loop repeats.

**Important**: Because surveys are skipped while the display is asleep, you'll see fewer than one every 1–2 hours in practice.

> Note: the source also contains an `is_user_active()` idle-time check, but the current loop does **not** call it — only the screen-on state is used.

## Environment Variables

The script loads configuration from a `.env` file:

- `SURVEY_URL` - Your Google Form or survey URL (required; falls back to a placeholder if unset)
- `MIN_INTERVAL` - Minimum seconds between surveys (code default: 1800 = 30 min; currently set to 3600 = 1 hour in `.env`)
- `MAX_INTERVAL` - Maximum seconds between surveys (code default: 5400 = 90 min; currently set to 7200 = 2 hours in `.env`)
- `TEST_MODE` - Set to `true`/`1`/`yes` to use short 30–60 second intervals for testing (ignores `MIN_INTERVAL`/`MAX_INTERVAL`)
- `PYTHONUNBUFFERED` - Set to `1` (in the LaunchAgent) so log output is written in real time rather than block-buffered

Note: `NOTIFICATION_TIMEOUT` appears in `.env.example` but is not used by the current code (there is no auto-dismiss behavior).

## Active Location (Run on Startup)

> **Note:** launchd cannot reliably run this script from the Documents folder —
> after a macOS update it fails with "Operation not permitted". The active copy
> therefore runs from `~/Library/Scripts/presence-checker/`, which launchd can
> access without Full Disk Access. This directory (in Documents) is the
> development copy and git repo. See [`MOVED.md`](MOVED.md) for details.

The LaunchAgent at `~/Library/LaunchAgents/com.user.presencechecker.plist` uses
`RunAtLoad` (start at login) and `KeepAlive` (auto-restart), and points at the
`~/Library/Scripts/presence-checker/` copy.

To apply local code/config changes to the running service:
```bash
cp presence_checker.py .env ~/Library/Scripts/presence-checker/
launchctl unload ~/Library/LaunchAgents/com.user.presencechecker.plist
launchctl load ~/Library/LaunchAgents/com.user.presencechecker.plist
```

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

The active service writes logs to its Library location:

- Output: `~/Library/Scripts/presence-checker/presence_checker.log`
- Errors: `~/Library/Scripts/presence-checker/presence_checker_error.log`

## Customization

Prefer setting `MIN_INTERVAL` / `MAX_INTERVAL` in `.env`. To change behavior in code, edit `presence_checker.py`:
- `self.min_interval` / `self.max_interval`: interval bounds in seconds (code defaults: 1800 / 5400 = 30 / 90 min)
- `self.activity_threshold`: idle-time threshold used by `is_user_active()` (currently unused by the loop)
- The browser is hardcoded to `Google Chrome` in `send_notification()`; change that string to use a different browser