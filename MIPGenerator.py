import numpy as np 
import scipy.ndimage
import os 
import imageio.v2 as imageio

import requests
import io

class MIPGenerator:
    def __init__(self, numpy_array:np.ndarray):
        self.numpy_array = numpy_array
        if len(self.numpy_array.shape) != 3:
            raise Exception('numpy_array must be 3D')

    def _project(self, angle:int) -> np.ndarray:
        array = self.numpy_array
        axis = 1
        vol_angle = scipy.ndimage.interpolation.rotate(array, angle=angle, reshape=False, axes = (1,2))
        MIP = np.amax(vol_angle, axis=axis)
        return MIP

    def _create_projection_list(self, frames:int=60) -> list:
        angles = np.linspace(0, 360, frames)
        projection_list = []
        for i in angles:
            MIP = self._project(i)
            MIP = self.flip_MIP(MIP)
            projection_list.append(MIP)
            print(f'{i} degrees')
        return projection_list

    def create_gif(self, filename:str, directory:str, frames:int=60, delay:float=10):
        delay = delay/1000
        filepath = os.path.join(directory, filename + '.gif')
        projection_list = self._create_projection_list(frames)
        imageio.mimsave(filepath, projection_list, duration=delay)

    def flip_MIP(self, MIP:np.ndarray):
        MIP = np.flip(MIP, axis=0)
        return MIP