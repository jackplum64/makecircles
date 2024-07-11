import numpy as np
from pathlib import Path
import os
import cv2
import math
import numba
from numba import int32, float32, types
from numba.experimental import jitclass


spec = [
    ('height', float32),
    ('width', float32),
    ('r_mean', float32),
    ('r_std_dev', float32),
    ('size', int32),
    ('circle_array', float32[:]),
    ('radius_array', float32[:]),
    ('circle_list', types.ListType(types.UniTuple(float32, 3))),
]


@jitclass(spec)
class CircleGroup:
    def __init__(self, boundaries, size, r_mean, r_std_dev):
        self.height, self.width = boundaries
        self.r_mean = r_mean
        self.r_std_dev = r_std_dev
        self.size = size


    def make_circle_array(self):
        exclude = None
        circle_array = np.zeros((self.size, 3), np.float32)
        itr = 0
        self.generate_radius_array()
        for radius in self.radius_array:
            new_circle = self.make_circle(radius)

            if self.does_overlap(new_circle) is True:
                continue
            if exclude is not None:
                if self.does_overlap_fully(new_circle, exclude) is True:
                    continue
            
            circle_array[itr][0] = new_circle[0]
            circle_array[itr][1] = new_circle[1]
            circle_array[itr][2] = new_circle[2]
            itr += 1
        return circle_array

    
    def make_circle(self, radius):
        radius = int(radius)
        xhi = int(self.width - radius)
        yhi = int(self.height - radius)

        x = np.random.randint(radius, xhi)
        y = np.random.randint(radius, yhi)
        return x, y, radius


    def init_circles(self):

        xhi_array =  self.width - self.radius_array
        yhi_array =  self.height - self.radius_array

        x_array = np.random.randint(self.radius_array, xhi_array, self.size)
        y_array = np.random.randint(self.radius_array, yhi_array, self.size)

    
    def generate_radius_array(self):
        self.radius_array = np.random.normal(self.r_mean, self.r_std_dev, self.size).astype(np.float32)
        self.radius_array = np.around(self.radius_array, decimals=0).astype(np.float32)
        self.radius_array[::-1].sort()
        # TODO: add rejection condition if total circle volume exceeds 90% image volume
        return self.radius_array

    
    def remove_initial_overlap(self, x_array, y_array):
        pass


    def does_overlap(self, new_circle):
        for circle in self.circle_list:
            min_distance = circle[2] + new_circle[2]

            if abs(circle[0] - new_circle[0]) > min_distance:
                continue
            if abs(circle[1] - new_circle[1]) > min_distance:
                continue

            if ((circle[0] - new_circle[0])**2 + (circle[1] - new_circle[1])**2) <= min_distance**2:
                return True
        return False


    def does_overlap_fully(self, new_circle, exclude_list):
        for circle in exclude_list:
            if abs(circle[0] - new_circle[0]) > abs(circle[2] - new_circle[2]):
                continue
            if abs(circle[1] - new_circle[1]) > abs(circle[2] - new_circle[2]):
                continue

            distance = math.sqrt((circle[0] - new_circle[0])**2 + (circle[1] - new_circle[1])**2)

            if circle[2] > (distance + new_circle[2]):
                return True
            
            if new_circle[2] > (distance + circle[2]):
                return True
        return False





class Canvas:
    def __init__(self, boundaries):
        self.height, self.width = boundaries
        self.draw_array = None
        self.draw_guide = []


    def create_background(self, color=None):
        if color is not None:
            self.color = np.array(color)
            self.background = np.ones((self.height, self.width, 3), np.uint8) * self.color
        else:
            self.background = np.zeros((self.height, self.width, 3), np.uint8)
        return self.background

    
    def create_image(self):
        pointer = 0
        images = []
        for count in self.draw_guide:
            image = self.background.copy()
            for row in range(pointer, pointer + count):
                self.draw_circle(image, (self.draw_array[row][0], self.draw_array[row][1]), self.draw_array[row][2], 
                                (self.draw_array[row][3], self.draw_array[row][4], self.draw_array[row][5])) # self, (x,y), r, (color))
                           
            images.append(image)
            pointer += count

        # TODO: improve this behavior to account for 1 or 3+ images
        final_img = cv2.addWeighted(images[0], 1, images[1], 1, 0)

        return final_img
            
    
    def draw_circle(self, image, center, r, color):
        cv2.circle(image, center, r, color, -1)
        return image
    


    def add_to_draw(self, circle_array, color):
        if self.draw_array == None:
            length, _ = np.shape(circle_array)
            color_array = np.tile(color, (length, 1))
            self.draw_array = np.append(circle_array, color_array, axis=1)
            self.draw_guide.append(length)
        else:
            length, _ = np.shape(circle_array)
            color_array = np.tile(color, (length, 1))
            array = np.append(circle_array, color_array, axis=1)
            self.draw_guide.append(length)
            self.draw_array = np.append(self.draw_array, new_array, axis=0)
        return self.draw_array


    def save_image(self, file_name, dir_name):
        parent_directory = Path(__file__).parent
        target_directory = os.path.join(parent_directory, dir_name)
        os.makedirs(target_directory, exist_ok=True)

        image = self.create_image()

        ksize = [9,9] # Gaussian blur kernal size
        img_blur = cv2.GaussianBlur(image, ksize, 0)

        filepath = os.path.join(target_directory, file_name)
        cv2.imwrite(filepath, img_blur)

        return filepath, target_directory


def main():
    AP = CircleGroup((1000,1000), 200, 70, 10)
    circle_array = AP.make_circle_array()

    pass


if __name__ == "__main__":
    main()