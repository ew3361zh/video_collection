from django.db import models
from urllib import parse
from django.core.exceptions import ValidationError

# Create your models here.
class Video(models.Model):
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=400)
    notes = models.TextField(blank=True, null=True)
    video_id = models.CharField(max_length=40, unique=True)

    def save(self, *args, **kwargs):
        # extract video id from youtube url
        # if not self.url.startswith('https://www.youtube.com/watch'):
        #     raise ValidationError(f'Non-YouTube URL {self.url}')
        url_components = parse.urlparse(self.url)

        if url_components.scheme != 'https':
            raise ValidationError(f'Non-YouTube URL {self.url}')

        if url_components.netloc != 'www.youtube.com':
            raise ValidationError(f'Non-YouTube URL {self.url}')

        if url_components.path != '/watch':
            raise ValidationError(f'Non-YouTube URL {self.url}')
            
        query_string = url_components.query
        if not query_string:
            raise ValidationError(f'Invalid YouTube URL {self.url}')
        parameters = parse.parse_qs(query_string, strict_parsing=True)
        v_parameters_list = parameters.get('v') # return None if no key found, e.g. no v key for no video id
        if not v_parameters_list: # check if None or empty list
            raise ValidationError(f'Invalid YouTube URL, missing parameters {self.url}')
        self.video_id = v_parameters_list[0] # string

        super().save(*args, **kwargs)


    def __str__(self):
        return f'ID: {self.pk}, Name: {self.name}, URL: {self.url}, Video_ID: {self.video_id}, Notes: {self.notes[:200]}'