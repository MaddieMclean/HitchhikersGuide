from random import seed, randint

sector_width = 8
sector_depth = 10


def d6(num):
    n = 0
    for _ in range(num):
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
    return system


def build_world():
    def get_temp():
        dm_table = {0: 0, 1: 0, 2: -2, 3: -2, 4: -1, 5: -1,
                    6: 0, 7: 0, 8: 1, 9: 1, 10: 2, 11: 6,
                    12: 6, 13: 2, 14: -1, 15: 2}
        return d6(2) + dm_table.get(atmosphere)

    def get_hydrographics():
        if size in (0, 1):
            return 0
        dm = -7
        if atmosphere in (0, 1, 10, 11, 12):
            dm += -4
        if atmosphere not in (13, 15):
            if temperature in (10, 11):
                dm += -2
            elif temperature > 11:
                dm += -6
        return d6(2) + dm

    size = d6(2) - 2
    atmosphere = to_zero(d6(2) - 7 + size)
    temperature = get_temp()
    hydrographics = to_zero(get_hydrographics())
    population = d6(2) - 2
    return {
        'starport': '',
        'size': size,
        'atmosphere': atmosphere,
        'hydrographic': hydrographics,
        'temperature': temperature,
        'base': '',
        'travelZone': '',
        'polity': '',
    }


def to_zero(n):
    return 0 if n < 0 else n


def main():
    for _ in range(10):
        seed()
        print(build_system(0))


if __name__ == '__main__':
    main()
