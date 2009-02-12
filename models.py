# -*- coding: UTF-8 -*-
import datetime
import os.path
from django.conf import settings
from django.db import models

class DeadlineManager(models.Manager):
    def valid_news(self):
        today = datetime.date.today()
        return self.all().filter(date__gte = today)

class Deadline(models.Model):
    """
    deadline per il pycon
    """
    date = models.DateField()

    objects = DeadlineManager()

    def __unicode__(self):
        return "deadline: %s" % (self.date, )

    class Meta:
        ordering = ['date']

    def isExpired(self):
       today = datetime.date.today()
       return today > self.date

class DeadlineContent(models.Model):
    """
    Testo, multilingua, di una deadline
    """
    deadline = models.ForeignKey(Deadline)
    language = models.CharField(max_length = 3)
    body = models.TextField()

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class MultilingualContent(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    language = models.CharField(max_length = 3)
    content = models.CharField(max_length = 20)
    body = models.TextField()

import urlparse
from django.core.files.storage import FileSystemStorage

# definisco uno storage custom perché non uso MEDIA_DIR per memorizzare la
# roba sotto stuff
fs = FileSystemStorage(
    location = settings.STUFF_DIR,
    base_url = urlparse.urljoin(settings.MEDIA_URL, 'stuff/')
)

def _speaker_image_path(instance, filename):
    return os.path.join('speaker', instance.slug + os.path.splitext(filename)[1].lower())

class Speaker(models.Model):
    nome = models.CharField('nome e cognome speaker', max_length = 100)
    slug = models.SlugField()
    homepage = models.URLField(verify_exists = False, blank = True)
    attivita = models.CharField(max_length = 50, blank = True)
    settore = models.CharField(max_length = 50, blank = True)
    provenienza = models.CharField(max_length = 100, blank = True)
    immagine = models.ImageField(upload_to = _speaker_image_path, blank = True, storage = fs)
    bios = generic.GenericRelation(MultilingualContent)

    class Meta:
        ordering = ['nome']

    def __unicode__(self):
        return self.nome

    @models.permalink
    def get_absolute_url(self):
        return ('conference-speaker', (), { 'slug': self.slug })

TALK_DURATION = (
    (30, '30 minuti'),
    (45, '45 minuti'),
    (60, '60 minuti'),
    (90, '90 minuti'),
)
TALK_LANGUAGES = (
    ('it', 'Italiano'),
    ('en', 'Inglese'),
)

def _talk_slides_path(instance, filename):
    return os.path.join('slides', instance.slug + os.path.splitext(filename)[1].lower())

class Talk(models.Model):
    titolo = models.CharField('titolo del talk', max_length = 100)
    slug = models.SlugField()
    speaker = models.ForeignKey(Speaker)
    durata = models.IntegerField(choices = TALK_DURATION)
    lingua = models.CharField('lingua del talk', max_length = 3, choices = TALK_LANGUAGES)
    abstracts = generic.GenericRelation(MultilingualContent)
    slides = models.FileField(upload_to = _talk_slides_path, blank = True, storage = fs)
    video = models.URLField(verify_exists = False, blank = True)

    def __unicode__(self):
        return self.titolo
