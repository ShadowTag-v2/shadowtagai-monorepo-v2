"""Example: Sending Transactional Emails

This example shows how to send transactional emails like:
- Order confirmations
- Password resets
- Account notifications
"""

import asyncio

import httpx

API_BASE_URL = "http://localhost:8000/api/v1/email"


async def send_order_confirmation():
    """Send an order confirmation email"""
    async with httpx.AsyncClient() as client:
        # Create order confirmation template
        template_data = {
            "name": "order_confirmation",
            "subject": "Order Confirmation #{{ order_id }}",
            "body_html": """
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h1>Order Confirmed!</h1>
                    <p>Hi {{ customer_name }},</p>
                    <p>Thank you for your order. We've received your payment and are processing your order.</p>

                    <div style="background: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h2>Order Details</h2>
                        <p><strong>Order ID:</strong> #{{ order_id }}</p>
                        <p><strong>Total:</strong> ${{ order_total }}</p>
                        <p><strong>Estimated Delivery:</strong> {{ delivery_date }}</p>
                    </div>

                    <h3>Items Ordered:</h3>
                    <ul>
                        {% for item in items %}
                        <li>{{ item }}</li>
                        {% endfor %}
                    </ul>

                    <p>You can track your order status at:</p>
                    <a href="https://shadowtag_v4.com/orders/{{ order_id }}" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0;">Track Order</a>

                    <p style="margin-top: 30px; color: #666;">
                        Questions? Contact us at support@shadowtag_v4.com
                    </p>
                </body>
                </html>
            """,
            "body_text": """
                Order Confirmed!

                Hi {{ customer_name }},

                Thank you for your order. Order ID: #{{ order_id }}
                Total: ${{ order_total }}
                Estimated Delivery: {{ delivery_date }}

                Track your order: https://shadowtag_v4.com/orders/{{ order_id }}
            """,
            "variables": ["customer_name", "order_id", "order_total", "delivery_date", "items"],
        }

        print("Creating order confirmation template...")
        response = await client.post(f"{API_BASE_URL}/templates", json=template_data)

        if response.status_code == 201:
            template = response.json()
            print(f"✓ Template created: {template['name']}")

            # Send order confirmation email
            print("\nSending order confirmation email...")

            send_data = {
                "recipient_email": "redacted@shadowtag-v4.local",
                "template_id": template["id"],
                "variables": {
                    "customer_name": "John Doe",
                    "order_id": "12345",
                    "order_total": "99.99",
                    "delivery_date": "March 25, 2024",
                    "items": ["Product A", "Product B", "Product C"],
                },
            }

            response = await client.post(f"{API_BASE_URL}/send", json=send_data)

            if response.status_code == 201:
                email = response.json()
                print("✓ Order confirmation sent!")
                print(f"  Email ID: {email['id']}")
                print(f"  Status: {email['status']}")
                print(f"  Tracking ID: {email['tracking_id']}")
            else:
                print(f"✗ Failed to send email: {response.text}")
        else:
            print(f"✗ Failed to create template: {response.text}")


async def send_password_reset():
    """Send a password reset email"""
    async with httpx.AsyncClient() as client:
        # Create password reset template
        template_data = {
            "name": "password_reset",
            "subject": "Reset Your Password",
            "body_html": """
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h1>Reset Your Password</h1>
                    <p>Hi {{ user_name }},</p>
                    <p>We received a request to reset your password. Click the button below to create a new password:</p>

                    <a href="{{ reset_url }}" style="background: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0;">Reset Password</a>

                    <p>This link will expire in 1 hour.</p>

                    <p>If you didn't request this, you can safely ignore this email.</p>

                    <p style="margin-top: 30px; color: #666; font-size: 14px;">
                        For security reasons, this link can only be used once.
                    </p>
                </body>
                </html>
            """,
            "body_text": """
                Reset Your Password

                Hi {{ user_name }},

                We received a request to reset your password.

                Reset your password here: {{ reset_url }}

                This link will expire in 1 hour.

                If you didn't request this, you can safely ignore this email.
            """,
            "variables": ["user_name", "reset_url"],
        }

        print("\nCreating password reset template...")
        response = await client.post(f"{API_BASE_URL}/templates", json=template_data)

        if response.status_code == 201:
            template = response.json()
            print(f"✓ Template created: {template['name']}")

            # Send password reset email
            print("\nSending password reset email...")

            send_data = {
                "recipient_email": "redacted@shadowtag-v4.local",
                "template_id": template["id"],
                "variables": {
                    "user_name": "Jane Smith",
                    "reset_url": "https://shadowtag_v4.com/reset-password?token=abc123xyz789",
                },
            }

            response = await client.post(f"{API_BASE_URL}/send", json=send_data)

            if response.status_code == 201:
                email = response.json()
                print("✓ Password reset email sent!")
                print(f"  Email ID: {email['id']}")
                print(f"  Status: {email['status']}")
            else:
                print(f"✗ Failed to send email: {response.text}")
        else:
            print(f"✗ Failed to create template: {response.text}")


async def main():
    """Run all examples"""
    print("=" * 60)
    print("Transactional Email Examples")
    print("=" * 60)

    await send_order_confirmation()
    print("\n" + "=" * 60 + "\n")
    await send_password_reset()

    print("\n" + "=" * 60)
    print("✓ All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
