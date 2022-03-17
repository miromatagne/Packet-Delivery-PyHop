from lib2to3.pgen2 import driver
from math import sqrt, pow, inf
import pyhop

# Comprobar si un elemento está en un conjunto
# "C1" in state.cities["C0"]["connections"]

# Recorrer elementos de un conjunto
# for city in state.cities["C0"]["connections"]:

# Problem constants
BUDGET = 10
BUS_PRICE_PER_KM = 0.1

#############################
# FUNCIONES AUXILIARES
#############################


def distance(c1, c2):
    """
    Calcula la distancia entre 2 puntos

    :param c1: objeto que describe la ubicación del primer punto
    :param c2: objeto que describe la ubicación del segundo punto
    :return: la distancia en linea recta entre los 2 puntos
    """
    x = pow(c1['X']-c2['X'], 2)
    y = pow(c1['Y']-c2['Y'], 2)
    return sqrt(x+y)


def seleccionarCamion(state, dest):
    """
    Selecciona el camión más cercano de una destinación en particular

    :param state: estado actual del problema
    :param dest: destinación donde se necesita un camión
    :return: el ID del camión más cercano
    """
    min_distance = float('inf')
    best_truck = None
    for cam in state.trucks:
        distance_to_dest = distance(
            state.cities[state.trucks[cam]['location']]['location'], state.cities[dest]['location'])
        if distance_to_dest < min_distance:
            best_truck = cam
            min_distance = distance_to_dest
    return best_truck


def seleccionarConductor(state, dest):
    """
    Selecciona el conductor más cercano de una destinación en particular

    :param state: estado actual del problema
    :param dest: destinación donde se necesita un conductor
    :return: el ID del conductor más cercano
    """
    min_distance = float('inf')
    best_con = None
    for con in state.drivers:
        driver_loc = state.drivers[con]['location']
        if driver_loc in state.intermediary_points.keys():
            location = state.intermediary_points[driver_loc]['location']
        else:
            location = state.cities[state.drivers[con]
                                    ['location']]['location']
        distance_to_dest = distance(location, state.cities[dest]['location'])
        if distance_to_dest < min_distance:
            best_con = con
            min_distance = distance_to_dest
    return best_con


def seleccionarSiguienteDestino(state, origin, destination, con, conduce=False):
    """
    Selecciona la proxima destinacion intermedia durante un viaje de un origen
    hasta una destinación.

    :param state: estado actual del problema
    :param origin: origen del viaje
    :param destination: destinación final del viaje
    :param con: conductor que está efectuando el viaje
    :param conduce: indica si el conductor está conduciendo un camión o no
    :return: el nombre del siguiente destino
    """
    min_distance = float('inf')
    best_dest = None
    possible_next = []
    origin_is_city = origin in state.cities.keys()

    if not origin_is_city:
        possible_next = state.intermediary_points[origin]['connections']
    else:
        possible_next = state.cities[origin]['connections']

    destination_is_city = destination in state.cities.keys()
    for next in possible_next:
        next_is_city = next in state.cities.keys()

        if conduce and not next_is_city:
            continue

        if not conduce and (origin_is_city and next_is_city):
            continue

        if next not in state.drivers[con]['path']:
            if next_is_city and destination_is_city:
                distance_to_dest = distance(
                    state.cities[destination]['location'], state.cities[next]['location'])
            elif next_is_city and not destination_is_city:
                distance_to_dest = distance(
                    state.cities[next]['location'], state.intermediary_points[destination]['location'])
            elif not next_is_city and destination_is_city:
                distance_to_dest = distance(
                    state.intermediary_points[next]['location'], state.cities[destination]['location'])
            elif not next_is_city and not destination_is_city:
                distance_to_dest = distance(
                    state.intermediary_points[destination]['location'], state.intermediary_points[next]['location'])

            if distance_to_dest < min_distance:
                best_dest = next
                min_distance = distance_to_dest

    return best_dest


