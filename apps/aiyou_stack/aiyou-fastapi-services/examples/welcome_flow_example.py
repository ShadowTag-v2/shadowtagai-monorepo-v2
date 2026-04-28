# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Example: Creating a Welcome Email Flow

This example demonstrates how to:
1. Create email templates
2. Create a welcome flow
3. Enroll recipients in the flow
"""

import asyncio

import httpx

API_BASE_URL = "http://localhost:8000/api/v1/email"


async def create_welcome_flow_example():
    """Create a complete welcome email flow"""
    async with httpx.AsyncClient() as client:
        # Step 1: Create email templates
        print("Creating email templates...")

        templates = [
            {
                "name": "welcome_day_0",
                "subject": "Welcome to AI You, {{ first_name }}! 🎉",
                "body_html": """
                    <html>
                    <body style="font-family: Arial, sans-serif;">
                        <h1>Welcome {{ first_name }}!</h1>
                        <p>We're thrilled to have you join AI You.</p>
                        <p>Here's what you can do to get started:</p>
                        <ul>
                            <li>Complete your profile</li>
                            <li>Explore our features</li>
                            <li>Join our community</li>
                        </ul>
                        <a href="https://shadowtag_v4.com/getting-started" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Get Started</a>
                    </body>
                    </html>
                """,
                "body_text": "Welcome {{ first_name }}! We're thrilled to have you join AI You.",
                "variables": ["first_name"],
            },
            {
                "name": "welcome_day_1",
                "subject": "Here are your first steps, {{ first_name }}",
                "body_html": """
                    <html>
                    <body style="font-family: Arial, sans-serif;">
                        <h1>Day 1: Your First Steps</h1>
                        <p>Hi {{ first_name }},</p>
                        <p>Let's make the most of your AI You account!</p>
                        <h2>Quick Wins:</h2>
                        <ol>
                            <li>Set up your first project</li>
                            <li>Invite your team</li>
                            <li>Try our AI features</li>
                        </ol>
                        <p>Need help? Our support team is here 24/7.</p>
                    </body>
                    </html>
                """,
                "body_text": "Hi {{ first_name }}, let's make the most of your AI You account!",
                "variables": ["first_name"],
            },
            {
                "name": "welcome_day_3",
                "subject": "{{ first_name }}, see what others are achieving",
                "body_html": """
                    <html>
                    <body style="font-family: Arial, sans-serif;">
                        <h1>Success Stories</h1>
                        <p>Hi {{ first_name }},</p>
                        <p>See what other users are achieving with AI You:</p>
                        <blockquote>
                            "AI You helped us increase productivity by 300%!" - Sarah, Tech Lead
                        </blockquote>
                        <blockquote>
                            "The automation features saved us 20 hours per week." - Mike, CEO
                        </blockquote>
                        <p>Ready to unlock your potential?</p>
                        <a href="https://shadowtag_v4.com/upgrade">Upgrade to Pro</a>
                    </body>
                    </html>
                """,
                "body_text": "Hi {{ first_name }}, see what other users are achieving with AI You!",
                "variables": ["first_name"],
            },
        ]

        template_ids = []
        for template_data in templates:
            response = await client.post(f"{API_BASE_URL}/templates", json=template_data)
            if response.status_code == 201:
                template = response.json()
                template_ids.append(template["id"])
                print(f"✓ Created template: {template['name']}")
            else:
                print(f"✗ Failed to create template: {response.text}")

        # Step 2: Create welcome flow
        print("\nCreating welcome flow...")

        flow_data = {
            "name": "User Welcome Series",
            "description": "3-email welcome series to onboard new users",
            "flow_type": "welcome",
            "active": True,
            "config": {"send_time": "9:00 AM", "timezone": "UTC"},
            "steps": [
                {
                    "template_id": template_ids[0],
                    "step_order": 0,
                    "delay_days": 0,
                    "delay_hours": 0,
                    "delay_minutes": 0,
                },
                {
                    "template_id": template_ids[1],
                    "step_order": 1,
                    "delay_days": 1,
                    "delay_hours": 0,
                    "delay_minutes": 0,
                },
                {
                    "template_id": template_ids[2],
                    "step_order": 2,
                    "delay_days": 3,
                    "delay_hours": 0,
                    "delay_minutes": 0,
                },
            ],
        }

        response = await client.post(f"{API_BASE_URL}/flows", json=flow_data)
        if response.status_code == 201:
            flow = response.json()
            flow_id = flow["id"]
            print(f"✓ Created flow: {flow['name']} (ID: {flow_id})")
        else:
            print(f"✗ Failed to create flow: {response.text}")
            return

        # Step 3: Enroll recipients
        print("\nEnrolling recipients...")

        recipients = [
            "redacted@shadowtag-v4.local",
            "redacted@shadowtag-v4.local",
            "redacted@shadowtag-v4.local",
        ]

        enroll_data = {"flow_id": flow_id, "recipient_emails": recipients}

        response = await client.post(f"{API_BASE_URL}/flows/bulk-enroll", json=enroll_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Enrolled {result['enrolled_count']} recipients")
            if result["failed_count"] > 0:
                print(f"✗ Failed to enroll {result['failed_count']} recipients")
                for error in result["errors"]:
                    print(f"  - {error}")
        else:
            print(f"✗ Failed to enroll recipients: {response.text}")

        print("\n✓ Welcome flow setup complete!")
        print(f"Flow ID: {flow_id}")
        print("Recipients will receive:")
        print("  - Email 1: Immediately")
        print("  - Email 2: After 1 day")
        print("  - Email 3: After 3 days")


if __name__ == "__main__":
    asyncio.run(create_welcome_flow_example())
