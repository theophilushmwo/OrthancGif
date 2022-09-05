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

class mozaicGenerator:
    def __init__(self, numpy_array: np.ndarray, cols: int, nb_images: int, finalWidth, finalHeight):
        self.numpy_array = numpy_array
        self.cols = cols
        self.nb_images = nb_images
        self.finalWidth = finalWidth
        self.finalHeight = finalHeight
        self.rows = int(self.nb_images / self.cols)

    def getImages(self):
        images = []
        row = []
        gap = int(len(self.numpy_array) / self.nb_images)
        for i in range(self.nb_images):
            row.append(self.numpy_array[i * gap])
            if (i + 1) % self.cols == 0:
                images.append(row)
                row = []
        return images
    
    def concatImages(self, images):
        imagesRow = []
        for i in range(self.rows):
            imagesRow.append(np.concatenate(images[i], axis=1))
        return np.concatenate(imagesRow, axis=0)

    def createImage(self, output):
        images = self.getImages()
        image = self.concatImages(images)
        print(self.finalHeight)
        print(self.finalWidth)
        image = scale(image, self.finalWidth, self.finalHeight)
        imageio.imwrite(output, image, format='.png')

def get_nparray(series: str):
    x = requests.get(
        f'https://localhost:8042/series/{series}/numpy?rescale=true')
    c = np.load(io.BytesIO(x.content), allow_pickle=True)
    return c

def get_param(param, default, **request):
    try:
        return int(request['get'][param])
    except:
        return default

def scale(image, nRows, nCols):
    nR0 = len(image)
    nC0 = len(image[0])
    return [[ image[int(nR0 * r / nRows)][int(nC0 * c / nCols)]  
            for c in range(nCols)] for r in range(nRows)]

def displayGif(output, uri, **request):
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
            gifBuffer = MIPGenerator(np_array, frames, delay, 360)
            memory_output = io.BytesIO()
            gifBuffer.create_gif(memory_output)
            memory_output.seek(0)
            output.AnswerBuffer(memory_output.read(), 'image/gif')
        except:
            output.AnswerBuffer('Images are not 3D', 'text/plain')
    else:
        output.SendMethodNotAllowed('GET')

def displayMozaic(output, uri, **request):
    if request['method'] == 'GET':
        cols = get_param('cols', 5, **request)
        nb_images = get_param('images', 20, **request)
        finalWidth = get_param('width', 512, **request)
        finalHeight = get_param('height', 512, **request)
        series = uri.split('/')[2]
        try:
            np_array = get_nparray(series)
        except:
            output.AnswerBuffer('Invalid series ID', 'text/plain')
            return
        try:
            mozaicBuffer = mozaicGenerator(np_array, cols, nb_images, finalWidth, finalHeight)
            memory_output = io.BytesIO()
            mozaicBuffer.createImage(memory_output)
            memory_output.seek(0)
            output.AnswerBuffer(memory_output.read(), 'image/png')
        except:
            output.AnswerBuffer('Internal server error', 'text/plain')
    else:
        output.SendMethodNotAllowed('GET')

orthanc.RegisterRestCallback('/series/(.*)/mozaic', displayMozaic)
orthanc.RegisterRestCallback('/series/(.*)/mip', displayGif)

