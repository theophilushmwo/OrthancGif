import numpy as np
import scipy.ndimage
import imageio
from multiprocessing import Pool, cpu_count
from functools import partial

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
        pool = Pool(nbCores)
        projection_list = pool.map(self._project, angles)
        return projection_list

    def create_gif(self, output) -> None:
        projection_list = self._create_projection_list()
        imageio.mimwrite(output, projection_list, format='.gif', duration=self.delay)

if __name__ == '__main__':
    import requests
    import io
    import time
    url = 'https://demo.orthanc-server.com/series/1de00990-03680ef4-0be6bd5b-73a7d350-fb46abfa/numpy?rescale=true'
    timer = time.time()
    response = requests.get(url)
    print(f'Orthanc request took {time.time() - timer} seconds')
    content = io.BytesIO(response.content)
    numpy_array = np.load(content, allow_pickle=True)
    generator = MIPGenerator(numpy_array, 30, 100, 360)
    timer = time.time()
    generator.create_gif('test.gif')
    print(f'GIF creation took {time.time() - timer} seconds')

