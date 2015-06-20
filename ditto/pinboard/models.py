from django.core.validators import URLValidator
from django.db import models

from ditto.ditto.models import DittoAccount, DittoItem


class Account(DittoAccount):
    # max_length derived from DittoAccount.username max_length plus
    # 21 characters for ':12345...'.
    api_token = models.CharField(null=False, blank=False, max_length=51,
                    help_text='From https://pinboard.in/settings/password eg, "philgyford:1234567890ABCDEFGHIJ"')

    @property
    def service_name(self):
      return "Pinboard"


class Bookmark(DittoItem):
    account = models.ForeignKey(Account, null=False, blank=False)

    # `url` in the Pinboard API:
    url = models.TextField(null=False, blank=False, unique=True,
                validators=[URLValidator()])

    # `dt` in the Pinboard API:
    post_time = models.DateTimeField(null=False, blank=False)

    # `extended` in the Pinboard API:
    description = models.TextField(null=False, blank=True,
                    help_text="The 'extended' text description.")

    # `toread` in the Pinboard API:
    to_read = models.BooleanField(default=False, null=False, blank=False)

    shared = models.BooleanField(default=True, null=False, blank=False)

    # Up to 100 tags
    # Up to 255 chars each. No commas or whitespace.
    # Private tags start with a period.
    # TODO tags

    def save(self, *args, **kwargs):
        self.summary = self.description
        super(Bookmark, self).save(*args, **kwargs)

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('bookmark_details', args=[str(self.id)])

