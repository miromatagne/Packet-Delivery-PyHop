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


def seleccionar_camion(state, dest):
    """
    Selecciona el camión más cercano de un destino en particular

    :param state: estado actual del problema
    :param dest: destino donde se necesita un camión
    :return: el ID del camión más cercano
    """
    min_distance = float('inf')
    best_truck = None
    for cam in state.trucks:
        if state.trucks[cam]['objective']:
            continue

        truck_point = state.trucks[cam]['point']
        truck_location = state.points[truck_point]['location']
        dest_location = state.points[dest]['location']

        distance_to_dest = distance(truck_location, dest_location)
        if distance_to_dest < min_distance:
            best_truck = cam
            min_distance = distance_to_dest

    return best_truck


def seleccionar_conductor(state, dest):
    """
    Selecciona el conductor más cercano de un destino en particular

    :param state: estado actual del problema
    :param dest: destino donde se necesita un conductor
    :return: el ID del conductor más cercano
    """
    min_distance = float('inf')
    best_con = None
    for con in state.drivers:
        driver_point = state.drivers[con]['point']
        driver_location = state.points[driver_point]['location']
        dest_location = state.points[dest]['location']

        distance_to_dest = distance(driver_location, dest_location)
        if distance_to_dest < min_distance:
            best_con = con
            min_distance = distance_to_dest

    return best_con


def seleccionar_siguiente_destino(state, origin, dest, con, conduce=False):
    """
    Selecciona el próximo destino intermedio durante un viaje de un origen
    hasta un destino.

    :param state: estado actual del problema
    :param origin: origen del viaje
    :param dest: destino final del viaje
    :param con: conductor que está efectuando el viaje
    :param conduce: indica si el conductor está conduciendo un camión o no
    :return: el nombre del siguiente destino
    """
    min_distance = float('inf')
    best_dest = None
    possible_next = state.points[origin]['connections']

    for next in possible_next:
        if conduce and not is_city(next):
            continue

        if not conduce and (is_city(origin) and is_city(next)):
            continue

        if next not in state.drivers[con]['path']:
            next_location = state.points[next]['location']
            dest_location = state.points[dest]['location']
            distance_to_dest = distance(next_location, dest_location)

            if distance_to_dest < min_distance:
                best_dest = next
                min_distance = distance_to_dest

    return best_dest


def get_bus_price(origin, dest):
    """
    Devuelve el precio de un trayecto en autobús de un origen a una destinación.
    El cálculo se basa en el precio por kilómetro que cuesta el autobús y la distancia
    del trayecto a efectuar.

    :param origin: origen
    :param dest: destino
    """
    return BUS_PRICE_PER_KM*distance(origin, dest)


def is_city(point):
    return point.startswith('C')

def is_intermediary(point):
    return point.startswith('P')

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
    pack_point = state.packets[paq]['point']
    truck_point = state.packets[paq]['point']

    if  pack_point == truck_point:
        state.packets[paq]['point'] = cam
        return state
    return False


def descargar_paquete(state, paq, cam):
    """
    Descarga un paquete de un camión.

    :param state: estado actual del problema
    :param paq: paquete a descargar
    :param cam: camión de donde descargar el paquete
    """
    pack_point = state.packets[paq]['point']
    if pack_point == cam:
        state.packets[paq]['point'] = state.trucks[cam]['point']
        return state
    return False


def autobus_op(state, con, dest):
    """
    Efectua un trayecto de autobús de un conductor.

    :param state: estado actual del problema
    :param con: conductor que coge el autobús
    :param dest: destino del autobús
    """
    driver_point = state.drivers[con]['point']

    if not is_intermediary(driver_point) and not is_intermediary(dest):
        return False

    if dest not in state.points[driver_point]['connections']:
        return False

    driver_location = state.points[driver_point]['location']
    dest_location = state.points[dest]['location']
    state.price += get_bus_price(driver_location, dest_location)
    state.drivers[con]['path'].append(dest)
    state.drivers[con]['point'] = dest

    return state


def caminar_op(state, con, dest):
    """
    Un conductor efectua un camino a pie de un punto a otro.

    :param state: estado actual del problema
    :param con: conductor que camina
    :param dest: destinación a donde camina el conductor
    """
    driver_point = state.drivers[con]['point']

    if not is_intermediary(driver_point) and not is_intermediary(dest):
        return False

    if dest not in state.points[driver_point]['connections']:
        return False

    # state.time += distancia(driver_loc, dest)
    state.drivers[con]['path'].append(dest)
    state.drivers[con]['point'] = dest
    return state


