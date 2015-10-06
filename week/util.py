import urllib, urlparse, re, os, ConfigParser, logging, uuid, logging.config, types, datetime, json, calendar,random
from django.conf import settings
log=logging.getLogger(__name__)

from pyquery import PyQuery as pq

from django.template import RequestContext

def rip_playlist(filename=None, path=None, episode=None):
    '''prepare lookups for later rows.'''
    from week.models import *
    if not episode:
        import ipdb;ipdb.set_trace()
        print 'need episode'
        return False
    if not filename and not path:
        return False
    lookups={}
    VALID_ROWS={'artist':'artist', 
                
                'song':'song', 
                'track':'song',
                
                'album':'album',
                'album / format':'albumformat',
                'year':'year',
                }
    if filename:
        dom=pq(filename=filename)
    else:
        print 'not implemented'
        return False
    import ipdb;ipdb.set_trace()
    row=dom("table tr th.song")
    if not row:
        return False
    for ii, el in enumerate(row):
        val=el.text and el.text.lower()
        if not val:continue
        if val in VALID_ROWS:
            lookups[ii]=VALID_ROWS[val]
    possibly_song_rows=dom("table tr")
    ii=0
    while 1:
        songdata={}
        tr=possibly_song_rows.eq(ii)
        
        if not tr:
            break
        ii+=1
        tds=tr("td.song")
        if len(tds)>10:
            continue
        if len(tds)<2:
            continue
        for tdnum in lookups:
            td=tds.eq(tdnum)
            if not td:
                break
            songdata[lookups[tdnum]]=td.text()
        #now we have something like {'song':'hallelujah', 'year':'2001'}
        
        songdata=patchup(songdata)
        
        song=dict2song(songdata)
        if song:
            ps=PlayedSong(song=song, episode=episode)
            ps.save()
        try:
            print ps
        except:
            print repr(ps)
        
def patchup(songdata):
    '''some djs have magical formats'''
    if 'albumformat' in songdata:
        songdata['album']=songdata['albumformat'].split('('[0])
    if 'year' in songdata:
        try:
            val = int(songdata['year'])
            songdata['year']=str(val)
        except:
            try:
                val=int(songdata['year'].split('/')[0])
                songdata['year']=str(val)
            except:
                del songdata['year']
    for k,v in songdata.items():
        songdata[k]=v.strip('"').strip("'").strip()
    return songdata
        
def dict2song(dict):
    from week.models import *
    if not dict:
        return False
    if not 'song' in dict or not dict['song']:
        return False
    if not 'artist' in dict or not dict['artist']:
        return False
    song=Song(name=dict['song'])
    if 'year' in dict and dict['year']:
        song.year=dict['year']
    artist, created=Artist.objects.get_or_create(name=dict['artist'])    
    if 'album' in dict and dict['album']:
        if 'year' in dict:
            album, created=Album.objects.get_or_create(name=dict['album'], year=dict['year'])
        else:
            album, created=Album.objects.get_or_create(name=dict['album'])
        album.artists.add(artist)
        song.album=album
    if 'label' in dict:
        label, created=Label.objects.get_or_create(name=dict['label'])
        song.label=label
    song.save()
    song.artists.add(artist)
    exi=Song.objects.filter(name=song.name, year=song.year, artists=song.artists.all(), label=song.label).exists()
    if exi.exists():
        import ipdb;ipdb.set_trace()
        song.delete()
        song = exi[0]
    return song

def adminify(*args):
    for func in args:
        name=None
        if not name:
            if func.__name__.startswith('my'):
                name=func.__name__[2:]
            else:
                name=func.__name__
            name = name.replace('_', ' ')
        func.allow_tags=True
        func.short_description=name

def strip_html(text):
    def fixup(m):
        text = m.group(0)
        if text[:1] == "<":
            return "" # ignore tags
        if text[:2] == "&#":
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        elif text[:1] == "&":
            import htmlentitydefs
            entity = htmlentitydefs.entitydefs.get(text[1:-1])
            if entity:
                if entity[:2] == "&#":
                    try:
                        return unichr(int(entity[2:-1]))
                    except ValueError:
                        pass
                else:
                    return unicode(entity, "iso-8859-1")
        return text # leave as is
    return re.sub("(?s)<[^>]*>|&#?\w+;", fixup, text)

def save_image_locally(url):
    """randomize name, and return name of image found at end of the url
    save it to static/aimg/name[0]/name"""

    parts=urlparse.urlparse(url)
    f,ext=os.path.splitext(parts.path)
    rnd=str(uuid.uuid4())
    if not ext:
        ext='.jpg'
        #stick a .jpg on there.
    fn=rnd+ext
    outdir='/home/ernie/RD3/rd3/static/aimg/%s/'%rnd[0]
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    outpath=outdir+fn
    try:
        urllib.urlretrieve(url, outpath)
    except Exception, e:
        log.error('error saving url %s %s',url, e)
        return None
    return fn

import sys
import traceback
def format_exception(maxTBlevel=10):
    cla, exc, trbk = sys.exc_info()
    excName = cla.__name__
    try:
        excArgs = exc.__dict__["args"]
    except KeyError:
        excArgs = "<no args>"
    excTb = traceback.format_tb(trbk, maxTBlevel)
    res='%s\n%s\n%s\n%s'%(excName, str(exc)[:100]+'...', excArgs, ''.join(excTb))
    return res

def r2r(template, request, context=None, lang=None):
    if not context:
        context={}
    from coffin.shortcuts import render_to_response
    return render_to_response(template, context, RequestContext(request))

def r2s(template, context=None):
    from coffin.shortcuts import render_to_string
    return render_to_string(template, dictionary=context)

