from logic.asymmetry_logic import AsymmetryProcessor


def test_equal_apt():

    proc = AsymmetryProcessor()
    viz = proc.get_visualized_left_right_asymmetry(5, 5)

    assert viz.left_start_angle == 79.97
    assert viz.left_y == 5.0
    assert viz.right_start_angle == 82.48
    assert viz.right_y == 8.5


def test_equal_zero():

    proc = AsymmetryProcessor()
    viz = proc.get_visualized_left_right_asymmetry(0, 0)

    assert viz.left_start_angle == 79.97
    assert viz.left_y == 5.0
    assert viz.right_start_angle == 82.48
    assert viz.right_y == 8.5


def test_left_2x_right():

    proc = AsymmetryProcessor()
    viz = proc.get_visualized_left_right_asymmetry(10, 5)

    assert viz.left_start_angle == 59.36
    assert viz.left_y == 2.42
    assert viz.right_start_angle == 82.48
    assert viz.right_y == 8.5


def test_left_2x_right_2():

    proc = AsymmetryProcessor()
    viz = proc.get_visualized_left_right_asymmetry(8, 4)

    assert viz.left_start_angle == 59.36
    assert viz.left_y == 2.42
    assert viz.right_start_angle == 82.48
    assert viz.right_y == 8.5


def test_right_2x_left():
    proc = AsymmetryProcessor()
    viz = proc.get_visualized_left_right_asymmetry(5, 10)

    assert viz.left_start_angle == 79.97
    assert viz.left_y == 5.0
    assert viz.right_start_angle == 63.98
    assert viz.right_y == 4.15


def test_right_2x_left_2():
    proc = AsymmetryProcessor()
    viz = proc.get_visualized_left_right_asymmetry(4, 8)

    assert viz.left_start_angle == 79.97
    assert viz.left_y == 5.0
    assert viz.right_start_angle == 63.98
    assert viz.right_y == 4.15

def test_left_1_5x_right():

    proc = AsymmetryProcessor()
    viz = proc.get_visualized_left_right_asymmetry(6, 4)

    assert viz.left_start_angle == 67.71
    assert viz.left_y == 3.11
    assert viz.right_start_angle == 82.48
    assert viz.right_y == 8.5


def test_right_1_5x_left():
    proc = AsymmetryProcessor()
    viz = proc.get_visualized_left_right_asymmetry(5, 7.5)

    assert viz.left_start_angle == 79.97
    assert viz.left_y == 5.0
    assert viz.right_start_angle == 71.48
    assert viz.right_y == 5.3



