"""This submodule contains the path_parse() function used to convert SVG path
element d-strings into svgpathtools Path objects.
Note: This file was taken (nearly) as is from the svg.path module (v 2.0)."""

# External dependencies
from __future__ import division, absolute_import, print_function
import numpy as np
import warnings

# Internal dependencies
from .path import Path


def parse_path(pathdef, current_pos=0j, tree_element=None):
    return Path(pathdef, current_pos=current_pos, tree_element=tree_element)


def _check_num_parsed_values(values, allowed):
    if not any(num == len(values) for num in allowed):
        if len(allowed) > 1:
            warnings.warn('Expected one of the following number of values {0}, but found {1} values instead: {2}'
                          .format(allowed, len(values), values))
        elif allowed[0] != 1:
            warnings.warn('Expected {0} values, found {1}: {2}'.format(allowed[0], len(values), values))
        else:
            warnings.warn('Expected 1 value, found {0}: {1}'.format(len(values), values))
        return False
    return True


def _parse_transform_substr(transform_substr):

    type_str, value_str = transform_substr.split('(')
    value_str = value_str.replace(',', ' ')
    values = list(map(float, filter(None, value_str.split(' '))))

    transform = np.identity(3)
    if 'matrix' in type_str:
        if not _check_num_parsed_values(values, [6]):
            return transform

        transform[0:2, 0:3] = np.array([values[0:6:2], values[1:6:2]])

    elif 'translate' in transform_substr:
        if not _check_num_parsed_values(values, [1, 2]):
            return transform

        transform[0, 2] = values[0]
        if len(values) > 1:
            transform[1, 2] = values[1]

    elif 'scale' in transform_substr:
        if not _check_num_parsed_values(values, [1, 2]):
            return transform

        x_scale = values[0]
        y_scale = values[1] if (len(values) > 1) else x_scale
        transform[0, 0] = x_scale
        transform[1, 1] = y_scale

    elif 'rotate' in transform_substr:
        if not _check_num_parsed_values(values, [1, 3]):
            return transform

        angle = values[0] * np.pi / 180.0
        if len(values) == 3:
            offset = values[1:3]
        else:
            offset = (0, 0)
        tf_offset = np.identity(3)
        tf_offset[0:2, 2:3] = np.array([[offset[0]], [offset[1]]])
        tf_rotate = np.identity(3)
        tf_rotate[0:2, 0:2] = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        tf_offset_neg = np.identity(3)
        tf_offset_neg[0:2, 2:3] = np.array([[-offset[0]], [-offset[1]]])

        transform = tf_offset.dot(tf_rotate).dot(tf_offset_neg)

    elif 'skewX' in transform_substr:
        if not _check_num_parsed_values(values, [1]):
            return transform

        transform[0, 1] = np.tan(values[0] * np.pi / 180.0)

    elif 'skewY' in transform_substr:
        if not _check_num_parsed_values(values, [1]):
            return transform

        transform[1, 0] = np.tan(values[0] * np.pi / 180.0)
    else:
        # Return an identity matrix if the type of transform is unknown, and warn the user
        warnings.warn('Unknown SVG transform type: {0}'.format(type_str))

    return transform


def parse_transform(transform_str):
    """Converts a valid SVG transformation string into a 3x3 matrix.
    If the string is empty or null, this returns a 3x3 identity matrix"""
    if not transform_str:
        return np.identity(3)
    elif not isinstance(transform_str, str):
        raise TypeError('Must provide a string to parse')

    total_transform = np.identity(3)
    transform_substrs = transform_str.split(')')[:-1]  # Skip the last element, because it should be empty
    for substr in transform_substrs:
        total_transform = total_transform.dot(_parse_transform_substr(substr))

    return total_transform
