import numpy as np
import scipy.ndimage
import imageio
import requests
import io
import orthanc


class MIPGenerator:
    def __init__(self, numpy_array: np.ndarray):
        self.numpy_array = numpy_array
        if len(self.numpy_array.shape) != 4:
            raise Exception('numpy_array must be 3D')

    def _project(self, angle: int) -> np.ndarray:
        vol_angle = scipy.ndimage.rotate(
            self.numpy_array, angle=angle, reshape=False, axes=(1, 2))
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
        imageio.mimwrite(output, projection_list, format='.gif', duration=delay)

    def flip_MIP(self, MIP: np.ndarray):
        MIP = np.flip(MIP, axis=0)
        return MIP


def get_nparray(series: str):
    x = requests.get(
        f'https://demo.orthanc-server.com/series/{series}/numpy?rescale=true')
    c = np.load(io.BytesIO(x.content), allow_pickle=True)
    return c

def get_param(param, default, **request):
    try:
        return int(request['get'][param])
    except:
        return default

def displayGif(output, uri, **request):
    if request['method'] == 'GET':
        frames = get_param('frames', 60, **request)
        delay = get_param('delay', 10, **request)
        print(f'frames: {frames}, delay: {delay}')
        series = uri.split('/')[2]
        try:
            np_array = get_nparray(series)
        except:
            output.AnswerBuffer('Did not find any series', 'text/plain')
            return
        test = MIPGenerator(np_array)
        memory_output = io.BytesIO()
        test.create_gif(memory_output, frames, delay)
        memory_output.seek(0)
        output.AnswerBuffer(memory_output.read(), 'image/gif')
    else:
        output.SendMethodNotAllowed('GET')


orthanc.RegisterRestCallback('/series/(.*)/mip', displayGif)
