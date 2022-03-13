from math import sqrt, pow, inf
import pyhop

# Comprobar si un elemento está en un conjunto
# "C1" in state.cities["C0"]["connections"]

# Recorrer elementos de un conjunto
# for city in state.cities["C0"]["connections"]:

# Problem constants
BUS_PRICE = 2

#############################
# FUNCIONES AUXILIARES
#############################


def distance(c1, c2):
    # print(c1)
    # print(c2)
    x = pow(c1['X']-c2['X'], 2)
    y = pow(c1['Y']-c2['Y'], 2)
    return sqrt(x+y)


def seleccionarCamion(state, dest):
    min_distance = float('inf')
    best_truck = None
    for cam in state.trucks:
        if distance(state.cities[cam['location']]['location'], state.cities[dest]['location']) < min_distance:
            best_truck = cam
            min_distance = distance(
                state.cities[cam['location']]['location'], state.cities[dest]['location'])
    return best_truck


def seleccionarConductor(state, dest):
    min_distance = float('inf')
    best_con = None
    for con in state.drivers:
        if state.drivers[con]['location'] in state.intermediary_points.keys():
            con_location = state.intermediary_points[state.drivers[con]
                                                     ['location']]['location']
        else:
            con_location = state.cities[state.drivers[con]
                                        ['location']]['location']
        if distance(con_location, state.cities[dest]['location']) < min_distance:
            best_con = con
            min_distance = distance(
                con_location, state.cities[dest]['location'])
    return best_con


def seleccionarSiguienteDestino(state, origin, dest, driver=False):
    min_distance = float('inf')
    best_city = None
    possible_cities = []
    if origin in state.intermediary_points.keys():
        possible_cities = state.intermediary_points[origin]['connections']
    else:
        possible_cities = state.cities[origin]['connections']
    for city in possible_cities:
        if city not in state.path:
            if city not in state.intermediary_points.keys():
                if distance(state.cities[city]['location'], state.cities[dest]['location']) < min_distance:
                    best_city = city
                    min_distance = distance(
                        state.cities[city]['location'], state.cities[dest]['location'])
            elif driver:
                if distance(state.intermediary_points[city]['location'], state.cities[dest]['location']) < min_distance:
                    best_city = city
                    min_distance = distance(
                        state.intermediary_points[city]['location'], state.cities[dest]['location'])
    return best_city

#############################
# OPERADORES
#############################


def cargar_paquete(state, paq, cam):
    if state.packets[paq]['location'] == state.trucks[cam]['location']:
        state.packets[paq]['location'] = cam
        return state
    return False


def descargar_paquete(state, paq, cam):
    if state.packets[paq]['location'] == cam:
        state.packets[paq]['location'] = state.trucks[cam]['location']
        return state
    return False


def autobus_op(state, con, dest):
    driver_loc = state.drivers[con]['location']
    if driver_loc in state.intermediary_points.keys():
        if dest in state.intermediary_points[driver_loc]['connections']:
            state.price += BUS_PRICE
            # state.time += distancia(state.drivers[con]["location"], dest)
            state.drivers[con]['location'] = dest
            return state
    elif driver_loc in state.cities.keys():
        if dest in state.intermediary_points.keys() and dest in state.cities[driver_loc]['connections']:
            state.drivers[con]['location'] = dest
            state.price += BUS_PRICE
            # state.time += distancia(state.drivers[con]["location"], dest)
            return state
    return False


def caminar_op(state, con, dest):
    driver_loc = state.drivers[con]['location']
    if driver_loc in state.intermediary_points.keys():
        if dest in state.intermediary_points[driver_loc]['connections']:
            # state.time += distancia(driver_loc, dest)
            state.drivers[con]['location'] = dest
            return state
    elif driver_loc in state.cities.keys():
        if dest in state.intermediary_points.keys() and dest in state.cities[driver_loc]:
            # state.time += distancia(driver_loc, dest)
            state.drivers[con]['location'] = dest
            return state
    return False


def conducir_op(state, cam, con, dest):
    driver_loc = state.drivers[con]['location']
    truck_loc = state.trucks[cam]['location']
    if driver_loc == truck_loc and dest in state.cities[driver_loc]['connections']:
        # state.time += distance(driver_loc, dest)
        state.drivers[con]['location'] = dest
        state.trucks[cam]['location'] = dest
        return state
    return False


pyhop.declare_operators(cargar_paquete, descargar_paquete,
                        autobus_op, caminar_op, conducir_op)
print('')
pyhop.print_operators()

#############################
# METODOS
#############################

# mover_paquete


def paquete_en_destino(state, paq, dest):
    if state.packets[paq]['location'] == dest:
        return []
    return False


def paquete_en_otro_lugar(state, paq, dest):
    cam = seleccionarCamion(state, state.packets[paq]["location"])
    con = seleccionarConductor(state, state.packets[paq]["location"])
    paq_loc = state.packets[paq]['location']
    return [
        ('conseguir_camion_y_conductor', cam, con, paq_loc),
        ('cargar_paquete', paq, cam),
        ('conducir', cam, con, dest),
        ('descargar_paquete', paq, cam)
    ]


