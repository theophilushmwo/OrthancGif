import numpy as np
import imageio

class MosaicGenerator:
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
        image = scale(image, self.finalWidth, self.finalHeight)
        imageio.imwrite(output, image, format='.png')