def getBusPrice(origin, destination):
    """
    Devuelve el precio de un trayecto en autobús de un origen a una destinación.
    El cálculo se basa en el precio por kilómetro que cuesta el autobús y la distancia
    del trayecto a efectuar.

    :param origin: origen
    :param destination: destinación
    """
    print(origin)
    print(destination)
    return BUS_PRICE_PER_KM*distance(origin, destination)


#############################
# OPERADORES
#############################


def cargar_paquete(state, paq, cam):
    """
    Carga un paquete en un camión.

    :param state: estado actual del problema
    :param paq: paquete a cargar
    :param cam: camión donde cargar el paquete
    """
    if state.packets[paq]['location'] == state.trucks[cam]['location']:
        state.packets[paq]['location'] = cam
        return state
    return False


def descargar_paquete(state, paq, cam):
    """
    Descarga un paquete de un camión.

    :param state: estado actual del problema
    :param paq: paquete a descargar
    :param cam: camión de donde descargar el paquete
    """
    if state.packets[paq]['location'] == cam:
        state.packets[paq]['location'] = state.trucks[cam]['location']
        return state
    return False


def autobus_op(state, con, dest):
    """
    Efectua un trayecto de autobús de un conductor.

    :param state: estado actual del problema
    :param con: conductor que coge el autobús
    :param dest: destinación del autobús
    """
    driver_loc = state.drivers[con]['location']
    if driver_loc in state.intermediary_points.keys():
        if dest in state.intermediary_points[driver_loc]['connections']:
            if dest in state.intermediary_points.keys():
                state.price += getBusPrice(state.intermediary_points[state.drivers[con]
                                                                     ['location']]['location'], state.intermediary_points[dest]['location'])
            else:
                state.price += getBusPrice(
                    state.intermediary_points[state.drivers[con]['location']]['location'], state.cities[dest]['location'])
            # state.time += distancia(state.drivers[con]["location"], dest)
            state.drivers[con]['path'].append(dest)
            state.drivers[con]['location'] = dest
            return state
    elif driver_loc in state.cities.keys():
        if dest in state.intermediary_points.keys() and dest in state.cities[driver_loc]['connections']:
            if dest in state.intermediary_points.keys():
                state.price += getBusPrice(state.cities[state.drivers[con]['location']]
                                           ['location'], state.intermediary_points[dest]['location'])
            else:
                state.price += getBusPrice(
                    state.cities[state.drivers[con]['location']]['location'], state.cities[dest]['location'])
            state.drivers[con]['path'].append(dest)
            state.drivers[con]['location'] = dest
            # state.time += distancia(state.drivers[con]["location"], dest)
            return state
    return False


def caminar_op(state, con, dest):
    """
    Un conductor efectua un camino a pie de un punto a otro.

    :param state: estado actual del problema
    :param con: conductor que camina
    :param dest: destinación a donde camina el conductor
    """
    driver_loc = state.drivers[con]['location']
    if driver_loc in state.intermediary_points.keys():
        if dest in state.intermediary_points[driver_loc]['connections']:
            # state.time += distancia(driver_loc, dest)
            state.drivers[con]['path'].append(dest)
            state.drivers[con]['location'] = dest
            return state
    elif driver_loc in state.cities.keys():
        if dest in state.intermediary_points.keys() and dest in state.cities[driver_loc]:
            # state.time += distancia(driver_loc, dest)
            state.drivers[con]['path'].append(dest)
            state.drivers[con]['location'] = dest
            return state
    return False


def conducir_op(state, cam, con, dest):
    """
    Un conductor conduce un camión hasta un destino.

    :param state: estado actual del problema
    :param cam: camión que está conducido
    :param con: conductor
    :param dest: destinación
    """
    driver_loc = state.drivers[con]['location']
    truck_loc = state.trucks[cam]['location']
    if driver_loc == truck_loc and dest in state.cities[driver_loc]['connections']:
        # state.time += distance(driver_loc, dest)
        state.drivers[con]['path'].append(dest)
        state.drivers[con]['location'] = dest
        state.trucks[cam]['location'] = dest
        return state
    return False


