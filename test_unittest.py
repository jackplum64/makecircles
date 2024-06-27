from main import *
import unittest

class Test_TestRadiusGeneration(unittest.TestCase):
    # generate positive radius given valid mean and std_dev
    def test_generate_positive_radius(self):
        r_mean = 10
        r_std_dev = 2
        radius = generate_radius(r_mean, r_std_dev)
        assert radius > 0

    # handle very small mean and std_dev values with fixed assert statement
    def test_handle_small_mean_std_dev(self):
        r_mean = 0.1
        r_std_dev = 0.1
        radius = generate_radius(r_mean, r_std_dev)
        assert radius is None or radius > 0
    
    # Test handling very large standard deviation
    def test_handling_large_std_dev(self):
        r_mean = 10
        r_std_dev = 1000
        radius = generate_radius(r_mean, r_std_dev)
        assert radius is not None and radius > 0


class Test_TestMakeCircle(unittest.TestCase):
    # Generates a circle within the image boundaries
    def test_circle_within_boundaries(self):
        height, width = 100, 100
        r_mean, r_std_dev = 10, 2
        circle = make_circle(height, width, r_mean, r_std_dev)
        assert circle is not None
        x, y, radius = circle
        assert radius > 0
        assert radius <= min(height, width) // 2
        assert radius <= x <= width - radius
        assert radius <= y <= height - radius

    # Handles cases where radius generation fails after 1000 attempts
    def test_radius_generation_failure(self):
        height, width = 100, 100
        r_mean, r_std_dev = -10, 2  # Unlikely to generate a positive radius
        circle = make_circle(height, width, r_mean, r_std_dev)
        assert circle is None


class TestMakeCircleList(unittest.TestCase):

    # generates a list of non-overlapping circles of specified length
    def test_generates_non_overlapping_circles(self):
        height = 100
        width = 100
        r_mean = 10
        r_std_dev = 2
        n = 5
        circles = make_circle_list(height, width, r_mean, r_std_dev, n)
        self.assertEqual(len(circles), n)
        for i in range(len(circles)):
            for j in range(i + 1, len(circles)):
                self.assertFalse(does_overlap(circles[i], [circles[j]]))

    # handles case where n is zero
    def test_handles_zero_circles(self):
        height = 100
        width = 100
        r_mean = 10
        r_std_dev = 2
        n = 0
        circles = make_circle_list(height, width, r_mean, r_std_dev, n)
        self.assertEqual(len(circles), 0)

    # circles are within the image boundaries
    def test_circles_within_image_boundaries(self):
        height = 100
        width = 100
        r_mean = 10
        r_std_dev = 2
        n = 5
        circles = make_circle_list(height, width, r_mean, r_std_dev, n)
        self.assertEqual(len(circles), n)
        for circle in circles:
            x, y, radius = circle
            self.assertTrue(x - radius >= 0)
            self.assertTrue(y - radius >= 0)
            self.assertTrue(x + radius <= width)
            self.assertTrue(y + radius <= height)

    # validates the distribution of radii matches expected statistical properties
    def test_distribution_of_radii(self):
        height = 1000
        width = 1000
        r_mean = 10
        r_std_dev = 1
        n = 100
        circles = make_circle_list(height, width, r_mean, r_std_dev, n)
        radii = [circle[2] for circle in circles]
        mean_radius = np.mean(radii)
        std_dev_radius = np.std(radii)
        self.assertAlmostEqual(mean_radius, r_mean, delta=1)
        self.assertAlmostEqual(std_dev_radius, r_std_dev, delta=1)

    # checks that radii values are realistic and non-negative
    def test_radii_realistic_and_non_negative(self):
        height = 100
        width = 100
        r_mean = 10
        r_std_dev = 2
        n = 5
        circles = make_circle_list(height, width, r_mean, r_std_dev, n)
        for circle in circles:
            x, y, radius = circle
            self.assertGreaterEqual(radius, 0)
            self.assertLessEqual(radius, r_mean + 3*r_std_dev)

    # ensures no circles are None in the final list
    def test_no_none_circles_in_final_list(self):
        height = 100
        width = 100
        r_mean = 10
        r_std_dev = 2
        n = 5
        circles = make_circle_list(height, width, r_mean, r_std_dev, n)
        self.assertEqual(len(circles), n)
        for circle in circles:
            self.assertIsNotNone(circle)

    # handles case where r_mean or r_std_dev is zero
    def test_handles_zero_values(self):
        height = 100
        width = 100
        r_mean = 0
        r_std_dev = 0
        n = 5
        circles = make_circle_list(height, width, r_mean, r_std_dev, n)
        self.assertEqual(len(circles), n)
        for circle in circles:
            self.assertNotEqual(circle[2], 0)

    # handles case where height or width is too small to fit any circles
    def test_handles_small_height_or_width_fixed(self):
        height = 4
        width = 4
        r_mean = 5
        r_std_dev = 1
        n = 1
        circles = make_circle_list(height, width, r_mean, r_std_dev, n)
        self.assertIsNone(circles)

    # Test case where height or width is larger than mean, but with large std_dev
    def test_large_std_dev(self):
        height = 40
        width = 40
        r_mean = 10
        r_std_dev = 20
        n = 5
        circles = make_circle_list(height, width, r_mean, r_std_dev, n)
        self.assertIsNone(circles)