def conducir_op(state, cam, con, dest):
    """
    Un conductor conduce un camión hasta un destino.

    :param state: estado actual del problema
    :param cam: camión que está conducido
    :param con: conductor
    :param dest: destinación
    """
    if dest == None:
        return False

    driver_point = state.drivers[con]['point']
    truck_point = state.trucks[cam]['point']

    if is_intermediary(driver_point) or is_intermediary(dest):
        return False

    if driver_point == truck_point and dest in state.points[driver_point]['connections']:
        # state.time += distance(driver_loc, dest)
        state.drivers[con]['path'].append(dest)
        state.drivers[con]['point'] = dest
        state.trucks[cam]['point'] = dest
        return state

    return False

def marcar_camion(state, cam):
    state.trucks[cam]['objective'] = True
    return state

def reset_camino_conductor_op(state, con):
    """
    Reinicia el historial de ciudades que ha visitado un conductor

    :param con: conductor
    """
    state.drivers[con]['path'] = []
    return state


pyhop.declare_operators(cargar_paquete, descargar_paquete,
                        autobus_op, caminar_op, conducir_op, marcar_camion, reset_camino_conductor_op)
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
    if state.packets[paq]['point'] == dest:
        return []
    return False


def paquete_en_otro_lugar(state, paq, dest):
    """
    El paquete no está en su destino.

    :param paq: paquete
    :param dest: destinación
    """
    pack_point = state.packets[paq]['point']
    cam = seleccionar_camion(state, pack_point)
    con = seleccionar_conductor(state, pack_point)
    return [
        ('conseguir_camion_y_conductor', cam, con, pack_point),
        ('cargar_paquete', paq, cam),
        ('conducir', cam, con, dest),
        ('descargar_paquete', paq, cam)
    ]


pyhop.declare_methods('mover_paquete', paquete_en_destino,
                      paquete_en_otro_lugar)

# cumplir_objetivo_camion

def camion_en_objetivo(state, cam, dest):
    if state.trucks[cam]['point'] == dest:
        return [('marcar_camion', cam)]
    
    return False


def camion_no_en_objetivo(state, cam, dest):
    return [('mover_camion', cam, dest), ('marcar_camion', cam)]


pyhop.declare_methods('cumplir_objetivo_camion', camion_en_objetivo, camion_no_en_objetivo)


# mover_camion


def camion_en_destino(state, cam, dest):
    """
    El camión ya está en su destino.

    :param cam: camión
    :param dest: destinación
    """
    if state.trucks[cam]['point'] == dest:
        return []
    return False


