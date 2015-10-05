from django.db import models

from django.contrib.auth.models import User

from util import *

class DJ(GoodModel):
    name=models.CharField(max_length=200)
    class Meta:
        db_table='dj'  
        
    def __unicode__(self):
        return self.name or 'no name'

class MicBreak(GoodModel):
    show=models.ForeignKey('Show', related_name='micbreaks')
    start_time=models.DateTimeField(blank=True,null=True)
    length=models.IntegerField(blank=True,null=True)    
    class Meta:
        db_table='micbreak'    
        
    def __unicode__(self):
        return 'mic break show %s time %s'%(show, start_time or '')

class Show(GoodModel):
    name=models.CharField(max_length=200, blank=True, null=True)
    dj=models.ForeignKey('DJ', related_name='shows')
    mp3_initial=models.CharField(max_length=2)
    
    class Meta:
        db_table='show'
    
    def __unicode__(self):
        return self.name

class Episode(GoodModel):
    name=models.CharField(max_length=200, blank=True, null=True)
    show=models.ForeignKey(Show, related_name='episodes')
    dj=models.ForeignKey('DJ', related_name='episodes')
    mp3_filename=models.CharField(max_length=200, blank=True, null=True)
    mp3_length=models.IntegerField(blank=True, null=True) #seconds
    mp3_offset=models.FloatField(blank=True, null=True) #number of seconds from start of mp3 that the show actaly starts
    start_time=models.DateTimeField(blank=True,null=True) #real time start time
    length=models.IntegerField(blank=True,null=True) #seconds
    web_only=models.BooleanField(default=False)
    
    class Meta:
        db_table='episode'    
        
    def __unicode__(self):
        return 'episode "%s" of show "%s"'%(self.name or '', self.show or '')

class Album(GoodModel):
    name=models.CharField(max_length=200)
    year=models.DateTimeField(blank=True, null=True)
    label=models.ForeignKey('Label', blank=True, null=True, related_name='albums')
    artists=models.ManyToManyField('Artist', blank=True, related_name='albums') #can have many, dup with song.
    
    class Meta:
        db_table='album'        
        
    def __unicode__(self):
        return '%s (%s)'%(self.name or '', self.year and str(self.year) or 'none')
        
class Artist(GoodModel):
    name=models.CharField(max_length=200)
    class Meta:
        db_table='artist'      
        
    def __unicode__(self):
        return self.name or ''
        
class Label(GoodModel):
    name=models.CharField(max_length=200)
    class Meta:
        db_table='label'      
        
    def __unicode__(self):
        return self.name or ''
        
class Song(GoodModel): #song-in-show actually
    name=models.CharField(max_length=200)
    artists=models.ManyToManyField(Artist, related_name='songs')
    album=models.ForeignKey(Album, related_name='songs')
    start_time=models.DateTimeField(blank=True,null=True)
    length=models.IntegerField(blank=True,null=True)
    episode=models.ForeignKey(Episode, related_name='songs')
    
    class Meta:
        db_table='song'
        
    def __unicode__(self):
        return '%s by %s from album %s'%(self.name or '', ', '.join([str(artist) for artist in self.artists.all()] or ''), self.album or '')
        
class Comment(GoodModel):
    user=models.ForeignKey(User, related_name='comments')
    text=models.TextField()
    
    #all blank but one, big source of errors.
    song=models.ForeignKey(Song, related_name='comments', blank=True, null=True)
    artist=models.ForeignKey(Artist, related_name='comments', blank=True, null=True)
    album=models.ForeignKey(Album, related_name='comments', blank=True, null=True)
    micbreak=models.ForeignKey(MicBreak, related_name='comments', blank=True, null=True)
    show=models.ForeignKey(Show, related_name='comments', blank=True, null=True)
    episode=models.ForeignKey(Episode, related_name='comments', blank=True, null=True)
    dj=models.ForeignKey(DJ, related_name='comments', blank=True, null=True)
    
    class Meta:
        db_table='comment'
            
    def __unicode__(self):
        return 'comment by %s: "%s..."'%(self.user,self.text[:100])