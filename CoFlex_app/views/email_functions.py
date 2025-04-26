from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import escape
from django.conf import settings
from datetime import datetime
from typing import Dict, Any, Union, List, Optional


def send_verification_code_email(user, sender_email, recipient_email, verification_code, expiry_time: str):
    if user and sender_email and verification_code and expiry_time:
        context = {
            'user': {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            },
            'recipient_email': recipient_email,
            'verification_code': verification_code,
            'expiry_time': expiry_time,
            'current_year': datetime.now().year
        }

        # Render HTML email content
        html_message = render_to_string(f'emails/verification_code_email.html', context)

        # Create a simple plain-text version
        plain_message = f"""
           Hello {context.get('user', {}).get('first_name', '')},

           Your verification code is: {context.get('verification_code', '')}

           This code will expire in {context.get('expiry_time', '1 minute')}.

           Thank you,

           The CoFlex Team
           """

        # Send the email
        try:
            result = send_mail(
                subject="Your CoFlex Verification Code",
                message=plain_message,
                from_email=sender_email,
                recipient_list=[recipient_email],
                html_message=html_message,
                fail_silently=False
            )
            return result > 0
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    else:
        print('Error not enough data to send email')
        return


def send_booking_confirmation_email(user, sender_email, recipient_email, booking, booking_details, location):
    if user and sender_email and booking and booking_details and location:
        context = {
            'user': {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            },
            'booking': {
                'id': booking.booking_id,
                'created_date': booking.created_date,
                'created_time': booking.created_time.strftime('%H:%M:%S')
            },
            'booking_details': {
                'start_date': booking_details.start_date,
                'start_time': booking_details.start_time,
                'end_date': booking_details.end_date,
                'end_time': booking_details.end_time,
                'special_requests': booking_details.special_requests,
                'status': booking_details.status
            },
            'location': {
                'name': location.location_name,
                'code': location.location_code,
                'address': location.location_details.address,
                'contact_phone': location.location_details.contact_phone,
                'website': location.location_details.website
            },
            'current_year': datetime.now().year
        }

        # Render HTML email content
        html_message = render_to_string('emails/booking_confirmation_email.html', context)

        # Create a simple plain-text version
        plain_message = f"""
            Hello {context['user']['first_name']} {context['user']['last_name']},

            Your booking at {context['location']['name']} has been confirmed!

            Booking ID: {context['booking']['id']}
            Date: {context['booking_details']['start_date']}
            Time: {context['booking_details']['start_time']} - {context['booking_details']['end_time']}

            Location Address: {context['location']['address']}
            Contact Phone: {context['location']['contact_phone']}

            Thank you for using CoFlex!
            """

        # Send the email
        try:
            result = send_mail(
                subject=f"Your CoFlex Booking Confirmation - {context['booking']['id']}",
                message=plain_message,
                from_email=sender_email,
                recipient_list=[recipient_email],
                html_message=html_message,
                fail_silently=False
            )
            return result > 0
        except Exception as e:
            print(f"Error sending booking confirmation email: {e}")
            return False
    else:
        print('Error: Not enough data to send booking confirmation email')
        return False


def send_subscription_confirmation_email(user, sender_email, recipient_email, subscription, subscription_details,
                                         payment_details, card_details_last_four=None):
    if user and sender_email and subscription and subscription_details and payment_details:

        subscription_plan = subscription_details.subscription_plan.replace("_", " ").title()
        type = subscription_details.subscription_type.capitalize()
        status = subscription_details.subscription_status.replace("_", " ").title()
        method = payment_details.payment_method.replace("_", " ").title()
        payment_status = payment_details.payment_status.capitalize()
        context = {
            'user': {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            },
            'subscription': {
                'start_date': subscription_details.subscription_from_date,
                'end_date': subscription_details.subscription_till_date,
                'type': type,
                'plan': subscription_plan,
                'status': status,
                'duration': subscription_details.subscription_duration,
                'days_left': subscription_details.days_left
            },
            'payment': {
                'amount': payment_details.charged_amount,
                'date': payment_details.charged_date,
                'time': payment_details.charged_time.strftime('%H:%M:%S') if payment_details.charged_time else '',
                'method': method,
                'status': payment_status
            },
            'current_year': datetime.now().year
        }

        # Add card details if available
        if card_details_last_four:
            context['payment']['card_last_four'] = card_details_last_four.last_four_digits

        # Render HTML email content
        html_message = render_to_string('emails/user_subscription_confirmation_email.html', context)

        # Create a simple plain-text version
        plain_message = f"""
            Hello {context['user']['first_name']} {context['user']['last_name']},

            Thank you for subscribing to CoFlex!

            Plan: {context['subscription']['plan']}
            Duration: {context['subscription']['type']}
            Valid from: {context['subscription']['start_date']} to {context['subscription']['end_date']}

            Payment Details:
            Amount: {context['payment']['amount']}
            Payment Method: {context['payment']['method']}
            Status: {context['payment']['status']}

            Thank you for choosing CoFlex!
            """

        # Send the email
        try:
            result = send_mail(
                subject="Your CoFlex Subscription Confirmation",
                message=plain_message,
                from_email=sender_email,
                recipient_list=[recipient_email],
                html_message=html_message,
                fail_silently=False
            )
            return result > 0
        except Exception as e:
            print(f"Error sending subscription confirmation email: {e}")
            return False
    else:
        print('Error: Not enough data to send subscription confirmation email')
        return False


def send_booking_cancellation_email(user, sender_email, recipient_email, booking, booking_details, location):
    if user and sender_email and booking and booking_details and location:

        # Get location details
        location_details = location.location_details

        context = {
            'user': {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            },
            'booking': {
                'id': booking.booking_id,
                'status': booking_details.status,
                'created_date': booking.created_date,
                'created_time': booking.created_time,
                'cancellation_date': datetime.now().strftime('%Y-%m-%d'),
                'cancellation_time': datetime.now().strftime('%H:%M:%S')
            },
            'location': {
                'name': location.location_name,
                'address': location_details.address,
                'contact_phone': location_details.contact_phone,
                'working_hours': location_details.working_hours,
                'website': location_details.website
            },
            'schedule': {
                'start_date': booking_details.start_date,
                'end_date': booking_details.end_date,
                'start_time': booking_details.start_time,
                'end_time': booking_details.end_time,
                'duration': booking_details.duration,
                'special_requests': booking_details.special_requests
            },
            'current_year': datetime.now().year
        }

        # Render HTML email content
        html_message = render_to_string('emails/booking_cancellation_email.html', context)

        # Create a simple plain-text version
        plain_message = f"""
            Hello {context['user']['first_name']} {context['user']['last_name']},

            Your booking #{context['booking']['id']} has been successfully cancelled.

            Location: {context['location']['name']})
            Address: {context['location']['address']}
            Originally scheduled for: {context['schedule']['start_date']} to {context['schedule']['end_date']}
            Time: {context['schedule']['start_time']} to {context['schedule']['end_time']}

            If you didn't request this cancellation, please contact our support team immediately.

            Thank you for using CoFlex!
            """

        # Send the email
        try:
            result = send_mail(
                subject="Your CoFlex Booking Cancellation Confirmation",
                message=plain_message,
                from_email=sender_email,
                recipient_list=[recipient_email],
                html_message=html_message,
                fail_silently=False
            )
            return result > 0
        except Exception as e:
            print(f"Error sending booking cancellation email: {e}")
            return False
    else:
        print('Error: Not enough data to send booking cancellation email')
        return False