pyhop.declare_methods('mover_paquete', paquete_en_destino,
                      paquete_en_otro_lugar)

# mover_camion


def camion_en_destino(state, cam, dest):
    if state.trucks[cam]['location'] == dest:
        return []
    return False


def camion_en_otro_lugar(state, cam, dest):
    truck_loc = state.trucks[cam]['location']
    con = seleccionarConductor(state, dest)
    return [
        ('conseguir_conductor', con, truck_loc),
        ('conducir', cam, con, dest)
    ]


pyhop.declare_methods('mover_camion', camion_en_destino, camion_en_otro_lugar)

# mover_conductor


def conductor_en_destino(state, con, dest):
    if state.drivers[con]['location'] == dest:
        return []
    return False


def conductor_en_otro_lugar(state, con, dest):
    d = seleccionarSiguienteDestino(
        state, state.drivers[con]['location'], dest, driver=True)
    return [("mover_conductor_paso", con, d, dest)]


pyhop.declare_methods(
    'mover_conductor', conductor_en_destino, conductor_en_otro_lugar)

# mover_conductor_paso
# TODO : añadir las condiciones que determinen cuando tomar el autobus y cuando caminar


def autobus(state, con, d, dest):
    return [
        ('autobus_op', con, d),
        ('mover_conductor', con, dest)
    ]


def caminar(state, con, d, dest):
    return [
        ('caminar_op', con, d),
        ('mover_conductor', con, dest)
    ]


pyhop.declare_methods('mover_conductor_paso', autobus, caminar)

# conseguir_camion_y_conductor(dest)


def camion_conseguido(state, con, cam, dest):
    if any(state.trucks[truck]['location'] == dest for truck in state.trucks):
        return[('conseguir_conductor', con, dest)]
    return False


def camion_por_conseguir(state, con, cam, dest):
    #cam = seleccionarCamion(state, dest)
    return [('mover_camion', cam, dest)]


pyhop.declare_methods('conseguir_camion_y_conductor',
                      camion_conseguido, camion_por_conseguir)

# conseguir_conductor


def conductor_conseguido(state, con, dest):
    if any(state.drivers[driver]['location'] == dest for driver in state.drivers):
        return []
    return False


def conductor_por_conseguir(state, con, dest):
    #con = seleccionarConductor(state, dest)
    return [("mover_conductor", con, dest)]


pyhop.declare_methods('conseguir_conductor',
                      conductor_conseguido, conductor_por_conseguir)

# conducir


def en_destino(state, cam, con, dest):
    driver_loc = state.drivers[con]['location']
    truck_loc = state.trucks[cam]['location']
    if driver_loc == truck_loc and driver_loc != dest:
        return []
    return False


def en_otro_lugar(state, cam, con, dest):
    driver_loc = state.drivers[con]['location']
    truck_loc = state.trucks[cam]['location']
    if driver_loc == truck_loc:
        d = seleccionarSiguienteDestino(state, truck_loc, dest)
        return [("conducir_op", cam, con, d), ("conducir", cam, con, dest)]
    return False


# ====================================================================== #


pyhop.declare_methods(
    'mover_conductor', conductor_en_destino, conductor_en_otro_lugar)


def iterative_goal_m(state, goal):
    for data in goal.data:
        if data[0] == 'driver':
            if state.drivers[data[1]]['location'] != data[2]:
                return [('mover_conductor', data[1], data[2]), ('iterative_goal', goal)]
        if data[0] == 'truck':
            if state.trucks[data[1]]['location'] != data[2]:
                return [('mover_camion', data[1], data[2]), ('iterative_goal', goal)]
        if data[0] == 'package':
            if state.packets[data[1]]['location'] != data[2]:
                return [('mover_paquete', data[1], data[2]), ('iterative_goal', goal)]


pyhop.declare_methods('iterative_goal', iterative_goal_m)

# Descripción del estado inicial del problema
state = pyhop.State('state')
state.cities = {'C0': {'location': {'X': 0, 'Y': 50}, 'connections': {'C1', 'C2', 'P01'}},
                'C1': {'location': {'X': 100, 'Y': 50}, 'connections': {'C0', 'C2', 'P01', 'P12'}},
                'C2': {'location': {'X': 50, 'Y': 0}, 'connections': {'C0', 'C1', 'P12'}}}

state.intermediary_points = {'P01': {'location': {'X': 50, 'Y': 100}, 'connections': {'C0', 'C1'}},
                             'P12': {'location': {'X': 75, 'Y': 0}, 'connections': {'C1', 'C2'}}}

state.packets = {'P1': {'location': 'C0'},
                 'P2': {'location': 'C0'}}

state.trucks = {'T1': {'location': 'C1'},
                'T2': {'location': 'C0'}}

state.drivers = {'D1': {'location': 'P01'},
                 'D2': {'location': 'C1'}}

state.path = []

state.time = 0
state.price = 0

# Descripción del objetivo del problema
goal = pyhop.Goal('goal')
goal.data = [['driver', 'D1', 'C0'], ['truck', 'T1', 'C0'],
             ['package', 'P1', 'C1'], ['package', 'P2', 'C2']]

pyhop.pyhop(state, [('iterative_goal', goal)], verbose=1)
