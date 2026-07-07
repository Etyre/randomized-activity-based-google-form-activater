#!/usr/bin/env python3
"""
Randomized Presence Checker
Opens survey at random intervals to check user presence and collect responses.
"""

import random
import time
import subprocess
import sys
from datetime import datetime, timedelta
import os
from pathlib import Path
import json

class PresenceChecker:
    def __init__(self, survey_url="https://forms.gle/your-survey-link-here"):
        self.survey_url = survey_url

        # Check if we're in test mode
        test_mode = os.environ.get('TEST_MODE', 'false').lower() in ('true', '1', 'yes')

        if test_mode:
            # Test mode: 30-60 seconds (hardcoded, ignores env vars)
            self.min_interval = 30
            self.max_interval = 60
            print(f"[TEST MODE] Using short intervals: {self.min_interval}-{self.max_interval} seconds")
        else:
            # Production mode: use env vars or defaults (15-90 minutes)
            self.min_interval = int(os.environ.get('MIN_INTERVAL', 30 * 60))
            self.max_interval = int(os.environ.get('MAX_INTERVAL', 90 * 60))

        self.activity_threshold = 30  # Only send notifications if user was active in last 30 seconds
        self.running = True

    def get_random_interval(self):
        """Generate random interval between min and max interval"""
        return random.randint(self.min_interval, self.max_interval)

    def is_screen_on(self):
        """Check if the screen/display is currently on using CoreGraphics"""
        try:
            from Quartz import CGDisplayIsAsleep, CGMainDisplayID

            display_id = CGMainDisplayID()
            is_asleep = CGDisplayIsAsleep(display_id)
            screen_on = not is_asleep

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                  f"Display state: {'on' if screen_on else 'off'}")

            return screen_on

        except ImportError:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                  f"Warning: PyObjC not available, assuming screen is on")
            return True
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                  f"Error checking screen state: {e}, assuming screen is on")
            return True

    def is_user_active(self):
        """Check if user has been active at computer in the last 30 seconds"""
        try:
            # Get system idle time using ioreg command
            result = subprocess.run([
                'ioreg', '-c', 'IOHIDSystem'
            ], capture_output=True, text=True, check=True)

            # Parse the output to find HIDIdleTime
            for line in result.stdout.split('\n'):
                if 'HIDIdleTime' in line:
                    # Extract the idle time value
                    idle_time_ns = int(line.split('=')[1].strip())
                    # Convert nanoseconds to seconds
                    idle_time_seconds = idle_time_ns / 1_000_000_000

                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                          f"User idle for {idle_time_seconds:.1f} seconds")

                    # Return True if user was active within threshold
                    return idle_time_seconds < self.activity_threshold

            # If we can't find idle time, assume user is active
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                  f"Could not determine idle time, assuming user active")
            return True

        except subprocess.CalledProcessError as e:
            print(f"Error checking user activity: {e}")
            # If we can't check, assume user is active
            return True

    def play_notification_sound(self):
        """Play system notification sound"""
        try:
            subprocess.run(['afplay', '/System/Library/Sounds/Hero.aiff'],
                         check=True, capture_output=True)
        except subprocess.CalledProcessError:
            # Fallback to system beep
            subprocess.run(['osascript', '-e', 'beep'],
                         capture_output=True)

    def send_notification(self):
        """Open survey in browser with sound notification"""
        try:
            # Play notification sound
            self.play_notification_sound()

            # Open the survey in a new window
            subprocess.run(['open', '-n', '-a', 'Google Chrome', '--args', '--new-window', self.survey_url], check=True)

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Survey opened")

        except subprocess.CalledProcessError as e:
            print(f"Error opening survey: {e}")

    def run(self):
        """Main loop - wait for random intervals and open survey"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Presence checker started")
        print(f"Survey URL: {self.survey_url}")
        print(f"Interval range: {self.min_interval}-{self.max_interval} seconds")

        try:
            while self.running:
                # Wait for random interval
                wait_time = self.get_random_interval()
                next_check = datetime.now() + timedelta(seconds=wait_time)

                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                      f"Next survey in {wait_time} seconds "
                      f"(at {next_check.strftime('%H:%M:%S')})")

                time.sleep(wait_time)

                # Check if screen is on before opening survey
                if self.is_screen_on():
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Screen is on. Opening survey...")
                    self.send_notification()
                else:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Screen is off. Skipping survey.")

        except KeyboardInterrupt:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Presence checker stopped")
            self.running = False

def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        content = None
        for attempt in range(3):
            try:
                content = env_file.read_text()
                break
            except OSError as e:
                print(f"Warning: Could not read .env file (attempt {attempt + 1}/3): {e}")
                time.sleep(1)
        if content is None:
            print("Error: Failed to read .env file after 3 attempts, continuing without it")
            return
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                # Strip comments from value (anything after #)
                if '#' in value:
                    value = value.split('#')[0]
                os.environ[key.strip()] = value.strip()

def main():
    # Load environment variables from .env file
    load_env_file()

    # Get survey URL from environment variable, command line, or default
    survey_url = os.environ.get('SURVEY_URL')

    # If URL provided as command line argument, it takes precedence
    if len(sys.argv) > 1:
        survey_url = sys.argv[1]

    # Fall back to default if not set
    if not survey_url:
        survey_url = "https://forms.gle/your-survey-link-here"
        print("Warning: No SURVEY_URL found in .env file or command line. Using default placeholder.")

    checker = PresenceChecker(survey_url)
    checker.run()

if __name__ == "__main__":
    main()