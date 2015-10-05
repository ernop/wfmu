# wfmu
wfmu project


# Ripping from recent archives:
    
    programs=$(".programs");
    $.each(programs, function(index, prog){console.log($(prog).find('.show-title-link').attr('href'), "==", $(prog).find('.show-title-link').text(), "==", $(prog).find('.djs').text())})
    
==status==

# got 69 mp3s
# got show lists

==not done==

# rip shows, labels, songs etc.
# other stuff
# listen
# convert Song => SongInShow, 
# make new Song[==song+artist+album] table

===bob brainen===
    
    rows=$("tr[valign=top]")
    results=[]
    $.each(rows, function(index, row){
        row=$(row)
        artist=$($(row).find('td')[0]).text().replace(/^\s+|\s+$/g, '')
        song=$($(row).find('td')[1]).text().replace(/^\s+|\s+$/g, '')
        album=$($(row).find('td')[2]).text().replace(/^\s+|\s+$/g, '').split('(')[0].replace(/^\s+|\s+$/g, '')
        year=$($(row).find('td')[3]).text().replace(/^\s+|\s+$/g, '')
        if (artist && song && year){
            results.push(artist+'=='+song+'=='+album+'=='+year)
        }
    })
    $.each(results, function(a,b){
        console.log(b)    
    })

%cpaste
lines=open('brainen.txt','r').readlines()
ep=Episode.objects.get(id=2)
import ipdb;ipdb.set_trace()
for line in lines:
    artist, song, album, year=line.strip().split('==')
    try:
        int(year)
        year=datetime.datetime(year=int(year), month=1, day=1)
    except:
        year=None
    ar=Artist.objects.filter(name=artist)
    if ar.exists():
        ar=ar[0]
    else:
        ar=Artist(name=artist)
        ar.save()
    albums=Album.objects.filter(artists=ar, am=album)
    if albums.exists():
        alb=albums[0]
    else:
        alb=Album(year=year, label=None, name=album)
        alb.save()
        alb.artists.add(ar)
    sng=Song(episode=ep, album=alb, name=song)
    sng.save()
    sng.artists.add(ar)
--