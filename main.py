import numpy as np
import random
import cv2
import os
import time
import math
from pathlib import Path
import concurrent.futures

def make_circle_list(height, width, r_mean, r_std_dev, n, exclude=[]):
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
        if len(exclude) > 0:
            if does_overlap_fully(new_circle, exclude) is True:
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
    # x, y, r = new_circle
    for circle in circle_list:
        min_distance = circle[2] + new_circle[2]

        if abs(circle[0] - new_circle[0]) > min_distance:
            continue
        if abs(circle[1] - new_circle[1]) > min_distance:
            continue

        if ((circle[0] - new_circle[0])**2 + (circle[1] - new_circle[1])**2) <= min_distance**2:
            return True
    return False


def does_overlap_fully(new_circle, exclude_list):
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
    

def draw_circles(img, circle_list, color, thickness=-1):
    # Draw each circle in a list of circles
    # Default thickness of -1 results in filled-in circles

    if circle_list is None:
        return

    for circle in circle_list:
        x, y, radius = circle
        center = (x, y)
        cv2.circle(img, center, radius, color, thickness)
    return img


def create_background(height, width, color):
    # Create background image of specified size and color
    if color == [0, 0, 0]:
        blank_image = np.zeros((height, width, 3), np.uint8)
    else:
        blank_image = np.ones((height, width, 3), np.uint8)
        blank_image[:] = color
    return blank_image


def save_image(image, file_name, dir_name):
    parent_directory = Path(__file__).parent
    target_directory = os.path.join(parent_directory, dir_name)
    os.makedirs(target_directory, exist_ok=True)

    ksize = [9,9] # Gaussian blur kernal size
    img_blur = cv2.GaussianBlur(image, ksize, 0)

    filepath = os.path.join(target_directory, file_name)
    cv2.imwrite(filepath, img_blur)

    return filepath, target_directory


def process_image(itr, width, height, background_color, background_img):
    r_mean_input = 72.8
    r_mean_target = 25 # Target mean for image rejection criteria
    r_mean_delta = 10 # Allowable difference for rejection criteria - large value allows all images to print
    r_std_dev_input = 37
    r_std_dev_target = 20 # Target std dev for image rejection criteria
    r_std_dev_delta = 5 # Allowable difference for rejection criteria - large value allows all images to print
    n = 200
    color = [255, 0, 0] # [b, g, r]
    AP_list = make_circle_list(height, width, r_mean_target, r_std_dev_target, n)
    AP_img = draw_circles(background_img.copy(), AP_list, color)

    # Analyze distributions
    AP_radii_list = [t[2] for t in AP_list]
    AP_radii_array = np.array(AP_radii_list)
    AP_mean = round(np.mean(AP_radii_array), 1)
    AP_std_dev = round(np.std(AP_radii_array), 1)

    if abs(AP_mean - r_mean_target) > r_mean_delta:
        print(f'Failure 1: AP Mean: {AP_mean}  Target Mean: {r_mean_target}')
        return None
    if abs(AP_std_dev - r_std_dev_target) > r_std_dev_delta:
        print(f'Failure 2: AP std dev: {AP_std_dev}  Target std dev: {r_std_dev_target}')
        return None

    # Generate void particles
    r_mean_input = 10
    r_mean_target = 10 # Target mean for image rejection criteria
    r_mean_delta = 2 # Allowable difference for rejection criteria
    r_std_dev_input = 6
    r_std_dev_target = 6 # Target std dev for image rejection criteria
    r_std_dev_delta = 2 # Allowable difference for rejection criteria
    n = 80
    color = [0, 0, 255] # [b, g, r]
    void_list = make_circle_list(height, width, r_mean_target, r_std_dev_target, n, exclude=AP_list)
    void_img = draw_circles(background_img.copy(), void_list, color)

    void_radii_list = [t[2] for t in void_list]
    void_radii_array = np.array(void_radii_list)
    void_mean = round(np.mean(void_radii_array),1)
    void_std_dev = round(np.std(void_radii_array), 1)

    if abs(void_mean - r_mean_target) > r_mean_delta:
        print(f'Failure 3: VOID Mean: {void_mean}  Target Mean: {r_mean_target}')
        return None
    if abs(void_std_dev - r_std_dev_target) > r_std_dev_delta:
        print(f'Failure 4: VOID std dev: {void_std_dev}  Target std dev: {r_std_dev_target}')
        return None

    # Combine imgs and save output
    
    image_name = (f'{(1+itr):03d}_APmean_{AP_mean}_APstd_{AP_std_dev}___VOIDmean_{void_mean}_VOIDstd_{void_std_dev}.png')
    save_dir = 'output'

    final_img = cv2.addWeighted(AP_img, 1, void_img, 1, 0)
    save_image(final_img, image_name, save_dir)


def main():
    start = time.perf_counter()
    width = 1000
    height = 1000
    background_color = [0,0,0]

    background_img = create_background(height, width, background_color)

    num_imgs = 100
    multi = True

    num_cpus = os.cpu_count()
    if multi == True:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = [executor.submit(process_image, itr, width, height, background_color, background_img) for itr in range(num_imgs)]
            concurrent.futures.wait(futures)
       

    else:
        for itr in range(num_imgs):
            process_image(itr, width, height, background_color, background_img)


    end = time.perf_counter()
    print(f'Total Time: {end - start}')


if __name__ == "__main__":
    main()
