import numpy as np
import imageio
from multiprocessing import Pool, cpu_count
import SimpleITK as sitk
from functools import partial

class MIPGenerator:
    def __init__(self, image: sitk.Image, delay: float = 0.1, frames: int = 16):
        self.image = image
        self.projections = []
        self.delay = delay / 1000
        self.frames = frames

    def _create_projection_list(self):
        nbCores = cpu_count() - 2
        imageMin = int(np.amin(sitk.GetArrayFromImage(self.image)))
        projection = {'sum': sitk.SumProjection,
              'mean':  sitk.MeanProjection,
              'std': sitk.StandardDeviationProjection,
              'min': sitk.MinimumProjection,
              'max': sitk.MaximumProjection}
        ptype = 'mean'
        paxis = 0

        rotation_axis = [0,0,1]
        rotation_angles = np.linspace(0.0, 2*np.pi, self.frames)
        rotation_center = self.image.TransformContinuousIndexToPhysicalPoint([(index-1)/2.0 for index in self.image.GetSize()])
        rotation_transform = sitk.VersorRigid3DTransform()
        rotation_transform.SetCenter(rotation_center)

        image_indexes = list(zip([0,0,0], [sz-1 for sz in self.image.GetSize()]))
        image_bounds = []
        for i in image_indexes[0]:
            for j in image_indexes[1]:
                for k in image_indexes[2]:
                    image_bounds.append(self.image.TransformIndexToPhysicalPoint([i,j,k]))

        all_points = []
        for angle in rotation_angles:
            rotation_transform.SetRotation(rotation_axis, angle)    
            for pnt in image_bounds:
                all_points.append(rotation_transform.TransformPoint(pnt))
        all_points = np.array(all_points)
        min_bounds = all_points.min(0)
        max_bounds = all_points.max(0)
        new_spc = [np.min(self.image.GetSpacing())] * 3
        new_sz = [int(sz/spc + 0.5) for spc,sz in zip(new_spc, max_bounds-min_bounds)]
        with Pool(nbCores) as p:
            self.projections = p.map(partial(self._create_projection, rotation_transform=rotation_transform,
                new_sz=new_sz, min_bounds=min_bounds, new_spc=new_spc, imageMin=imageMin,
                paxis=paxis, ptype=ptype, projection=projection, rotation_axis=rotation_axis), rotation_angles)

    def _create_projection(self, angle, rotation_transform,
        new_sz, min_bounds, new_spc, imageMin,
        paxis, ptype, projection, rotation_axis):
        rotation_transform.SetRotation(rotation_axis, angle) 
        resampled_image = sitk.Resample(image1=self.image,
                                        size=new_sz,
                                        transform=rotation_transform,
                                        interpolator=sitk.sitkLinear,
                                        outputOrigin=min_bounds,
                                        outputSpacing=new_spc,
                                        outputDirection = [1,0,0,0,1,0,0,0,1],
                                        defaultPixelValue = imageMin, #HU unit for air in CT, possibly set to 0 in other cases
                                        outputPixelType = self.image.GetPixelID())
        proj_image = projection[ptype](resampled_image, paxis)
        extract_size = list(proj_image.GetSize())
        extract_size[paxis]=0
        npArray = np.flip(sitk.GetArrayFromImage(sitk.Extract(proj_image, extract_size)), axis=0)
        return npArray

    def createGif(self, output):
        self._create_projection_list()
        imageio.mimwrite(output, self.projections, format='.gif', duration=self.delay)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Create a MIP gif from a 3D image')
    parser.add_argument('image', help='3D image')
    parser.add_argument('output', help='output file')
    parser.add_argument('--delay', type=float, default=0.1, help='delay between frames in ms')
    parser.add_argument('--frames', type=int, default=30, help='number of frames')
    args = parser.parse_args()
    mip = MIPGenerator(sitk.ReadImage(args.image), args.delay, args.frames)
    mip.createGif(args.output)