import json
from random import seed, randint

sector_width = 8
sector_depth = 10


def d6(num):
    n = 0
    for _ in range(num):
        n += randint(1, 6)
    return n


def to_range(n, maximum, minimum=0):
    n = minimum if n < minimum else n
    n = maximum if n > maximum else n
    return n


def dict_val(dict_obj, key, default=None):
    return dict_obj.get(key, default)


def dict_map(dict_obj, value):
    for key in dict_obj.keys():
        if value in dict_obj.get(key):
            return key
    return 0


def build_system(density):
    world = d6(1) + density > 3
    system = {
        'name': '',
        'gas giant': d6(2) < 10
    }
    if world:
        system['worldDetails'] = build_world()
    return system


def build_world():
    planet = build_planet()
    civ = build_civilisation()
    tech_level = get_tech_level(planet, civ)
    travel_zone = get_travel_zone(planet, civ)
    trade_code = get_trade_code(planet, civ, tech_level)
    return {
        'name': '',
        'polity': '',
        'description': '',
        'tradeCode': trade_code,
        'travelZone': travel_zone,
        'techLevel': tech_level,
        'planet': planet,
        'civilisation': civ
    }


def build_planet():
    def get_temp():
        dm_table = {1: (8, 9), 2: (10, 13, 15), 6: (11, 12), -1: (4, 5, 14),
                    -2: (2, 3)}
        temp = to_range(d6(2) + dict_map(dm_table, atmosphere), 12, 2)
        temp_table = {'frozen': [2], 'cold': (3, 4),
                      'temperate': (5, 6, 7, 8, 9),
                      'hot': (10, 11), 'boiling': [12]}
        return dict_map(temp_table, temp)

    def get_hydrographics():
        if size in (0, 1):
            return 0
        dm = -7
        if atmosphere in (0, 1, 10, 11, 12):
            dm += -4
        if atmosphere not in (13, 15):
            if 'hot' in temperature:
                dm += -2
            elif 'boiling' in temperature:
                dm += -6
        return to_range(d6(2) + dm + size, 10)

    size = d6(2) - 2
    atmosphere = to_range(d6(2) - 7 + size, 15)
    temperature = get_temp()
    hydrographics = get_hydrographics()
    return {'size': size, 'atmosphere': atmosphere,
            'temperature': temperature, 'hydrographics': hydrographics}


def build_civilisation():
    def pop_to_range(n, maximum):
        return 0 if population == 0 else to_range(n, maximum)

    def get_factions():
        if population == 0:
            return []
        dm = dict_map({1: (0, 7), -1: (x for x in range(10, 15))}, government)
        no_factions = randint(1, 3) + dm
        return [build_faction() for _ in range(no_factions)]

    def build_faction():
        return {'government': to_range(d6(2) - 7 + population, 15),
                'strength': d6(2),
                'name': ''}

    def get_starport():
        dm = dict_map({1: (8, 9), 2: [10], -1: (3, 4), -2: (0, 1, 2)},
                      population)
        return dict_map({'x': [2], 'e': (3, 4), 'd': (5, 6),
                         'c': (7, 8), 'b': (9, 10), 'a': [11]},
                        to_range(d6(2) + dm, 11, 2))

    def get_bases():
        scout = dict_val({'a': 10, 'b': 8, 'c': 8, 'd': 7}, starport, 13)
        naval = dict_val({'a': 8, 'b': 8}, starport, 13)
        research = dict_val({'a': 8, 'b': 10, 'c': 10}, starport, 13)
        tas = starport in ('a', 'b')
        return {'scout': d6(2) > scout, 'naval': d6(2) > naval,
                'research': d6(2) > research, 'tas': tas}

    population = d6(2) - 2
    government = pop_to_range(d6(2) - 7 + population, 15)
    factions = get_factions()
    law_level = pop_to_range(d6(2) - 7 + government, 9)
    starport = get_starport()
    bases = get_bases()
    return {'population': population, 'government': government,
            'factions': factions, 'lawLevel': law_level,
            'starport': starport, 'bases': bases}


