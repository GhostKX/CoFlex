from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import StaffAccounts, StaffAccountsProfiles, StaffPhotoDetails, StaffEditMainEmail


@receiver(post_save, sender=StaffAccounts)
def staff_account_created(sender, instance, created, **kwargs):
    if created:
        StaffAccountsProfiles.objects.create(staff=instance)
        StaffPhotoDetails.objects.create(staff=instance)
        StaffEditMainEmail.objects.create(staff=instance)