def r2j(vals):
    return HttpResponse(json.dumps(vals), mimetype='text/html')



def get_nested_objects(obj):
    from django.contrib.admin.util import NestedObjects
    collector = NestedObjects(using='default')
    collector.collect([obj])
    return collector.nested()

def ipdb():
    import inspect
    try:
        par = inspect.stack()[1]
        desc = '%s line:%s' % (par[1], [par[2]])
    except:
        log.error('failed to inspect stack.')
        from util import ipdb;ipdb()
        desc='failed to inspect stack.'
    if settings.LOCAL:
        log.error('missed ipdb call. %s', desc)
        import ipdb;ipdb.set_trace()
    else:
        log.error('missed ipdb call. %s', desc)

def sqlp(statement):
    import sqlparse
    res = sqlparse.format(statement, reindent=True)
    print res

def make_safe_tag_name(ss):
    res = []
    OKS = ['-', '_', ' ']
    ss=ss.replace('_','-')
    for c in ss:
        if (c.isalnum() and ord(c)<=122) or c in OKS:
            res.append(c)
    combo=''.join(res)
    combo=combo.lower()
    return combo

       
def nice_sparkline(results,width,height):
    '''a better one, results now consists of value & label'''
    '''stick the labels for x into labels[rnd]
    
    to produce: make {'2014-05-24': 15.0, '2014-05-21': 155.0}
    then produce results with costres2=group_day_dat(costres, by='month',mindate=mindate)
    
    '''
    ii=0
    num_results=[]
    labels={}
    for total,label in results:
        label+=' %d'%two_sig(total)
        labels[ii]=label
        ii+=1
        num_results.append(total)
    data=','.join([str(s) for s in num_results])
    rnd=str(int(random.random()*100000))
    res = '<div sparkid="%s" class="sparkline-data">%s</div>'%(rnd,data)    
    res+='<script>$(document).ready(function(){labels[%s]=%s});</script>'%(rnd,json.dumps(labels))
    return res
    
def simple_sparkline(results, width, height):
    #itd be nice if this was way better for labelling and stuff.
    res = '<div class="simple-sparkline-data">%s</div>'%(','.join([str(s) for s in results]))
    return res

import datetime, tempfile, os, json

from django.shortcuts import HttpResponseRedirect, HttpResponse
from django.db import models
from django.conf import settings

from django.template import RequestContext

import logging
log=logging.getLogger(__name__)



class GoodModel(models.Model):
    
    #should add default modified & created here.

    created=models.DateTimeField(auto_now_add=True)
    modified=models.DateTimeField(auto_now=True)

    def clink(self, text=None, wrap=True,skip_btn=False,klasses=None, tooltip=None):
        if skip_btn:
            klass=''
        else:
            klass='btn btn-default'
        if klasses:
            klass+=' '.join(klasses)
        if wrap:
            wrap=''
        else:
            wrap=' nb'
        if not text:
            text=self
        if not tooltip:
            tooltip=''
        try:
            res=u'<a class="%s%s" title="%s" href="%s/week/%s/?id=%d">%s</a>'%(klass, tooltip, wrap, settings.ADMIN_EXTERNAL_BASE, self.__class__.__name__.lower(), self.id, text)
            return res
        except:
            res=u'<a class="%s%s" title="%s" href="%s/week/%s/?id=%d">%s</a>'%(klass, tooltip, wrap, settings.ADMIN_EXTERNAL_BASE, self.__class__.__name__.lower(), self.id, repr(text))
            return res
            

    def alink(self, text=None,wrap=True):
        if wrap:
            wrap=' nb'
        else:
            wrap=''
        if not text:
            text=self
        return u'<a class="btn btn-default" href="%s/week/%s/%d/">%s</a>'%(wrap,settings.ADMIN_EXTERNAL_BASE, self.__class__.__name__.lower(), self.id, text)

    class Meta:
        app_label='wfmu'
        abstract=True

def debu(func, *args, **kwgs):
    def inner(*args, **kwgs):
        try:
            return func(*args, **kwgs)
        except Exception, e:
            log.error('exception %s',e)
            if settings.LOCAL:
                import ipdb;ipdb.set_trace()
            else:
                return 'Error <contact Ernie>'
            return func(*args, **kwgs)
            return None
    inner.__doc__=func.__doc__
    inner.__name__=func.__name__
    return inner

def mktable(dat, rights=None, bigs=None, skip_false=False, nb=False,non_max_width=False):
    rows = []
    for row in dat:
        if not row:
            continue
        if type(row) not in [list, set, tuple]:
            row=[row,]
        if skip_false and not row[-1]:
            continue
        res = '<tr>'
        for ii, thing in enumerate(row):
            klasses = []
            if nb:
                klasses.append('nb')
            if rights and ii in rights:
                klasses.append('right')
            if bigs and ii in bigs:
                klasses.append('big')
            if klasses:
                res += '<td class="%s">%s</td>' % (' '.join(klasses), thing)
            else:
                res += '<td>%s</td>' % (thing)
        rows.append(res+'</tr>')
    tblklass='table thintable'
    tblstyle=''
    if non_max_width:
        tblstyle='width:inherit;'
    return '<table class="%s" style="background-color:white;%s">%s</table>' % (tblklass,tblstyle,''.join(rows))

def nbspan(contents,klass=None,):
    if not contents:contents=''
    if not klass:
        klass=''
    res='<span class="nb %s">%s</span>'%(klass, contents)
    return res

def div(contents=None,klass=None):
    klasszone=''
    if klass:
        klasszone='class="%s"'%klass
    res='<div %s>%s</div>'%(klasszone,contents)
    return res