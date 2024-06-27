import numpy as np
import random
import cv2
import os


def make_circle_list(height, width, r_mean, r_std_dev, n):
    # Generate a list of non-overlapping circles
    # Return circles as list of tuples [(x, y, r), (x, y, r)]

    if not all(var > 0 for var in [height, width, r_mean, n]):
        print(f'ERROR: parameter invalid value')
        print(f'''circle_list cannot be generated with params height: 
              {height}, width: {width}, r_mean: {r_mean}, 
              r_std_dev: {r_std_dev}, n: {n}''')
        return None
    if not all((var > r_mean + r_std_dev*4) for var in [height, width]):
        print(f'ERROR: impossible packing')
        print(f'''circle_list cannot be generated with params height: 
              {height}, width: {width}, r_mean: {r_mean}, 
              r_std_dev: {r_std_dev}, n: {n}''')
        return None

    circle_list = []
    while len(circle_list) < n:
        new_circle = make_circle(height, width, r_mean, r_std_dev)

        if new_circle is None:
            continue
        if does_overlap(new_circle, circle_list) is True:
            continue

        circle_list.append(new_circle)

    return circle_list


def make_circle(height, width, r_mean, r_std_dev):
    # Generate circle that does not intersect image boundary
    # Return circle as tuple with position and radius
    radius = generate_radius(r_mean, r_std_dev)

    if radius is None:
        return None

    xlo = 0 + radius
    xhi = width - radius
    ylo = 0 + radius
    yhi = height - radius

    x = random.randint(xlo, xhi)
    y = random.randint(ylo, yhi)

    return x, y, radius


def does_overlap(new_circle, circle_list):
    # Takes circle as tuple and list of circle as list of tuples
    # Checks circle against list of circles for overlap
    # If overlap, return True.  Otherwise return False
    x_new, y_new, radius_new = new_circle
    new_point = np.array([x_new, y_new])
    for circle in circle_list:
        x, y, radius = circle
        min_distance = radius_new + radius
        point = np.array([x, y])

        euclidian_distance = np.linalg.norm(new_point - point)

        if euclidian_distance <= min_distance:
            return True
    return False


def generate_radius(r_mean, r_std_dev):
    # Generate nonnegative and nonzero radius
    # Generate as sample of a normal dist. given mean, std_dev
    # Return as integer; if count > 1000 return None
    count = 0
    radius = 0
    while radius <= 0:
        output = np.random.normal(r_mean, r_std_dev, 1)
        output_rounded = np.around(output, decimals=0)
        output_rounded_int = output_rounded.astype(int)
        radius = output_rounded_int[0]
        count += 1
        if count > 1000:
            return None

    return radius
    

def draw_circles(img, height, width, r_mean, r_std_dev, n, color, thickness=-1):
    # Draw a group of non-overlapping circles with statistical inputs
    # Defaul thickness of -1 results in filled-in circles
    circle_list = make_circle_list(height, width, r_mean, r_std_dev, n)

    if circle_list is None:
        return

    for circle in circle_list:
        x, y, radius = circle
        center = (x, y)
        cv2.circle(img, center, radius, color, thickness)


def create_background(height, width, color):
    # Create background image of specified size and color
    blank_image = np.ones((height, width, 3), np.uint8)
    blank_image[:] = color
    return blank_image


def save_image(img, name, directory):
    ksize = [9,9] # Gaussian blur kernal size
    img_blur = cv2.GaussianBlur(img, ksize, 0)

    name = name + '.png'
    name_blur = name + '_blur.png'

    os.chdir(directory)
    cv2.imwrite(name, img)
    cv2.imwrite(name_blur, img_blur)


def main():
    width = 1000
    height = 1000
    background_color = [0,0,0]

    img = create_background(height, width, background_color)

    # Generate AP particles
    r_mean = 35
    r_std_dev = 5
    n = 10
    color = [201, 27, 18] # [b, g, r]
    draw_circles(img, height, width, r_mean, r_std_dev, n, color)

    # Generate void particles
    r_mean = 15
    r_std_dev = 10
    n = 25
    color = [53, 26, 232] # [b, g, r]
    draw_circles(img, height, width, r_mean, r_std_dev, n, color)

    save_dir = './output'
    image_name = 'circles'

    save_image(img, image_name, save_dir)


if __name__ == "__main__":
    main()