def camion_en_otro_lugar(state, cam, dest):
    """
    El camión no está en su destino.

    :param cam: camión
    :param dest: destinación
    """
    truck_point = state.trucks[cam]['point']
    con = seleccionar_conductor(state, truck_point)
    return [
        ('conseguir_conductor', con, truck_point),
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
    if state.drivers[con]['point'] == dest:
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
    driver_point = state.drivers[con]['point']
    state.drivers[con]['path'].append(driver_point)
    return [('mover_conductor_paso', con, dest), ('mover_conductor', con, dest)]


pyhop.declare_methods(
    'mover_conductor', conductor_en_destino, conductor_en_otro_lugar)

# mover_conductor_paso

def conducir_paso(state, con, dest):
    driver_point = state.drivers[con]['point']
    cam = seleccionar_camion(state, driver_point)

    if state.trucks[cam]['point'] == driver_point:
        d = seleccionar_siguiente_destino(state, driver_point, dest, con, conduce=True)
        print('\n\n\nConduzco paso ' + cam + ' ' + con + '\n\n\n')
        return [('conducir_op', cam, con, d)]

    return False

def autobus(state, con, dest):
    """
    El conductor va a efectuar un trayecto en autobús si queda suficiente dinero.

    :param state: estado actual del problema
    :param con: conductor
    :param d: siguiente destino intermedio
    :param dest: destinación final
    """
    driver_point = state.drivers[con]['point']
    driver_location = state.points[driver_point]['location']

    d = seleccionar_siguiente_destino(state, driver_point, dest, con, conduce=False)
    dest_location = state.points[d]['location']

    if get_bus_price(driver_location, dest_location) <= BUDGET - state.price:
        return [('autobus_op', con, d)]

    return False


def caminar(state, con, dest):
    """
    El conductor va a efectuar un trayecto caminando.

    :param state: estado actual del problema
    :param con: conductor
    :param d: siguiente destinación intermedia
    :param dest: destinación final
    """
    driver_point = state.drivers[con]['point']
    location = state.points[driver_point]['location']

    d = seleccionar_siguiente_destino(state, driver_point, dest, con, conduce=False)
    dest_location = state.points[d]['location']

    if get_bus_price(location, dest_location) > BUDGET - state.price:
        return [('caminar_op', con, d)]

    return False


pyhop.declare_methods('mover_conductor_paso', conducir_paso, autobus, caminar)

# conseguir_camion_y_conductor(cam, con, dest)


def camion_conseguido(state, cam, con, dest):
    """
    Ya hay un camión a la destinación solicitada.

    :param state: estado actual del problema
    :param cam: camión
    :param con: conductor
    :param dest: destino
    """
    if state.trucks[cam]['point'] == dest:
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
    if state.drivers[con]['point'] == dest:
        return []
    return False


def conductor_por_conseguir(state, con, dest):
    """
    Todavía no hay ningun conductor a la destinación solicitada.

    :param state: estado actual del problema
    :param con: conductor
    :param dest: destinación
    """
    if state.drivers[con]['point'] != dest:
        return [("mover_conductor", con, dest)]
    return False


pyhop.declare_methods('conseguir_conductor',
                      conductor_conseguido, conductor_por_conseguir)

# conducir


def en_destino(state, cam, con, dest):
    """
    El camión ha llegado a su destino.

    :param state: estado actual del problema
    :param cam: camión
    :param con: conductor
    :param dest: destino
    """
    driver_point = state.drivers[con]['point']
    truck_point = state.trucks[cam]['point']

    if driver_point == truck_point and driver_point == dest:
        state.drivers[con]['path'] = []
        return []

    return False


def en_otro_lugar(state, cam, con, dest):
    """
    El camión no ha llegado a su destino.

    :param state: estado actual del problema
    :param cam: camión
    :param con: conductor
    :param dest: destino
    """
    driver_point = state.drivers[con]['point']
    truck_point = state.trucks[cam]['point']

    if driver_point == truck_point:
        d = seleccionar_siguiente_destino(
            state, driver_point, dest, con, conduce=True)
        return [("conducir_op", cam, con, d), ("conducir", cam, con, dest)]

    return False


pyhop.declare_methods('conducir', en_destino, en_otro_lugar)

# ====================================================================== #

def iterative_goal_m(state, goal):
    for data in goal.data:
        if data[0] == 'driver':
            if state.drivers[data[1]]['point'] != data[2]:
                return [('mover_conductor', data[1], data[2], False), ('iterative_goal', goal)]
        if data[0] == 'truck':
            if state.trucks[data[1]]['point'] != data[2]:
                return [('cumplir_objetivo_camion', data[1], data[2]), ('iterative_goal', goal)]
        if data[0] == 'package':
            if state.packets[data[1]]['point'] != data[2]:
                return [('mover_paquete', data[1], data[2]), ('iterative_goal', goal)]
    return []


pyhop.declare_methods('iterative_goal', iterative_goal_m)

# Descripción del estado inicial del problema
state = pyhop.State('state')
state.points = {'C0': {'location': {'X': 0, 'Y': 50}, 'connections': {'C1', 'C2', 'P01'}},
                'C1': {'location': {'X': 100, 'Y': 50}, 'connections': {'C0', 'C2', 'P01', 'P12'}},
                'C2': {'location': {'X': 50, 'Y': 0}, 'connections': {'C0', 'C1', 'P12'}},
                'P01': {'location': {'X': 50, 'Y': 100}, 'connections': {'C0', 'C1'}},
                'P12': {'location': {'X': 75, 'Y': 0}, 'connections': {'C1', 'C2'}}}

state.packets = {'P1': {'point': 'C0'},
                 'P2': {'point': 'C0'}}

state.trucks = {'T1': {'point': 'C1', 'objective': False},
                'T2': {'point': 'C0', 'objective': False}}

state.drivers = {'D1': {'point': 'P01', 'path': []},
                 'D2': {'point': 'C1', 'path': []}}

state.time = 0
state.price = 0

# Descripción del objetivo del problema
goal = pyhop.Goal('goal')
goal.data = [['package', 'P1', 'C1'], [
    'package', 'P2', 'C2'], ['truck', 'T1', 'C0'], ['driver', 'D1', 'C0']]

pyhop.pyhop(state, [('iterative_goal', goal)], verbose=2)
