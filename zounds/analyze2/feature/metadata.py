from __future__ import division
import numpy as np
from zounds.analyze2.extractor import Extractor,SingleInput
from zounds.analyze2 import chunksize

class MetaDataExtractor(Extractor):
    
    def __init__(self,pattern,key = None,needs = None):
        Extractor.__init__(self,needs = needs,key=key)
        self.pattern = pattern
        self.store = False
        self.finite = False
    
    def dim(self,env):
        raise NotImplementedError()
    
    @property
    def dtype(self):
        raise NotImplementedError()
    
    def _process(self):
        l = len(self.input[self.sources[0]])
        return [self.pattern.data()] * l


class LiteralExtractor(SingleInput):
    
    def __init__(self,dtype,needs = None, key = None):
        SingleInput.__init__(self, needs = needs, key = key)
        self._dtype = dtype
        self.finite = False
    
    def dim(self,env):
        return 1
    
    @property
    def dtype(self):
        return self._dtype
    
    def _process(self):
        return self.in_data[0][self.key]

class CounterExtractor(Extractor):
    
    def __init__(self,needs = None, key = None):
        Extractor.__init__(self,needs = needs, key = key)
        self.n = 0
        self.finite = False
    
    def dim(self,env):
        return ()

    @property
    def dtype(self):
        return np.int32
    
    def _process(self):
        l = len(self.input[self.sources[0]])
        c = np.arange(self.n,self.n + l)
        self.n += l
        return c