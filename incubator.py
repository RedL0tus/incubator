#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from solid import OpenSCADObject, cube, translate, sphere, minkowski, import_scad, cylinder, rotate, scad_render_to_file

from typing import Dict, List, Union


FILLET_RADIUS: int = 3
BOTTOM_THICKNESS: float = 0.8


def box(width: int, depth: int, height: int, thickness: int, radius: int) -> OpenSCADObject:
    fillet = sphere(radius)
    inner_diff = 2 * thickness + 2 * radius
    inner_width = max(width - inner_diff, 0)
    inner_depth = max(depth - inner_diff, 0)
    inner_height = max(height - BOTTOM_THICKNESS, 0)
    inner_space_cube = cube([inner_width, inner_depth, inner_height + radius])
    inner_space_offset = [thickness + radius, thickness + radius, BOTTOM_THICKNESS + radius]
    inner_space = translate(inner_space_offset) (minkowski() (inner_space_cube, fillet))

    outer_diff = 2 * radius
    outer_cube = cube([width - outer_diff, depth - outer_diff, height])
    outer = translate([radius, radius, radius]) (minkowski() (outer_cube, fillet))
    return outer - inner_space


def incubator(width: int, depth: int, height: int, thickness: int, hole_distance: int, hole_diameter: float) -> OpenSCADObject:
    ret = box(width, depth, height, thickness, FILLET_RADIUS)
    inner_diff = thickness + 2 * FILLET_RADIUS
    hole_radius = hole_diameter / 2
    print('>>> Padding: {inner_diff}'.format(inner_diff=inner_diff))
    print('>>> Hole: radius={radius}, diameter={diameter}'.format(radius=hole_radius, diameter=hole_diameter))

    distance = hole_diameter + hole_distance

    inner_width = width - 2 * inner_diff
    width_count = int((inner_width - hole_diameter) // distance) + 1
    width_padding = (inner_width - (width_count * distance - hole_distance)) / 2
    width_start = float(inner_diff) + width_padding
    print('>>> Width: {width}, inner: {inner_width}, start: {width_start}, padding: {width_padding}'.format(
        width=width, inner_width=inner_width, width_start=width_start, width_padding=width_padding))

    inner_depth = depth - 2 * inner_diff
    depth_count = int((inner_depth - hole_diameter) // distance) + 1
    depth_padding = (inner_depth - (depth_count * distance - hole_distance)) / 2
    depth_start = float(inner_diff) + depth_padding
    print('>>> Depth: {depth}, inner: {inner_depth}, start: {depth_start}, padding: {depth_padding}'.format(
        depth=depth, inner_depth=inner_depth, depth_start=depth_start, depth_padding=depth_padding))

    inner_height = height - inner_diff
    height_padding = inner_diff
    height_count = int(inner_height * 0.5 // distance)
    height_start = inner_diff

    print('>>> Hole pattern: {width}x{depth}x{height}'.format(width=width_count, depth=depth_count, height=height_count))

    pole_width = (rotate([0, 90, 0]) (cylinder(hole_radius, width)))
    pole_width = translate([0, depth_start + hole_radius, height_start + hole_radius]) (pole_width)
    pole_depth = (rotate([-90, 90, 0]) (cylinder(hole_radius, depth)))
    pole_depth = translate([width_start + hole_radius, 0, height_start + hole_radius]) (pole_depth)

    mesh = pole_depth + pole_width
    for i in range(0, width_count):
        mesh += translate([i * distance, 0, 0]) (pole_depth)
    for i in range(0, depth_count):
        mesh += translate([0, i * distance, 0]) (pole_width)
    for i in range(0, height_count):
        ret -= translate([0, 0, i * distance]) (mesh)
    return ret


if __name__ == '__main__':
    import sys
    import pathlib
    import argparse

    import trafaret as T

    from trafaret_config import commandline

    from pprint import pprint
    from pathlib import Path

    trafaret = T.Dict({
        T.Key('width', default=175): T.Int(),
        T.Key('depth', default=115): T.Int(),
        T.Key('height', default=75): T.Int(),
        T.Key('thickness', default=8): T.Int(),
        T.Key('hole_distance', default=5): T.Int(),
        T.Key('hole_diameter', default=0.5): T.Float(),
    })

    base_dir = Path(__file__).parent
    default_config = base_dir / 'config' / 'standard.yaml'

    ap = argparse.ArgumentParser(description='Generate OpenSCAD models of fish-hatching boxes')
    commandline.standard_argparse_options(ap, default_config=default_config)
    ap.add_argument('-o', '--out', type=str, help='Output file name', required=True)
    options,unknown = ap.parse_known_args(sys.argv)
    pprint(options)

    dimension = commandline.config_from_options(options, trafaret)
    print('>>> Generating: {width}x{depth}x{height}-{thickness}-{hole_distance}-{hole_diameter}'.format(**dimension))
    model = incubator(**dimension)
    scad_render_to_file(model, str(options.out))