def reset_camino_conductor_op(state, con):
    """
    Reinicia el historial de ciudades que ha visitado un conductor

    :param con: conductor
    """
    state.drivers[con]['path'] = []
    return state


pyhop.declare_operators(cargar_paquete, descargar_paquete,
                        autobus_op, caminar_op, conducir_op, reset_camino_conductor_op)
print('')
pyhop.print_operators()

#############################
# METODOS
#############################

# mover_paquete


def paquete_en_destino(state, paq, dest):
    """
    El paquete ya está en su destino.

    :param paq: paquete
    :param dest: destinación
    """
    if state.packets[paq]['location'] == dest:
        return []
    return False


def paquete_en_otro_lugar(state, paq, dest):
    """
    El paquete no está en su destino.

    :param paq: paquete
    :param dest: destinación
    """
    paq_loc = state.packets[paq]['location']
    cam = seleccionarCamion(state, state.packets[paq]["location"])
    con = seleccionarConductor(state, state.packets[paq]["location"])
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
    """
    El camión ya está en su destino.

    :param cam: camión
    :param dest: destinación
    """
    if state.trucks[cam]['location'] == dest:
        return []
    return False


def camion_en_otro_lugar(state, cam, dest):
    """
    El camión no está en su destino.

    :param cam: camión
    :param dest: destinación
    """
    truck_loc = state.trucks[cam]['location']
    con = seleccionarConductor(state, truck_loc)
    return [
        ('conseguir_conductor', con, truck_loc),
        ('conducir', cam, con, dest)
    ]


pyhop.declare_methods('mover_camion', camion_en_destino, camion_en_otro_lugar)

# mover_conductor


def conductor_en_destino(state, con, dest):
    """
    El conductor ya está en su destino.

    :param con: conductor
    :param dest: destinación
    """
    if state.drivers[con]['location'] == dest:
        print("Reset path")
        state.drivers[con]['path'] = []
        return []
        # return [('reset_camino_conductor_op', con)]
    return False


def conductor_en_otro_lugar(state, con, dest):
    """
    El conductor no está en su destino.

    :param conductor: conductor
    :param dest: destinación
    """
    if state.drivers[con]['location'] != dest:
        state.drivers[con]['path'].append(state.drivers[con]['location'])
        driver_loc = state.drivers[con]['location']
        d = seleccionarSiguienteDestino(
            state, driver_loc, dest, con, conduce=False)
        return [("mover_conductor_paso", con, d, dest)]
    return False


pyhop.declare_methods(
    'mover_conductor', conductor_en_destino, conductor_en_otro_lugar)

# mover_conductor_paso


def autobus(state, con, d, dest):
    """
    El conductor va a efectuar un trayecto en autobús si queda suficiente dinero.

    :param state: estado actual del problema
    :param con: conductor
    :param d: siguiente destinación intermedia
    :param dest: destinación final
    """
    if state.drivers[con]['location'] in state.cities.keys():
        driver_location = state.cities[state.drivers[con]
                                       ['location']]['location']
    else:
        driver_location = state.intermediary_points[state.drivers[con]
                                                    ['location']]['location']
    if d in state.cities.keys():
        d_location = state.cities[d]['location']
    else:
        d_location = state.intermediary_points[d]['location']
    if getBusPrice(driver_location, d_location) <= BUDGET - state.price:
        return [
            ('autobus_op', con, d),
            ('mover_conductor', con, dest)
        ]
    return False


