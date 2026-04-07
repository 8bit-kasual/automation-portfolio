#!/usr/bin/env python3
"""
Manual KVS Activity Push — Selenium-based NocoDB → KVS sync

Queries NocoDB for Sales Activities with "Push to KVS = true" flag,
then creates KVS tasks using Selenium browser automation.

Usage:
    python push_kvs_activities.py [--dry-run] [--limit N]

Options:
    --dry-run       Preview activities to push without creating KVS tasks
    --limit N       Process only first N activities (useful for testing)

Process:
    1. Query NocoDB Sales Activities with "Push to KVS = true"
    2. Validate required fields (Account, Date, Title, Contact optional)
    3. Connect to Selenium Chrome debugging session
    4. For each activity:
       - Map NocoDB data to KVS task format
       - Execute create_kvs_task_final.py logic to fill KVS form
       - Capture KVS Task ID
       - Update NocoDB with Task ID, Sync Status, and error (if any)
       - Uncheck "Push to KVS" flag
    5. Generate summary report

Requirements:
    - Chrome debugging session running: start-kvs-chrome.bat
    - Logged into KVS in Chrome window
    - NocoDB API token in .env file
    - Selenium Python library installed
"""

import os
import sys
import argparse
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

# Configuration from environment
NOCODB_API_URL = "http://localhost:8080/api/v2"
NOCODB_BASE_ID = "pu3kkly0sn9mdz1"
NOCODB_SALES_ACTIVITIES_TABLE_ID = "ml5o8449sn55xxc"
NOCODB_ACTIVE_ACCOUNTS_TABLE_ID = "mkn8keuazv469tf"
NOCODB_CONTACTS_TABLE_ID = "mdey25ca8vc7bar"
NOCODB_API_TOKEN = os.getenv("NOCODB_API_TOKEN", "")
KVS_CREATE_TASK_URL = "https://kvs.teltonika.lt/Tasks/Create/0?ReturnUrl=%2fTasks"
CHROME_DEBUG_PORT = 9222

# API headers
NOCODB_HEADERS = {
    "xc-auth": NOCODB_API_TOKEN,
    "Content-Type": "application/json"
}


