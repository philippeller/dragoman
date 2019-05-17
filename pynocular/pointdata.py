from __future__ import absolute_import
import numpy as np
import pandas
from scipy.interpolate import griddata

from pynocular.data import Data
from pynocular.stat_plot import *

__all__ = ['PointData']

class PointData(Data):
    '''
    Data Layer to hold point-type data structures (Pandas DataFrame, Dict, )
    '''
    def __init__(self, data=None):
        if data is None:
            data = {}
        super(PointData, self).__init__(data=data)

    @property
    def vars(self):
        '''
        Available variables in this layer
        '''
        if self.type == 'df':
            return list(self.data.columns)
        elif self.type == 'dict':
            return self.data.keys()
        else:
            return []

    def __len__(self):
        if self.type == 'df':
            return len(self.data)
        elif self.type == 'dict':
            return len(self.data[self.data.keys()[0]])

    @property
    def array_shape(self):
        '''
        the shape of a single variable
        '''
        return (len(self))

    def set_data(self, data):
        '''
        Set the data
        '''
        # TODO: run some compatibility cheks
        if isinstance(data, pandas.core.frame.DataFrame):
            self.type = 'df'
        elif isinstance(data, dict):
            self.type = 'dict'
        elif isinstance(data, np.ndarray):
            assert data.dtype.names is not None, 'unsctructured arrays not supported'
        self.data = data

    def get_array(self, var, flat=False):
        if self.type == 'df':
            arr = self.data[var].values
        else:
            arr = self.data[var]
        return arr

    def __getitem__(self, var):
        if isinstance(var, str):
            if var in self.vars:
                return self.get_array(var)
        else:
            # create new instance with mask or slice applied
            if self.type == 'df':
                return PointData(self.data[var])
            else:
                new_data = {}
                for key, val in self.data.items():
                    new_data[key] = val[var]
                return PointData(new_data)

    def add_data(self, var, data):
        # TODO do some checks of shape etc
        if self.type == 'struct_array':
            raise TypeError('cannot append rows to structured np array')
        self.data[var] = data

    def plot_scatter(self, x, y, c=None, s=None, cbar=False, fig=None, ax=None, **kwargs):
        plot_points_2d(self, x, y, c=c, s=s, cbar=cbar, fig=fig, ax=ax, **kwargs)

    def plot(self, x, y, *args, **kwargs):
        plot(self, x, y, *args, **kwargs)
