import numpy as np
import scipy.ndimage
import imageio
from multiprocessing import Pool, cpu_count
import imageio.core.util
import signal

def silence_imageio_warning(*args, **kwargs):
    pass

def Initializer():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


class MIPGenerator:
    def __init__(self, numpy_array: np.ndarray, frames, delay, projection):
        self.numpy_array = numpy_array
        self.frames = frames
        self.delay = delay / 1000
        self.projection = projection
        imageio.core.util._precision_warn = silence_imageio_warning

    def _project(self, angle: int) -> np.ndarray:
        vol_angle = scipy.ndimage.rotate(
            self.numpy_array, angle=angle, reshape=False, axes=(1, 2))
        MIP = np.amax(vol_angle, axis=1)
        MIP = np.flip(MIP, axis=0)
        return MIP

    def _create_projection_list(self) -> list:
        angles = np.linspace(0, self.projection, self.frames)
        nbCores = cpu_count() - 2
        pool = Pool(nbCores, initializer=Initializer)
        projection_list = pool.map(self._project, angles)
        return projection_list

    def create_gif(self, output) -> None:
        try:
            projection_list = self._create_projection_list()
            imageio.mimwrite(output, projection_list, format='.gif', duration=self.delay)
        except Exception as e:
            print(e)
            raise e