def get_tech_level(planet, civ):
    def get_min_tl():
        min_tl_table = {3: (4, 7, 9), 5: (2, 3, 13, 14), 8: (0, 1, 8, 15),
                        9: [11], 10: [12]}
        return dict_map(min_tl_table, planet.get('atmosphere'))

    def starport():
        table = {6: 'a', 4: 'b', 2: 'c', -4: 'x'}
        return dict_map(table, civ.get('starport'))

    def size():
        return dict_map({2: (0, 1), 1: (2, 3, 4)}, planet.get('size'))

    def atmo():
        table = {1: (0, 1, 2, 3, 10, 11, 12, 13, 14, 15)}
        return dict_map(table, planet.get('atmosphere'))

    def hydro():
        return dict_map({1: (0, 9), 2: [10]}, planet.get('hydrographics'))

    def pop():
        table = {1: (1, 2, 3, 4, 5, 8), 9: [2], 10: [4]}
        return dict_map(table, civ.get('population'))

    def gov():
        table = {1: (0, 5), 2: [7], -2: (13, 14)}
        return dict_map(table, civ.get('government'))

    min_tl = get_min_tl()
    dm = starport() + size() + atmo() + hydro() + pop() + gov()
    return to_range(d6(2) + dm, 15, min_tl)


def get_travel_zone(planet, civ):
    atmo = planet.get('atmosphere') > 9
    gov = civ.get('government') in (0, 7, 10)
    law = civ.get('lawLevel') in (0, 9)
    warning = ''
    if atmo:
        warning += '|dangerous atmosphere| '
    if gov:
        warning += '|dangerous political climate| '
    if law:
        warning += '|inhospitable law enforcement| '
    return f'amber: {warning}' if any([atmo, law, gov]) else 'green'


def get_trade_code(planet, civ, tech_level):
    size = planet.get('size')
    atmo = planet.get('atmosphere')
    hydro = planet.get('hydrographics')
    population = civ.get('population')
    gov = civ.get('government')
    law = civ.get('lawLevel')

    is_ag = 10 > atmo > 3 and 9 > hydro > 3 and 8 > population > 4
    is_as = all(x == 0 for x in (size, atmo, hydro))
    is_ba = all(x == 0 for x in (population, gov, law))
    is_de = atmo > 1 and hydro == 0 and size > 2
    is_fl = atmo > 9 and hydro > 0
    is_ga = atmo in (5, 6, 8) and 8 > hydro > 4 and 9 > size > 5
    is_hi = population > 8
    is_ht = tech_level > 11
    is_ie = atmo < 2 and hydro > 0
    is_in = atmo in (0, 1, 2, 4, 7, 9) and population > 8
    is_lo = 4 > population
    is_lt = tech_level < 6
    is_na = 4 > atmo and 4 > hydro and population > 5
    is_ni = 7 > population
    is_po = atmo in (2, 3, 4, 5) and 4 > hydro
    is_ri = atmo in (6, 7, 8) and population in (6, 7, 8)
    is_va = atmo == 0
    is_wa = hydro > 9

    codes = {'ag': is_ag, 'as': is_as, 'ba': is_ba, 'de': is_de, 'fl': is_fl,
             'ga': is_ga, 'hi': is_hi, 'ht': is_ht, 'ie': is_ie, 'in': is_in,
             'lo': is_lo, 'lt': is_lt, 'na': is_na, 'ni': is_ni, 'po': is_po,
             'ri': is_ri, 'va': is_va, 'wa': is_wa}
    trade_codes = []
    for k, v in codes.items():
        if v:
            trade_codes.append(k)
    return trade_codes


def main():
    worlds = []
    for _ in range(1):
        seed()
        worlds.append(build_system(0))
    print(json.dumps(worlds))


if __name__ == '__main__':
    main()
