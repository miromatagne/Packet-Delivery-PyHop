from lib2to3.pgen2 import driver
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

# TODO


def seleccionarCamion():
    return 'T1'

# TODO


def seleccionarConductor():
    return 'D1'

# TODO


def seleccionarSiguienteDestino():
    return 'C0'

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
    cam = seleccionarCamion()
    con = seleccionarConductor()
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
    con = seleccionarConductor()
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
    d = seleccionarSiguienteDestino()
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


def camion_conseguido(state, cam, con, dest):
    if any(state.trucks[truck]['location'] == dest for truck in state.trucks):
        return[('conseguir_conductor', dest)]
    return False


def camion_por_conseguir(state, dest):
    cam = seleccionarCamion()
    return [('mover_camion', cam, dest)]


pyhop.declare_methods('conseguir_camion_y_conductor',
                      camion_conseguido, camion_por_conseguir)

# conseguir_conductor


def conductor_conseguido(state, dest):
    if any(state.drivers[driver]['location'] == dest for driver in state.drivers):
        return []
    return False


def conductor_por_conseguir(state, dest):
    con = seleccionarConductor()
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
        d = seleccionarSiguienteDestino()
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
                'C1': {'location': {'X': 100, 'Y': 50}, 'connections': {'C0', 'C2', 'P01', 'P02'}},
                'C2': {'location': {'X': 50, 'Y': 0}, 'connections': {'C0', 'C1', 'P02'}}}

state.intermediary_points = {'P01': {'location': {'X': 50, 'Y': 100}, 'connections': {'C0', 'C1'}},
                             'P12': {'location': {'X': 75, 'Y': 0}, 'connections': {'C1', 'C2'}}}

state.packets = {'P1': {'location': 'C0'},
                 'P2': {'location': 'C0'}}

state.trucks = {'T1': {'location': 'C1'},
                'T2': {'location': 'C0'}}

state.drivers = {'D1': {'location': 'P01'},
                 'D2': {'location': 'C1'}}

state.time = 0
state.price = 0

# Descripción del objetivo del problema
goal = pyhop.Goal('goal')
goal.data = [['driver', 'D1', 'C0'], ['truck', 'T1', 'C0'],
             ['package', 'P1', 'C1'], ['package', 'P2', 'C2']]
