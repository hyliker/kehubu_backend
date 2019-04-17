from django.db import models
from django.conf import settings
from mptt.models import MPTTModel, TreeForeignKey
from model_utils.models import TimeStampedModel
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill


class Category(MPTTModel, TimeStampedModel):
    group = models.ForeignKey('kehubu.Group', on_delete=models.CASCADE,
                              related_name='forum_category_set')
    name = models.CharField(max_length=24, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                            related_name='children')
    description = models.TextField(blank=True)
    priority = models.PositiveSmallIntegerField(default=0)
    icon = ProcessedImageField(upload_to="uploads/forum.Category.icon/%Y/%m/%d/",
                               processors=[ResizeToFill(200, 200)],
                               format='PNG',
                               options={'quality': 80},
                               blank=True)
    def __str__(self):
        return self.name


class Topic(TimeStampedModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='forum_topic_set')
    title = models.CharField(max_length=128)
    content = models.TextField()
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    @property
    def summary(self):
        return self.content[:200]


class Post(TimeStampedModel):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='forum_post_set')
    content = models.TextField()

    def __str__(self):
        return self.content[:50]

    @property
    def summary(self):
        return self.content[:200]


class Attachment(TimeStampedModel):
    group = models.ForeignKey('kehubu.Group', on_delete=models.CASCADE)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='forum_attachment_set')
    file = models.FileField(upload_to="forum.Attachment.file/%Y/%m/%d/")
    mimetype = models.CharField(max_length=24, editable=False)

    def __str__(self):
        return self.file.name