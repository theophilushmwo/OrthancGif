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

def outputMip(output, uri, **request):
    displayGif(output, uri, 360, **request)

def outputAvip(output, uri, **request):
    displayGif(output, uri, 180, **request)

def outputMinip(output, uri, **request):
    displayGif(output, uri, 60, **request)

def displayGif(output, uri, projection, **request):
    if request['method'] == 'GET':
        frames = get_param('frames', 60, **request)
        delay = get_param('delay', 10, **request)
        series = uri.split('/')[2]
        try:
            np_array = get_nparray(series)
        except:
            output.AnswerBuffer('Invalid series ID', 'text/plain')
            return
        try:
            gifBuffer = MIPGenerator(np_array, frames, delay, projection)
            memory_output = io.BytesIO()
            gifBuffer.create_gif(memory_output)
            memory_output.seek(0)
            output.AnswerBuffer(memory_output.read(), 'image/gif')
        except:
            output.AnswerBuffer('Images are not 3D', 'text/plain')
    else:
        output.SendMethodNotAllowed('GET')


orthanc.RegisterRestCallback('/series/(.*)/mip', outputMip)
orthanc.RegisterRestCallback('/series/(.*)/avip', outputAvip)
orthanc.RegisterRestCallback('/series/(.*)/minip', outputMinip)

