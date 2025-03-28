import datetime

from django.utils.timezone import now
from datetime import timedelta
from .models import VerifiedUsers, SandSubscribedUsers

import os
import logging

# Absolute path for the log file
log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'django_cron.log')

logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s")


def delete_expired_users():
    try:
        users = VerifiedUsers.objects.filter(is_active=False)

        if users:
            for user in users:
                deletion_time = user.user_account_deletion.deletion_time
                time_difference = now() - deletion_time

                if time_difference > timedelta(days=30):
                    user.delete()
                    print(f'Deleted user {user.email} due to 30 days expiration.')
                    logging.info(f'Deleted user {user.email} due to 30 days expiration.')
                else:
                    print(f'User {user.email} is not yet eligible for deletion (less than 30 days)')
                    logging.info(f'User {user.email} is not yet eligible for deletion (less than 30 days)')
        else:
            print('No inactive users to delete.')
            logging.info('No inactive users to delete.')
    except Exception as e:
        print(f'Error in delete_expired_users: {str(e)}')
        logging.error(f'Error in delete_expired_users: {str(e)}')


def delete_unsuccessful_card_details():
    try:
        users_card_details = SandSubscribedUsers.objects.filter(is_subscribed=False)
        if users_card_details:
            for user in users_card_details:
                user.delete()
                logging.info(f'User {user.email} card details are being deleted at {datetime.datetime.now()}')
        else:
            pass
            logging.info(f'No users with unsuccessful card details to delete at {datetime.datetime.now()}')
    except Exception as e:
        print(f'Error in delete_expired_users: {str(e)}')
        logging.error(f'Error in delete_expired_users: {str(e)}')

