import numpy as np
import cv2
import random
from numba import njit
from mayavi import mlab


class SphereGroup:
    def __init__(self, r_mean, r_std_dev, color):
        self.r_mean = r_mean
        self.r_std_dev = r_std_dev
        self.color = color
        self.sphere_list = []


    def make_sphere_list(self, boundaries, count):
        self.boundaries = boundaries
        self.count = count

        radius_list = self.generate_radius_list()
        itr = 0

        while len(self.sphere_list) < self.count:
            radius = radius_list[itr]
            new_sphere = self.make_sphere(radius)

            if new_sphere is None:
                continue
            if self.does_overlap(new_sphere) is True:
                continue

            self.sphere_list.append(new_sphere)
            itr += 1
            print(itr)

        return self.sphere_list
        

    def make_sphere(self, radius):
        xlo = 0 + radius
        xhi = self.boundaries[0] - radius
        ylo = 0 + radius
        yhi = self.boundaries[1] - radius
        zlo = 0 + radius
        zhi = self.boundaries[2] - radius

        x = random.randint(xlo, xhi)
        y = random.randint(ylo, yhi)
        z = random.randint(zlo, zhi)

        return (x, y, z, radius)


    def generate_radius_list(self):
        tries = 0
        radius_list = [0]
        while any(radius <= 0 for radius in radius_list):
            if tries > 1000:
                return None
            radius_list = np.random.normal(self.r_mean, self.r_std_dev, self.count)
            radius_list = np.around(radius_list, decimals=0).astype(int)
            tries += 1
        return radius_list


    def does_overlap(self, new_sphere):
        for sphere in self.sphere_list:
            min_distance = new_sphere[3] + sphere[3]

            if abs(sphere[0] - new_sphere[0]) > min_distance:
                continue
            
            if abs(sphere[1] - new_sphere[1]) > min_distance:
                continue
            
            if abs(sphere[2] - new_sphere[2]) > min_distance:
                continue

            euclidian_distance = np.linalg.norm(np.array(new_sphere[:3]) - np.array(sphere[:3]))

            if euclidian_distance <= min_distance:
                return True
        return False


    def does_overlap_elementwise(self, new_sphere):
        # Currently broken
        deltas = points - p.reshape(1, -1)
        dists = np.sqrt((deltas**2).sum(axis=1))
        return (dists < radii + r).any()
    
    

def draw_spheres(self, img):
    pass


def create_img():
    pass




def main():
    boundaries = (1000, 1000, 1000)

    AP = SphereGroup(25, 5, [201, 27, 18])
    AP_sphere_list = AP.make_sphere_list(boundaries, 2000)
    AP_points = np.array([s[:3] for s in AP_sphere_list])
    AP_radii = np.array([s[3] for s in AP_sphere_list])

    print(AP_radii)
    
    void = SphereGroup(15, 2, [53, 26, 232])
    void_sphere_list = void.make_sphere_list(boundaries, 6000)
    void_points = np.array([s[:3] for s in void_sphere_list])
    void_radii = np.array([s[3] for s in void_sphere_list])

    
    mlab.figure(bgcolor=(1, 1, 1))
    mlab.points3d(AP_points[:, 0], AP_points[:, 1], AP_points[:, 2], AP_radii,
                  color=tuple(np.array(AP.color) / 255.0), scale_factor=1, resolution=20, opacity=0.6)
    mlab.points3d(void_points[:, 0], void_points[:, 1], void_points[:, 2], void_radii,
                  color=tuple(np.array(void.color) / 255.0), scale_factor=1, resolution=20, opacity=0.6)
    mlab.show()



if __name__ == "__main__":
    main()