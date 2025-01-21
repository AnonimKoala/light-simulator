def calc_brush_alpha(opacity: float) -> int:
    """
    Calculate alpha value for brush color
    :param opacity: value between 0 and 1
    :return: alpha value between 0 and 255
    """
    if opacity > 1 or opacity < 0:
        raise ValueError("Opacity must be between 0 and 1")
    return int(opacity * 255)


def calc_opacity(alpha: int) -> float:
    """
    Calculate opacity value for brush alpha
    :param alpha: value between 0 and 255
    :return: opacity value between 0 and 1
    """
    return alpha / 255


def convert_qt_angle2cartesian(qt_angle: float) -> float:
    """
    Convert a Qt angle to a Cartesian angle.

    :param qt_angle: angle in Qt coordinate system
    :return: angle in Cartesian coordinate system (negative qt angle)
    """
    return -qt_angle

