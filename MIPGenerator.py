import numpy as np 
import scipy.ndimage
import os 
import imageio.v2 as imageio
import requests
import io
import orthanc

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
        f = open('/python/mip.txt', 'a')
        for i in angles:
            MIP = self._project(i)
            MIP = self.flip_MIP(MIP)
            projection_list.append(MIP)
            f.write(f'{i} degrees\n')
            print(f'{i} degrees')
        f.close()
        return projection_list

    def create_gif(self, filename:str, directory:str, frames:int=60, delay:float=10):
        delay = delay/1000
        filepath = os.path.join(directory, filename + '.gif')
        projection_list = self._create_projection_list(frames)
        imageio.mimsave(filepath, projection_list, duration=delay)

    def flip_MIP(self, MIP:np.ndarray):
        MIP = np.flip(MIP, axis=0)
        return MIP

def get_nparray(series:str):
    x = requests.get(f'https://demo.orthanc-server.com/series/{series}/numpy?=rescale=true')
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
        x = requests.get('https://demo.orthanc-server.com/series/318603c5-03e8cffc-a82b6ee1-3ccd3c1e-18d7e3bb/numpy?=rescale=true')
        c = np.load(io.BytesIO(x.content), allow_pickle=True)
        test = MIPGenerator(c)
        test.create_gif('test', '/python', 100, 50)
        image = imageio.imread(f'/python/test.gif')
        output.AnswerBuffer(image, 'text/plain')
    else:
        output.SendMethodNotAllowed('GET')

orthanc.RegisterRestCallback('/series/privateTest/help', displayGif)