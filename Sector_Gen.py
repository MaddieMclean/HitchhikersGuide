from random import seed, randint

sector_width = 8
sector_depth = 10
seed()


def d6(num):
    n = 0
    for i in range(num - 1):
        n += randint(1, 6)
    return n


def build_system(density):
    world = d6(1) + density > 3
    system = {
        'world': world,
        'gas giant': d6(2) < 10,
    }
    if world:
        system['worldDetails'] = build_world()


def build_world():
    size = d6(2) - 2
    return {
        'starport': '',
        'size': size,
        'atmosphere': '',
        'hydrographic': '',
        'base': '',
        'travelZone': '',
        'polity': '',
    }
