# Script Location Changed

**Date:** 2025-11-05 (re-established 2026-07-07)
**Documentation created by:** Claude Code

## Active Location
The active version of this script runs from:
```
~/Library/Scripts/presence-checker/
```

## Reason for Move
After a macOS update, launchd services could not access files in the Documents directory due to enhanced security restrictions ("Operation not permitted" errors). The `~/Library/Scripts/` location is accessible to launchd without requiring Full Disk Access permissions.

## What Runs There
- `presence_checker.py` - Main script
- `.env` - Configuration file
- `presence_checker.log` - Standard output log
- `presence_checker_error.log` - Standard error log

## Active Service
The launchd service is configured in:
```
~/Library/LaunchAgents/com.user.presencechecker.plist
```
It uses `RunAtLoad` (starts at login) and `KeepAlive` (auto-restarts if it dies).
The plist points at `/Users/elityre/Library/Scripts/presence-checker/` — NOT the
Documents copy.

## Files in This Directory
The files here (in Documents) remain the original/development copy and the git
repository. If you want to make changes:
1. Edit files here in the Documents folder (and commit them to git)
2. Copy the updated files to `~/Library/Scripts/presence-checker/`:
   ```bash
   cp presence_checker.py .env ~/Library/Scripts/presence-checker/
   ```
3. Restart the service:
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.user.presencechecker.plist
   launchctl load ~/Library/LaunchAgents/com.user.presencechecker.plist
   ```

## First-Time / Reinstall Setup
If `~/Library/Scripts/presence-checker/` does not exist (e.g. on a new machine or
after cleanup), recreate it:
```bash
mkdir -p ~/Library/Scripts/presence-checker
cp presence_checker.py .env ~/Library/Scripts/presence-checker/
chmod +x ~/Library/Scripts/presence-checker/presence_checker.py
# Ensure the plist at ~/Library/LaunchAgents/com.user.presencechecker.plist
# points at the ~/Library/Scripts/presence-checker/ paths (not Documents), then:
launchctl load ~/Library/LaunchAgents/com.user.presencechecker.plist
```

## Check Status
```bash
launchctl list | grep presencechecker   # shows PID if running
pgrep -fl presence_checker               # shows the running process
tail -f ~/Library/Scripts/presence-checker/presence_checker_error.log
```
