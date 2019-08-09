from models.asymmetry import VisualizedLeftRightAsymmetry


class AsymmetryProcessor(object):
    def __init__(self):
        self.min_left_degrees = 46.67
        self.min_right_degrees = 41.63

    def get_left_right_degrees(self, left_apt, right_apt):

        degrees_left = self.min_left_degrees
        degrees_right = self.min_right_degrees

        if left_apt >= right_apt:
            degrees_left = (((left_apt/right_apt) - 1) * 41.21) + self.min_left_degrees
        else:
            degrees_right = (((right_apt/left_apt) - 1) * 32.08) + self.min_right_degrees

        return degrees_left, degrees_right

    def get_start_angle(self, degrees):

        start_angle = 103.3 - (degrees / 2)

        return start_angle

    def get_left_right_y_values(self, left_start_angle, left_degrees, right_start_angle, right_degrees):

        left_y = ((360 - left_start_angle) - left_degrees) / left_degrees

        right_y = ((1.5 * (360 - right_start_angle)) - (1.5 * right_degrees)) / right_degrees

        return left_y, right_y

    def get_visualized_left_right_asymmetry(self, left_apt, right_apt):

        left_degrees, right_degrees = self.get_left_right_degrees(left_apt, right_apt)

        left_start_angle = self.get_start_angle(left_degrees)

        right_start_angle = self.get_start_angle(right_degrees)

        left_y, right_y = self.get_left_right_y_values(left_start_angle, left_degrees, right_start_angle, right_degrees)

        asymmetry = VisualizedLeftRightAsymmetry(left_start_angle, right_start_angle, left_y, right_y)

        return asymmetry