class KVSActivityPusher:
    """Manages manual push of NocoDB Sales Activities to KVS."""

    def __init__(self, dry_run: bool = False, limit: Optional[int] = None):
        self.dry_run = dry_run
        self.limit = limit
        self.driver = None
        self.results = {
            "total": 0,
            "synced": 0,
            "failed": 0,
            "activities": []
        }

    def connect_chrome(self) -> bool:
        """Connect to Chrome debugging session."""
        try:
            options = webdriver.ChromeOptions()
            options.add_experimental_option(
                "debuggerAddress", f"localhost:{CHROME_DEBUG_PORT}"
            )
            self.driver = webdriver.Chrome(options=options)
            print(f"✓ Connected to Chrome (port {CHROME_DEBUG_PORT})")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to Chrome: {e}")
            print(f"  Make sure Chrome is running: start-kvs-chrome.bat")
            return False

    def query_nocodb_activities(self) -> List[Dict]:
        """Query NocoDB for Sales Activities with Push to KVS = true."""
        try:
            url = f"{NOCODB_API_URL}/tables/{NOCODB_SALES_ACTIVITIES_TABLE_ID}/records"
            params = {
                "where": "(Push to KVS,eq,true)"
            }
            response = requests.get(url, headers=NOCODB_HEADERS, params=params)
            response.raise_for_status()

            activities = response.json().get("list", [])
            print(f"✓ Found {len(activities)} activities to push")

            if self.limit:
                activities = activities[:self.limit]
                print(f"  (limited to {self.limit})")

            return activities
        except Exception as e:
            print(f"✗ Failed to query NocoDB: {e}")
            return []

    def validate_activity(self, activity: Dict) -> Tuple[bool, Optional[str]]:
        """Validate that required fields are present."""
        fields = activity.get("fields", {})

        # Required fields
        if not fields.get("Title"):
            return False, "Missing Title"
        if not fields.get("Date"):
            return False, "Missing Date"
        if not fields.get("Account"):
            return False, "Missing Account"
        if not fields.get("Outcome"):
            return False, "Missing Outcome"

        return True, None

    def push_to_kvs(self, activity: Dict) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Create KVS task for this activity.

        Returns:
            (success: bool, task_id: Optional[str], error: Optional[str])
        """
        fields = activity.get("fields", {})

        try:
            # Navigate to KVS Create Task form
            self.driver.get(KVS_CREATE_TASK_URL)

            # Wait for form to load
            wait = WebDriverWait(self.driver, 15)
            wait.until(EC.presence_of_element_located((By.NAME, "Date")))

            # Build task description
            title = fields.get("Title", "")
            account = fields.get("Company Name", "")  # Lookup field
            contact = fields.get("Contact", "")
            notes = fields.get("Notes", "")
            outcome = fields.get("Outcome", "")

            description = f"{title}"
            if contact:
                description += f" — {contact}"
            if outcome:
                description += f" ({outcome})"
            if notes:
                description += f"\n\n{notes}"

            # Fill form fields
            date_field = self.driver.find_element(By.NAME, "Date")
            date_field.clear()
            date_field.send_keys(fields.get("Date", ""))

            goal_field = self.driver.find_element(By.NAME, "Goal")
            goal_field.clear()
            goal_field.send_keys(description)

            # Submit form
            submit_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Submit')]"
            )
            submit_button.click()

            # Wait for success page and extract task ID
            time.sleep(2)  # Allow form submission
            task_id_match = self._extract_task_id()

            if task_id_match:
                return True, task_id_match, None
            else:
                return False, None, "Could not extract KVS Task ID from response"

        except Exception as e:
            return False, None, str(e)

    def _extract_task_id(self) -> Optional[str]:
        """Extract KVS Task ID from page after successful submission."""
        try:
            # After successful KVS task creation, look for task ID in URL or page
            # This is implementation-specific based on KVS response
            current_url = self.driver.current_url
            if "Tasks/Edit/" in current_url:
                task_id = current_url.split("Tasks/Edit/")[-1].split("?")[0]
                return task_id
            return None
        except Exception:
            return None

    def update_nocodb_record(
        self, activity_id: str, task_id: Optional[str], error: Optional[str], synced: bool
    ) -> bool:
        """Update NocoDB record with sync results."""
        try:
            url = f"{NOCODB_API_URL}/tables/{NOCODB_SALES_ACTIVITIES_TABLE_ID}/records/{activity_id}"

            payload = {
                "Push to KVS": False,  # Uncheck the flag
                "KVS Sync Status": "Synced" if synced else "Error"
            }

            if task_id:
                payload["KVS Task ID"] = task_id

            if error:
                payload["KVS Error Message"] = error

            response = requests.patch(
                url,
                headers=NOCODB_HEADERS,
                json={"fields": payload}
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"  ⚠ Failed to update NocoDB: {e}")
            return False

    def process_activities(self):
        """Process all flagged activities."""
        if not NOCODB_API_TOKEN:
            print("✗ NOCODB_API_TOKEN not set in environment")
            return

        activities = self.query_nocodb_activities()
        self.results["total"] = len(activities)

        if not activities:
            print("No activities to push.")
            return

        if self.dry_run:
            print(f"\n[DRY RUN] Would push {len(activities)} activities:\n")
            for activity in activities:
                fields = activity.get("fields", {})
                print(f"  • {fields.get('Title')} ({fields.get('Date')})")
            return

        # Connect to Chrome
        if not self.connect_chrome():
            return

        try:
            for i, activity in enumerate(activities, 1):
                activity_id = activity.get("id")
                fields = activity.get("fields", {})
                title = fields.get("Title", "Unknown")

                print(f"\n[{i}/{len(activities)}] {title}")

                # Validate
                valid, error = self.validate_activity(activity)
                if not valid:
                    print(f"  ✗ Validation failed: {error}")
                    self.results["failed"] += 1
                    self.update_nocodb_record(activity_id, None, error, False)
                    self.results["activities"].append({
                        "title": title,
                        "status": "failed",
                        "error": error
                    })
                    continue

                # Push to KVS
                success, task_id, kvs_error = self.push_to_kvs(activity)

                if success:
                    print(f"  ✓ Synced (Task ID: {task_id})")
                    self.results["synced"] += 1
                    self.update_nocodb_record(activity_id, task_id, None, True)
                    self.results["activities"].append({
                        "title": title,
                        "status": "synced",
                        "task_id": task_id
                    })
                else:
                    print(f"  ✗ Failed: {kvs_error}")
                    self.results["failed"] += 1
                    self.update_nocodb_record(activity_id, None, kvs_error, False)
                    self.results["activities"].append({
                        "title": title,
                        "status": "failed",
                        "error": kvs_error
                    })

                time.sleep(1)  # Throttle requests

        finally:
            if self.driver:
                self.driver.quit()
                print("\n✓ Chrome session closed")

    def print_summary(self):
        """Print summary of push results."""
        print("\n" + "="*60)
        print("KVS PUSH SUMMARY")
        print("="*60)
        print(f"Total activities:  {self.results['total']}")
        print(f"Synced:            {self.results['synced']} ✓")
        print(f"Failed:            {self.results['failed']} ✗")

        if self.results["activities"]:
            print("\nDetails:")
            for item in self.results["activities"]:
                status_icon = "✓" if item["status"] == "synced" else "✗"
                print(f"  {status_icon} {item['title']}")
                if item["status"] == "synced":
                    print(f"     Task ID: {item['task_id']}")
                else:
                    print(f"     Error: {item['error']}")

        print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description="Manual push of NocoDB Sales Activities to KVS"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview activities without creating KVS tasks"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Process only first N activities"
    )

    args = parser.parse_args()

    pusher = KVSActivityPusher(dry_run=args.dry_run, limit=args.limit)
    pusher.process_activities()
    pusher.print_summary()


if __name__ == "__main__":
    main()
