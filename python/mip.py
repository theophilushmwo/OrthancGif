import numpy as np
import scipy.ndimage
import imageio
import requests
import io
import orthanc

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
        return MIP

    def _create_projection_list(self) -> list:
        angles = np.linspace(0, self.projection, self.frames)
        projection_list = []
        for i in angles:
            MIP = self._project(i)
            MIP = self.flip_MIP(MIP)
            projection_list.append(MIP)
        return projection_list

    def create_gif(self, output) -> None:
        projection_list = self._create_projection_list()
        imageio.mimwrite(output, projection_list, format='.gif', duration=self.delay)

    def flip_MIP(self, MIP: np.ndarray):
        MIP = np.flip(MIP, axis=0)
        return MIP