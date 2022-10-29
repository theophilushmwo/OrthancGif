import logging
import numpy as np
import io
import os
import orthanc
from mosaic import MosaicGenerator
from mip import MIPGenerator

def handle_error(error, output):
    logging.critical(error)
    #Load unsuported.png image
    script_dir = os.path.dirname(__file__)
    file_path = os.path.join(script_dir, 'unsupported.png')
    with open(file_path, 'rb') as f:
        output.AnswerBuffer(f.read(), 'image/png')

def get_nparray(series: str):
    response = orthanc.RestApiGet( f'/series/{series}/numpy?rescale=true')
    c = np.load(io.BytesIO(response), allow_pickle=True)
    return c

def get_param(param, default, **request):
    try:
        return int(request['get'][param])
    except:
        return default

def displayGif(output, uri, **request):
    if request['method'] == 'GET':
        frames = get_param('frames', 30, **request)
        delay = get_param('delay', 50, **request)
        series = uri.split('/')[2]

        try:
            np_array = get_nparray(series)
            if(len(np_array.shape) != 4) :
                output.AnswerBuffer('Images are not 3D', 'text/plain')
                return
            gifBuffer = MIPGenerator(np_array, frames, delay, 360)
            memory_output = io.BytesIO()
            gifBuffer.create_gif(memory_output)
            memory_output.seek(0)
            output.AnswerBuffer(memory_output.read(), 'image/gif')
        except Exception as e:
            handle_error(e, output)
    else:
        output.SendMethodNotAllowed('GET')

def displayMosaic(output, uri, **request):
    if request['method'] == 'GET':
        cols = get_param('cols', 5, **request)
        nb_images = get_param('images', 20, **request)
        finalWidth = get_param('width', 512, **request)
        finalHeight = get_param('height', 512, **request)
        series = uri.split('/')[2]
        try:
            np_array = get_nparray(series)
            mosaicBuffer = MosaicGenerator(np_array, cols, nb_images, finalWidth, finalHeight)
            memory_output = io.BytesIO()
            mosaicBuffer.createImage(memory_output)
            memory_output.seek(0)
            output.AnswerBuffer(memory_output.read(), 'image/png')
        except Exception as e:
            handle_error(e, output)
    else:
        output.SendMethodNotAllowed('GET')

orthanc.RegisterRestCallback('/series/(.*)/mosaic', displayMosaic)
orthanc.RegisterRestCallback('/series/(.*)/mip', displayGif)