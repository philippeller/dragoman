from __future__ import absolute_import
'''Module providing a data base class for translation methods'''
import numpy as np
import pynocular as pn

__license__ = '''Copyright 2019 Philipp Eller

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.'''


class Translation():
    '''Base class for translation methods'''

    def __init__(self,
                 source, 
                 *args,
                 source_needs_grid=False,
                 dest_needs_grid=False,
                 **kwargs):

        self.source = source
        self.source_has_grid = isinstance(self.source, (pn.GridData, pn.GridArray, pn.Grid))
        if source_needs_grid:
            assert self.source_has_grid, 'Source must provide grid'
        self.dest = self.generate_destination(*args, **kwargs)
        self.dest_has_grid = isinstance(self.dest, (pn.GridData, pn.GridArray, pn.Grid))
        if dest_needs_grid:
            assert self.dest_has_grid, 'Destination must provide grid'

        if self.dest_has_grid:
            self.wrt = self.dest.grid.vars
        elif self.source_has_grid:
            self.wrt = self.source.grid.vars
        else:
            self.wrt = self.dest.vars

        # checks
        if not set(self.wrt) <= set(source.vars):
            raise TypeError('the following variables are missing in the source: %s'%', '.join(set(self.vars) - (set(self.vars) & set(source.vars))))

        self.source_sample = None
        self.dest_sample = None

    def generate_destination(self, *args, **kwargs):
        '''Correctly set up a destination data format
        depending on the supplied input
        
        Parameters
        ----------
        args, kwargs

        '''
        if len(args) == 1 and len(kwargs) == 0:
            dest = args[0]
            if isinstance(dest, pn.GridData):
                grid = dest.grid
                grid.initialize(self.source)
                return pn.GridData(grid)
            if isinstance(dest, pn.Grid):
                grid = dest
                grid.initialize(self.source)
                return pn.GridData(grid)
            if isinstance(dest, pn.PointData):
                return dest

        # check if source has a grid and if any args are in there
        if isinstance(self.source, pn.GridData):
            dims = []
            for arg in args:
                # in thsio case the source may have a grid, get those edges
                if isinstance(arg, str):
                    if arg in self.source.grid.vars:
                        dims.append(self.source.grid[arg])
                        continue
                dims.append(arg)
            args = dims

        # instantiate
        grid = pn.grid.Grid(*args, **kwargs)
        grid.initialize(self.source)

        return pn.GridData(grid)

    def prepare_source_sample(self, flat=True, array=True):
        self.source_sample = [self.source.get_array(var, flat=flat) for var in self.wrt]
        if array:
            self.source_sample = np.stack(self.source_sample)

    def prepare_dest_sample(self, flat=True, array=True):
        self.dest_sample = [self.dest.get_array(var, flat=flat) for var in self.wrt]
        if array:
            self.dest_sample = np.stack(self.dest_sample)

    def setup(self):
        pass

    def run(self):

        self.setup()

        for var in self.source.vars:
            if var in self.wrt:
                continue
            source_data = self.source[var]
            result = self.eval(source_data)
            self.dest[var] = result
        return self.dest

    def eval(self, data):
        raise NotImplementedError()

    def get_empty_output_array(self, element_shape=tuple(), fill_value=np.nan):
        '''make empty array in shape of destinaion
    
        element_shape : tuple
            additional dimensions of the output
        fill_value : value
            fill value
        '''
        if fill_value is None:
            return np.empty(self.dest.array_shape + element_shape)
        return np.full(self.dest.array_shape + element_shape, fill_value)

