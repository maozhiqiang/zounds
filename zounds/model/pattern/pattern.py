from __future__ import division
from time import time

from zounds.model.model import Model
from zounds.analyze.feature.rawaudio import AudioFromDisk,AudioFromMemory
from zounds.pattern import usecs,put

class MetaPattern(type):
    
    _impl = {}
    
    def __init__(self,name,bases,attrs):
        self._impl[name] = self
        super(MetaPattern,self).__init__(name,bases,attrs)
    
    def _item_cls(self,item):
        return self._impl[item['_type']]
    
    def __getitem__(self,key):
        item = self.controller()[key]
        try:
            return self._item_cls(item).fromdict(item,stored = True)
        except TypeError:
            return [self._item_cls(i).fromdict(i,stored = True) for i in item]
    
    def _store(self,pattern):
        pattern.stored = time()
        self.controller().store(pattern.todict())
    
    def _convert(self,data):
        return [self._item_cls(d).fromdict(d,stored = True) for d in data]
    
    def contained_by(self,*frame_ids):
        d = self.controller().contained_by(*frame_ids)
        
        for k in d.iterkeys():
            d[k] = self._convert(d[k])
        
        return d

    def recent_patterns(self,how_many = 10,exclude_user = None):
        results = self.controller().recent_patterns(how_many,exclude_user)
        return self._convert(results)
    
    def patterns_by_user(self,source,how_many = 10):
        results = self.controller().patterns_by_user(source,how_many)
        return self._convert(results)
        
        

class Pattern(Model):
    '''
    A Pattern is the central concept in zounds.  Patterns can be nested.
    a "leaf" pattern represents a list of ids which point to audio frames.
    A "branch" pattern points to other patterns.
    '''
    __metaclass__ = MetaPattern
    
    def __init__(self,_id,source,external_id):
        Model.__init__(self)
        
        self.source = source
        self.external_id = external_id
        self._id = _id
        self._data = {'source'      : self.source,
                      'external_id' : self.external_id,
                      '_id'         : self._id} 
        
        self._fc = None
    
    @property
    def framecontroller(self):
        if not self._fc:
            self._fc = self.env().framecontroller
        return self._fc
    
    
    def audio_extractor(self,needs = None):
        raise NotImplemented()
    
    
    def data(self):
        return self._data

class FilePattern(Pattern):
    '''
    Represents a pattern in the form of an audio file on disk that has not 
    yet been stored 
    '''
    
    def __init__(self,_id,source,external_id,filename):
        Pattern.__init__(self,_id,source,external_id)
        self.filename = filename

    def audio_extractor(self, needs = None):
        e = self.__class__.env()
        return AudioFromDisk(e.samplerate,
                             e.windowsize,
                             e.stepsize,
                             self.filename,
                             needs = needs)

class DataPattern(Pattern):
    '''
    Represents a pattern in the form of an in-memory numpy array of audio 
    samples that has not yet been stored
    '''
    def __init__(self,_id,source,external_id,samples):
        Pattern.__init__(self,_id,source,external_id)
        self.samples = samples
        
    def audio_extractor(self,needs = None):
        e = self.__class__.env()
        return AudioFromMemory(e.samplerate,
                               e.windowsize,
                               e.stepsize,
                               self.samples,
                               needs = needs)