def caminar(state, con, d, dest):
    """
    El conductor va a efectuar un trayecto caminando.

    :param state: estado actual del problema
    :param con: conductor
    :param d: siguiente destinación intermedia
    :param dest: destinación final
    """
    if state.drivers[con]['location'] in state.cities.keys():
        driver_location = state.cities[state.drivers[con]
                                       ['location']]['location']
    else:
        driver_location = state.intermediary_points[state.drivers[con]
                                                    ['location']]['location']
    if d in state.cities.keys():
        d_location = state.cities[d]['location']
    else:
        d_location = state.intermediary_points[d]['location']
    if getBusPrice(driver_location, d_location) > BUDGET - state.price:
        return [
            ('caminar_op', con, d),
            ('mover_conductor', con, dest)
        ]
    return False


pyhop.declare_methods('mover_conductor_paso', autobus, caminar)

# conseguir_camion_y_conductor(cam, con, dest)


def camion_conseguido(state, cam, con, dest):
    """
    Ya hay un camión a la destinación solicitada.

    :param state: estado actual del problema
    :param cam: camión
    :param con: conductor
    :param dest: destinación
    """
    if state.trucks[cam]['location'] == dest:
        return[('conseguir_conductor', con, dest)]
    return False


def camion_por_conseguir(state, cam, con, dest):
    """
    Todavía no hay ningun camión a la destinación solicitada.

    :param state: estado actual del problema
    :param cam: camión
    :param con: conductor
    :param dest: destinación
    """
    return [('mover_camion', cam, dest)]


pyhop.declare_methods('conseguir_camion_y_conductor',
                      camion_conseguido, camion_por_conseguir)

# conseguir_conductor


def conductor_conseguido(state, con, dest):
    """
    Ya hay un conductor a la destinación solicitada.

    :param state: estado actual del problema
    :param con: conductor
    :param dest: destinación
    """
    if state.drivers[con]['location'] == dest:
        print("Reset path")
        state.drivers[con]['path'] = []
        return []
        # return [('reset_camino_conductor_op', con)]
    return False


def conductor_por_conseguir(state, con, dest):
    """
    Todavía no hay ningun conductor a la destinación solicitada.

    :param state: estado actual del problema
    :param con: conductor
    :param dest: destinación
    """
    if state.drivers[con]['location'] != dest:
        return [("mover_conductor", con, dest)]
    return False


pyhop.declare_methods('conseguir_conductor',
                      conductor_conseguido, conductor_por_conseguir)

# conducir


def en_destino(state, cam, con, dest):
    """
    El camión ha llegado a su destinación.

    :param state: estado actual del problema
    :param cam: camión
    :param con: conductor
    :param dest: destinación
    """
    driver_loc = state.drivers[con]['location']
    truck_loc = state.trucks[cam]['location']
    if driver_loc == truck_loc and driver_loc == dest:
        print("Reset path")
        state.drivers[con]['path'] = []
        return []
    return False


def en_otro_lugar(state, cam, con, dest):
    """
    El camión no ha llegado a su destinación.

    :param state: estado actual del problema
    :param cam: camión
    :param con: conductor
    :param dest: destinación
    """
    driver_loc = state.drivers[con]['location']
    truck_loc = state.trucks[cam]['location']
    if driver_loc == truck_loc:
        d = seleccionarSiguienteDestino(
            state, truck_loc, dest, con, conduce=True)
        return [("conducir_op", cam, con, d), ("conducir", cam, con, dest)]
    return False


pyhop.declare_methods('conducir', en_destino, en_otro_lugar)

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
    return []


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

state.drivers = {'D1': {'location': 'P01', 'path': []},
                 'D2': {'location': 'C1', 'path': []}}

state.time = 0
state.price = 0

# Descripción del objetivo del problema
goal = pyhop.Goal('goal')
goal.data = [['package', 'P1', 'C1'], [
    'package', 'P2', 'C2'], ['truck', 'T1', 'C0'], ['driver', 'D1', 'C0']]

pyhop.pyhop(state, [('iterative_goal', goal)], verbose=2)
