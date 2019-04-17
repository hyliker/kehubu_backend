import magic
from django.db.models import signals
from django.dispatch import receiver
from .models import Attachment


@receiver(signals.pre_save, sender=Attachment)
def attachment_pre_save(sender, instance, **kwargs):
    if instance.file:
        instance.mimetype = magic.from_buffer(instance.file.read(1024), mime=True)