from django.contrib import admin

from adminutil import *
# Register your models here.

from .models import *


class DJAdmin(OverriddenModelAdmin):
    list_display='id name myshow myepisodes'.split()
    search_fields=['name',]
    list_editable=['name',]
    def myshow(self, obj):
        return '<br>'.join([show.clink() for show in obj.shows.all()])
        
    def myepisodes(self, obj):
        return '<a href="../episode/?dj__id=%d">episodes</a>'%(obj.id)
        
    adminify(myshow, myepisodes)

class MicBreakAdmin(OverriddenModelAdmin):
    list_display='id myshow start_time length'.split()
    search_fields=['show__name',]
    def myshow(self,obj):
        return obj.show.clink()
    adminify(myshow)
    
class ShowAdmin(OverriddenModelAdmin):
    list_display='id myarchive myshowexists name mydj myepisodes mp3_initial'.split()
    search_fields=['name',]
    def mydj(self, obj):
        return obj.dj.clink()
        
    def myepisodes(self, obj):
        return '<a href="../episode?show__id=%d">episodes</a>'%(obj.id)
    
    def myarchive(self, obj):
        return obj.mp3_initial and '<a href=http://strelka.wfmu.org:5555/archive/%s/>archive</a>'%(obj.mp3_initial) or ''
        
    def myshowexists(self, obj):
        if not obj.mp3_initial:
            return False
        files=os.listdir('mp3')
        for file in files:
            if not file.endswith('.mp3'):
                continue
            if file.lower().startswith(obj.mp3_initial.lower()):
                return True
        return False
        
    adminify(mydj, myepisodes, myshowexists, myarchive)
    
class EpisodeAdmin(OverriddenModelAdmin):
    list_display='id name myshow mydj myplayed_songs mp3_filename mp3_length mp3_offset start_time length web_only'.split()
    search_fields=['name','show__name',]
    import django.contrib.admin.views
    
    def myplayed_songs(self, obj):
        return '<a href="../playedsong?episode=%d">songs (%d)</a>'%(obj.id, len(obj.played_songs.all()))
    
    def myshow(self,obj):
        return obj.show.clink()
    
    def mydj(self,obj):
        return obj.dj.clink()    
    
    adminify(myshow, mydj, myplayed_songs)
    
class AlbumAdmin(OverriddenModelAdmin):
    list_display='id name year mysongs myartists mylabel'.split()
    def myartists(self, obj):
        return '<br>'.join([artist.clink() for artist in obj.artists.all()])
    
    def mylabel(self, obj):
        return obj.label and obj.label.clink() or 'no label'
    
    def mysongs(self, obj):
        return '<br>'.join([song.clink(text=song.name) for song in obj.songs.all()])
    
    adminify(myartists, mylabel, mysongs)
    search_fields=['name',]
    
class ArtistAdmin(OverriddenModelAdmin):
    list_display='id name myalbums'.split()
    search_fields=['name',]
    def myalbums(self, obj):
        return '<br>'.join([album.clink() for album in obj.albums.all()])
        #return '<a href="../album?artists__id=%d">albums (%d)</a>'%(obj.id, obj.albums.count())
    adminify(myalbums)
    
class LabelAdmin(OverriddenModelAdmin):
    list_display='id name myalbums'.split()
    search_fields=['name',]
    def myalbums(self, obj):
        return '<a href="../album?label__id=%d">albums (%d)</a>'%(obj.id, obj.albums.count())
    
    adminify(myalbums)
    
class PlayedSongAdmin(OverriddenModelAdmin):
    list_display='id mysong myplayed_episode'.split()
    def mysong(self, obj):
        return obj.song.clink()
    
    def myplayed_episode(self, obj):
        return obj.episode.clink()    

    adminify(mysong, myplayed_episode)
    
class SongAdmin(OverriddenModelAdmin):
    list_display='id name year myplayed_episodes myartist myalbum  start_time length'.split()
    search_fields=['name',]
    
    @debu
    def myartist(self, obj):
        return '<br>'.join([artist.clink() for artist in obj.artists.all()])
    
    @debu
    def myalbum(self, obj):
        return obj.album and obj.album.clink() or 'no album'
    
    @debu
    def myplayed_episodes(self, obj):
        return '<br>'.join([ps.episode.clink() for ps in obj.plays.all()])
    
    adminify(myartist, myalbum, myplayed_episodes) #mylabels
    
class CommentAdmin(OverriddenModelAdmin):
    list_display='id text myrelated_object user'.split()
    search_fields=['text',]
    def myrelated_object(self, obj):
        if obj.dj:
            return obj.dj.clink()        
        if obj.micbreak:
            return obj.micbreak.clink()                
        if obj.show:
            return obj.show.clink()                
        if obj.episode:
            return obj.episode.clink()
        if obj.album:
            return obj.album.clink()        
        if obj.artist:
            return obj.artist.clink()        
        #if obj.label:
            #return obj.label.clink()
        if obj.song:
            return obj.song.clink()        
        return 'no related object'
        
    adminify(myrelated_object)

admin.site.register(DJ, DJAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Show, ShowAdmin)
admin.site.register(Song, SongAdmin)
admin.site.register(PlayedSong, PlayedSongAdmin)
admin.site.register(Episode, EpisodeAdmin)
admin.site.register(MicBreak, MicBreakAdmin)
admin.site.register(Label, LabelAdmin)
admin.site.register(Comment, CommentAdmin)