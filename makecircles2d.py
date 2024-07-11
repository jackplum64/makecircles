import numpy as np




class CircleGroup:
    def __init__(self, boundaries, size, r_mean, r_std_dev):
        self.height, self.width = boundaries
        self.r_mean = r_mean
        self.r_std_dev = r_std_dev
        self.size = size


    def make_circle_array(self):

        pass


    def init_circles(self):

        xhi_array =  self.radius_array - self.width
        yhi_array =  self.radius_array - self.height

        x_array = np.random.randint(self.radius_array, xhi_array, self.size, dtype=int32)
        y_array = np.random.randint(self.radius_array, yhi_array, self.size, dtype=int32)

    
    def generate_radius_array(self):
        self.radius_array = np.random.normal(self.r_mean, self.r_std_dev, self.size)
        self.radius_array = np.around(self.radius_array, decimals=0).astype(np.int32)
        self.radius_array.sort()
        # TODO: add rejection condition if total circle volume exceeds 90% image volume
        return self.radius_array

    
    def remove_initial_overlap(self, x_array, y_array):

        

        radius_sq_array = np.square(self.radius_array)

        pass


    def does_overlap(self, new_circle):
        pass


    def does_overlap_fully(self, new_circle):
        pass





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
                draw_circle(image, (self.draw_array[row][0], self.draw_array[row][1]), self.draw_array[row][2], 
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
    pass


if __name__ == "__main__":
    main()