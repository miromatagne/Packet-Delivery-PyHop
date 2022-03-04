import pyhop

# Comprobar si un elemento está en un conjunto
# "C1" in state.cities["C0"]["connections"]

# Recorrer elementos de un conjunto
# for city in state.cities["C0"]["connections"]:


def paquete_en_destino_m(state, paq, dest):
    if state.packets[paq]["location"] == dest:
        return []
    return False


def mover_paquete_m(state, pas, dest):
    pass


pyhop.declare_methods('mover_paquete', paquete_en_destino_m, mover_paquete_m)


def camion_en_destino(state, cam, dest):
    if state.trucks[cam]["location"] == dest:
        return []
    return False


def mover_camion_m(state, cam, dest):
    pass


pyhop.declare_methods('mover_camion', camion_en_destino, mover_camion_m)


def conductor_en_destino(state, con, dest):
    if state.drivers[con]["location"] == dest:
        return []
    return False


def mover_conductor_m(state, con, dest):
    pass


pyhop.declare_methods(
    'mover_conductor', conductor_en_destino, mover_conductor_m)


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
                             'P02': {'location': {'X': 75, 'Y': 0}, 'connections': {'C1', 'C2'}}}

state.packets = {'P1': {'location': 'C0'},
                 'P2': {'location': 'C0'}}

state.trucks = {'T1': {'location': 'C1'},
                'T2': {'location': 'C0'}}

state.drivers = {'D1': {'location': 'P01'},
                 'D2': {'location': 'C1'}}

# Descripción del objetivo del problema
goal = pyhop.Goal('goal')
goal.data = [['driver', 'D1', 'C0'], ['truck', 'T1', 'C0'],
             ['package', 'P1', 'C1'], ['package', 'P2', 'C2']]
