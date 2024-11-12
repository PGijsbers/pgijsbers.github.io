import random
from dataclasses import dataclass
from typing import Tuple, Self, Iterable

NOT_SET = 0

def fill(area: int, color: int, canvas: dict[Tuple[int, int], int]) -> dict[Tuple[int, int], int]:
    # An *incredibly stupid* algorithm for filling big squares (not even the biggest!) - but prototype
    empty = [k for k, v in canvas.items() if v == NOT_SET]
    x, y = random.choice(empty)
    width, height = 1, 1

    # Very unoptimized, because it rechecks the square every time instead of only checking the boundary
    while width * height < area:
        if bottom_right := all((x1, y1) in empty for x1 in range(x, x+width+1) for y1 in range(y, y+height+1)):
            width, height = width + 1, height+1
            continue

        if bottom_left := all((x1, y1) in empty for x1 in range(x-1, x+width) for y1 in range(y, y+height+1)):
            width, height = width + 1, height+1
            x = x - 1
            continue

        if top_left := all((x1, y1) in empty for x1 in range(x-1, x+width) for y1 in range(y-1, y+height)):
            width, height = width + 1, height + 1
            x, y = x - 1, y - 1
            continue

        if top_right := all((x1, y1) in empty for x1 in range(x, x+width+1) for y1 in range(y-1, y+height)):
            width, height = width + 1, height + 1
            y = y - 1
            continue
        break

    while width * height < area:
        if area - ((width + 1) * height) >= 0:
            if expand_right := all((x + width, y1) in empty for y1 in range(y, y+height+1)):
                width = width + 1
                continue
            if expand_left := all((x - 1, y1) in empty for y1 in range(y, y+height+1)):
                width = width + 1
                x = x - 1
                continue
        if area - (width * (height + 1)) >= 0:
            if expand_top := all((x1, y - 1) in empty for x1 in range(x, x+width+1)):
                height = height + 1
                y = y - 1
                continue
            if expand_bottom := all((x1, y + height) in empty for x1 in range(x, x+width+1)):
                height = height + 1
                continue
        break

    area = area - width * height
    for x1 in range(x, x+width):
        for y1 in range(y, y+height):
            canvas[(x1, y1)] = color

    if area > 0:
        fill(area, color, canvas)
    return canvas


def display_canvas(canvas: dict[Tuple[int, int], int]) -> None:
    width = max(x for x, y in canvas) + 1
    height = max(y for x, y in canvas) + 1
    markers = {0: '.', 1: '@', 2:'#', 3: '&'}
    for y in range(height):
        chars = ''.join(map(markers.get, [canvas[(x, y)] for x in range(width)]))
        print(chars)






def generate(*planes, width=10, height=10):
    # Unit of a size is number of squares, where a square is the smallest unit
    planes = sorted(planes)
    for plane in planes:
        width, height = pick_dimensions(plane.area)

def pick_dimensions(area: int) -> Tuple[int, int]:
    divisors = [w for w in range(1, area + 1) if area % w == 0]
    width = random.choice(divisors)
    return width, area / width

def split(size):
    if size == 1 or random.random() < 0.5:
        return [size]
    # should also only return non-prime numbers, since they need to be turned to squares
    remainder = random.randint(1, size)
    size = size - remainder
    return [size] + split(remainder)


if __name__ == '__main__':
    canvas = {(0,0): NOT_SET}
    fill(1, 1, canvas)

    canvas = {(x, y): NOT_SET for x in range(3) for y in range(3)}
    fill(4, 1, canvas)
    fill(5, 2, canvas)

    # I think I still noticed two mistakes:
    #  - one time the horizontal expansion didnt trigger completely
    #  - one time it filled more than `area` -- but in two places.. with possibly recursive call