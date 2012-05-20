import numpy as np


from environment import Environment
from analyze.extractor import SingleInput
from model.pipeline import Pipeline

# TODO: Write tests!
class Learned(SingleInput):
    '''
    A thin wrapper around a learned feature
    '''
    
    def __init__(self,
                  pipeline_id = None,
                  dim = None,
                  dtype = None,
                  needs = None, 
                  nframes = 1, 
                  step = 1, 
                  key = None):
        
        
        SingleInput.__init__(\
                        self, needs=needs,nframes=nframes,step=step,key=key)
        self.pipeline = Pipeline[pipeline_id]
        self._dim = dim
        self._dtype = dtype
        self.env = Environment.instance
    
    
    def dim(self,env):
        return self._dim
    
    @property
    def dtype(self):
        return self._dtype
    
    def _process(self):
        data = np.array(self.in_data[:self.nframes])
        data = data.reshape(np.product(data.shape))
        return self.pipeline(data)
    
    
        
    