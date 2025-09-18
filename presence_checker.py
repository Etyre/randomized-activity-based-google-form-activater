#!/usr/bin/env python3
"""
Randomized Presence Checker
Sends notifications at random intervals to check user presence and collect survey responses.
"""

import random
import time
import subprocess
import sys
import threading
from datetime import datetime, timedelta
import os
from pathlib import Path
import json

class PresenceChecker:
    def __init__(self, survey_url="https://forms.gle/your-survey-link-here"):
        self.survey_url = survey_url
        self.min_interval = int(os.environ.get('MIN_INTERVAL', 30 * 60))  # 30 minutes default
        self.max_interval = int(os.environ.get('MAX_INTERVAL', 4 * 60 * 60))  # 4 hours default
        self.notification_timeout = int(os.environ.get('NOTIFICATION_TIMEOUT', 5 * 60))  # 5 minutes default
        self.activity_threshold = 30  # Only send notifications if user was active in last 30 seconds
        self.running = True

    def get_random_interval(self):
        """Generate random interval between min and max interval"""
        return random.randint(self.min_interval, self.max_interval)

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
        """Send macOS notification with survey link"""
        title = "Presence Check"
        message = "Time for a quick survey! Opening now..."

        # AppleScript to send notification
        applescript = f'''
        display notification "{message}" with title "{title}" sound name "Hero"
        '''

        try:
            # Send notification
            subprocess.run(['osascript', '-e', applescript],
                         check=True, capture_output=True)

            # Also play sound separately to ensure it plays
            self.play_notification_sound()

            # Automatically open the survey after sending notification
            subprocess.run(['open', self.survey_url], check=True)

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Notification sent and survey opened")

            # Schedule auto-dismissal after timeout
            threading.Timer(self.notification_timeout, self.clear_notifications).start()

        except subprocess.CalledProcessError as e:
            print(f"Error sending notification: {e}")

    def clear_notifications(self):
        """Clear all notifications from notification center"""
        try:
            # AppleScript to clear notifications
            applescript = '''
            tell application "System Events"
                tell process "NotificationCenter"
                    try
                        click button 1 of window 1
                    end try
                end tell
            end tell
            '''
            subprocess.run(['osascript', '-e', applescript],
                         capture_output=True)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Notifications cleared")
        except subprocess.CalledProcessError:
            # If that doesn't work, try alternative method
            try:
                subprocess.run(['killall', 'NotificationCenter'],
                             capture_output=True)
            except subprocess.CalledProcessError:
                pass

    def open_survey(self):
        """Open survey in default browser"""
        try:
            subprocess.run(['open', self.survey_url], check=True)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Survey opened")
        except subprocess.CalledProcessError as e:
            print(f"Error opening survey: {e}")

    def run(self):
        """Main loop - wait for random intervals and send notifications"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Presence checker started")
        print(f"Survey URL: {self.survey_url}")
        print(f"Interval range: {self.min_interval}-{self.max_interval} seconds")

        try:
            while self.running:
                # Wait for random interval
                wait_time = self.get_random_interval()
                next_notification = datetime.now() + timedelta(seconds=wait_time)

                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                      f"Next notification in {wait_time} seconds "
                      f"(at {next_notification.strftime('%H:%M:%S')})")

                time.sleep(wait_time)

                # Check if user is active at computer before sending notification
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking user activity...")
                if self.is_user_active():
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] User is active, sending notification...")
                    self.send_notification()
                else:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] User not active (idle > {self.activity_threshold}s), skipping notification")

        except KeyboardInterrupt:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Presence checker stopped")
            self.running = False

def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
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