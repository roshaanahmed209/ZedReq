"""Email Sender Utility using Resend"""
import os
import resend
from typing import Optional

# Get API key from environment
RESEND_API_KEY = os.getenv('RESEND_API_KEY')

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY


def send_reservation_confirmation_email(email: str, promo_code: str) -> bool:
    """
    Send reservation confirmation email to user
    
    Args:
        email: User's email address
        promo_code: Generated promo code for the user
        
    Returns:
        True if email sent successfully, False otherwise
    """
    if not RESEND_API_KEY:
        print("Warning: RESEND_API_KEY not set, cannot send email")
        return False
    
    try:
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Your Seat is Reserved!</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f5f5f5;">
            <table role="presentation" style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 40px 20px; text-align: center;">
                        <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: #000000; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);">
                            <!-- Header -->
                            <tr>
                                <td style="padding: 40px 40px 30px; background: linear-gradient(135deg, #00B4D8 0%, #0096b8 100%); text-align: center;">
                                    <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: 300; letter-spacing: -1px;">ZedReq</h1>
                                </td>
                            </tr>
                            
                            <!-- Main Content -->
                            <tr>
                                <td style="padding: 40px; background-color: #000000;">
                                    <h2 style="margin: 0 0 20px; color: #ffffff; font-size: 28px; font-weight: 300; line-height: 1.3;">
                                        🎉 Your Seat is Reserved!
                                    </h2>
                                    <p style="margin: 0 0 24px; color: #cccccc; font-size: 16px; line-height: 1.6;">
                                        Thank you for reserving your spot at ZedReq! We're excited to have you join us on this journey to transform your career.
                                    </p>
                                    
                                    <!-- Promo Code Box -->
                                    <div style="background: rgba(0, 180, 216, 0.1); border: 2px solid #00B4D8; border-radius: 8px; padding: 24px; margin: 30px 0; text-align: center;">
                                        <p style="margin: 0 0 12px; color: #999; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">Your Promo Code</p>
                                        <p style="margin: 0; color: #00B4D8; font-size: 32px; font-weight: 700; letter-spacing: 2px; font-family: 'Courier New', monospace;">
                                            {promo_code}
                                        </p>
                                    </div>
                                    
                                    <p style="margin: 24px 0; color: #cccccc; font-size: 16px; line-height: 1.6;">
                                        Save this promo code! You'll receive exclusive early access and special discounts when we launch.
                                    </p>
                                    
                                    <!-- Referral Section -->
                                    <div style="background: rgba(0, 180, 216, 0.05); border-left: 4px solid #00B4D8; border-radius: 6px; padding: 24px; margin: 30px 0;">
                                        <h3 style="margin: 0 0 12px; color: #00B4D8; font-size: 20px; font-weight: 600;">
                                            💰 Get a Discount by Referring a Friend
                                        </h3>
                                        <p style="margin: 0; color: #cccccc; font-size: 15px; line-height: 1.6;">
                                            Share ZedReq with a friend and you'll both get a special discount when we launch! 
                                            We'll send you a unique referral link in a follow-up email.
                                        </p>
                                    </div>
                                    
                                    <!-- CTA Button -->
                                    <table role="presentation" style="width: 100%; margin: 30px 0;">
                                        <tr>
                                            <td style="text-align: center;">
                                                <a href="https://zedreq.ai" style="display: inline-block; padding: 16px 40px; background-color: #00B4D8; color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 500; font-size: 16px; transition: background-color 0.3s;">
                                                    Visit ZedReq
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <p style="margin: 30px 0 0; color: #999; font-size: 14px; line-height: 1.6;">
                                        We'll notify you as soon as we're ready to launch. Stay tuned for updates!
                                    </p>
                                </td>
                            </tr>
                            
                            <!-- Footer -->
                            <tr>
                                <td style="padding: 30px 40px; background-color: #0d0d0d; text-align: center; border-top: 1px solid #2a2a2a;">
                                    <p style="margin: 0 0 12px; color: #666; font-size: 14px;">
                                        © 2024 ZedReq. All rights reserved.
                                    </p>
                                    <p style="margin: 0; color: #666; font-size: 12px;">
                                        You're receiving this email because you reserved a seat at ZedReq.
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        r = resend.Emails.send({
            "from": "roshaanahmed290@gmail.com",
            "to": email,
            "subject": "🎉 Your Seat is Reserved at ZedReq!",
            "html": html_content
        })
        
        print(f"Email sent successfully to {email}: {r}")
        return True
        
    except Exception as e:
        print(f"Error sending email to {email}: {e}")
        return False
