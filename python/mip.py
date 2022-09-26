import numpy as np
import scipy.ndimage
import imageio
from multiprocessing import Pool, cpu_count
from functools import partial
import io
import requests
import time

class MIPGenerator:
    def __init__(self, numpy_array: np.ndarray, frames, delay, projection):
        self.numpy_array = numpy_array
        self.frames = frames
        self.delay = delay / 1000
        self.projection = projection
        if len(self.numpy_array.shape) != 4:
            raise Exception('numpy_array must be 3D')

    def _project(self, angle: int) -> np.ndarray:
        vol_angle = scipy.ndimage.rotate(
            self.numpy_array, angle=angle, reshape=False, axes=(1, 2))
        MIP = np.amax(vol_angle, axis=1)
        MIP = np.flip(MIP, axis=0)
        return MIP

    def _create_projection_list(self) -> list:
        angles = np.linspace(0, self.projection, self.frames)
        nbCores = cpu_count() - 2
        # Create a pool with the function project
        pool = Pool(nbCores)
        projection_list = pool.map(self._project, angles)
        return projection_list

    def create_gif(self, output) -> None:
        print('Creating gif...')
        timer = time.time()
        projection_list = self._create_projection_list()
        print('Projection time: ', time.time() - timer)
        imageio.mimwrite(output, projection_list, format='.gif', duration=self.delay)

