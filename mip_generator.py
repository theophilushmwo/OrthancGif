import numpy as np
import scipy.ndimage
import os
import imageio.v2 as imageio
import requests
import io
import orthanc


class MIPGenerator:
    def __init__(self, numpy_array: np.ndarray):
        self.numpy_array = numpy_array
        if len(self.numpy_array.shape) != 4:
            raise Exception('numpy_array must be 3D')

    def _project(self, angle: int) -> np.ndarray:
        vol_angle = scipy.ndimage.interpolation.rotate(
            self.numpy_array, angle=angle, reshape=False, axes=(1, 2), output=np.uint8)
        MIP = np.amax(vol_angle, axis=1)
        return MIP

    def _create_projection_list(self, frames: int = 60) -> list:
        angles = np.linspace(0, 360, frames)
        projection_list = []
        for i in angles:
            MIP = self._project(i)
            MIP = self.flip_MIP(MIP)
            projection_list.append(MIP)
        return projection_list

    def create_gif(self, output, frames: int = 60, delay: float = 10) -> None:
        delay = delay/1000
        projection_list = self._create_projection_list(frames)
        imageio.mimwrite(output, projection_list, format= '.gif', duration=delay)

    def flip_MIP(self, MIP: np.ndarray):
        MIP = np.flip(MIP, axis=0)
        return MIP


def get_nparray(series: str):
    x = requests.get(
        f'https://demo.orthanc-server.com/series/{series}/numpy?rescale=true')
    c = np.load(io.BytesIO(x.content), allow_pickle=True)
    return c


def displayGif(output, uri, **request):
    if request['method'] == 'GET':
        """
        series = uri.split('/')[1]
        nparray = get_nparray(series)
        test = MIPGenerator(nparray)
        test.create_gif('test', '/gifs', 100, 50)
        image = imageio.imread(f'/gifs/test.gif')
        output.AnswerBuffer(image, 'text/plain')
        """

        numpy = get_nparray('318603c5-03e8cffc-a82b6ee1-3ccd3c1e-18d7e3bb')
        test = MIPGenerator(numpy)
        memory_output = io.BytesIO()
        test.create_gif(memory_output, 100, 50)
        memory_output.seek(0)
        output.AnswerBuffer(memory_output.read(), 'image/gif')
    else:
        output.SendMethodNotAllowed('GET')


orthanc.RegisterRestCallback('/series/privateTest/help', displayGif)
