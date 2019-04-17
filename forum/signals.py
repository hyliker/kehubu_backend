import magic
from django.db.models import signals
from django.dispatch import receiver
from .models import Attachment, Post, Category, Topic


@receiver(signals.pre_save, sender=Attachment)
def attachment_pre_save(sender, instance, **kwargs):
    if instance.file:
        instance.mimetype = magic.from_buffer(instance.file.read(1024), mime=True)


@receiver(signals.post_save, sender=Topic)
def topic_post_save(sender, instance, created, **kwargs):
    if created:
        instance.category.update_topic_count()


@receiver(signals.post_delete, sender=Topic)
def topic_post_delete(sender, instance, **kwargs):
    instance.category.update_topic_count()


@receiver(signals.post_save, sender=Post)
def post_post_save(sender, instance, created, **kwargs):
    if created:
        instance.topic.category.update_post_count()
        instance.topic.update_post_count()


@receiver(signals.post_delete, sender=Post)
def post_post_delete(sender, instance, **kwargs):
    instance.topic.category.update_topic_count()
    instance.topic.update_post_count()