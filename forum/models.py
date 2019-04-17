from django.db import models
from django.conf import settings
from mptt.models import MPTTModel, TreeForeignKey
from model_utils.models import TimeStampedModel
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Category(MPTTModel, TimeStampedModel):
    group = models.ForeignKey('kehubu.Group', on_delete=models.CASCADE,
                              related_name='forum_category_set')
    name = models.CharField(max_length=24)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                            related_name='children')
    description = models.TextField(blank=True)
    priority = models.PositiveSmallIntegerField(default=0)
    icon = ProcessedImageField(upload_to="uploads/forum.Category.icon/%Y/%m/%d/",
                               processors=[ResizeToFill(200, 200)],
                               format='PNG',
                               options={'quality': 80},
                               blank=True)

    topic_count = models.PositiveIntegerField(default=0)
    post_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('group', 'parent', 'name')

    def __str__(self):
        return self.name

    def clean(self):
        if self.parent is not None:
            if self.group != self.parent.group:
                raise ValidationError(_("Parent category must be in same group"))

    def update_topic_count(self):
        self.topic_count = self.topic_set.count()
        self.save()

    def update_post_count(self):
        topic_set = self.topic_set.all()
        self.post_count = Post.objects.filter(topic__in=topic_set).count()
        self.save()


class Topic(TimeStampedModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='forum_topic_set')
    title = models.CharField(max_length=128)
    content = models.TextField()
    is_published = models.BooleanField(default=True)
    post_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    @property
    def summary(self):
        return self.content[:200]

    def clean(self):
        if not self.category.group.has_member(self.creator):
            raise ValidationError(_("Only group member can create topic"))

    def update_post_count(self):
        self.post_count = self.post_set.count()
        self.save()


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

    def clean(self):
        if not self.topic.category.group.has_member(self.creator):
            raise ValidationError(_("Only group member can create post"))

class Attachment(TimeStampedModel):
    group = models.ForeignKey('kehubu.Group', on_delete=models.CASCADE)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='forum_attachment_set')
    file = models.FileField(upload_to="uploads/forum.Attachment.file/%Y/%m/%d/")
    mimetype = models.CharField(max_length=24, editable=False)

    def __str__(self):
        return self.file.name

    def clean(self):
        if not self.group.has_member(self.creator):
            raise ValidationError(_("Only group member can create attachment"))
