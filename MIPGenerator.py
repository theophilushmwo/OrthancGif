import matplotlib.pyplot as plt
import numpy as np 
import scipy.ndimage
from PIL import Image
import os 
from fpdf import FPDF
import imageio.v2 as imageio
import requests
import io

class MIPGenerator:
    def __init__(self, numpy_array:np.ndarray):
        self.numpy_array = numpy_array

    def project(self, angle:int) -> np.ndarray:
        if len(self.numpy_array.shape) == 4 : 
            array = np.amax(self.numpy_array, axis = -1)
        else : 
            array = self.numpy_array
        axis = 1
        vol_angle = scipy.ndimage.interpolation.rotate(array , angle=angle , reshape=False, axes = (1,2))
        MIP = np.amax(vol_angle, axis=axis)
        self.MIP = MIP
        return MIP

    def create_projection_list(self, frames:int=60) -> list:
        angles = np.linspace(0, 360, frames)
        projection_list = []
        for i in angles:
            self.project(i)
            self.flip_MIP()
            projection_list.append(self.MIP)
            print(i)
        return projection_list

    def create_gif(self, filename:str, directory:str, frames:int=60, delay:float=10):
        delay = delay/1000
        filepath = os.path.join(directory, filename + '.gif')
        projection_list = self.create_projection_list(frames)
        imageio.mimsave(filepath, projection_list, duration=delay)

    def flip_MIP(self):
        self.MIP = np.flip(self.MIP, axis=0)
        return self.MIP

        
x = requests.get('https://demo.orthanc-server.com/series/318603c5-03e8cffc-a82b6ee1-3ccd3c1e-18d7e3bb/numpy?=rescale=true')

c = np.load(io.BytesIO(x.content), allow_pickle=True)

test = MIPGenerator(c)

test.create_gif('test', '/Users/theophilushomawoo/Documents/stage/galeo/python/', 100, 50)


