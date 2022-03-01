import pyhop

# Comprobar si un elemento está en un conjunto
# "C1" in state.cities["C0"]["connections"]

# Recorrer elementos de un conjunto
# for city in state.cities["C0"]["connections"]:

# Descripción del estado inicial del problema
state.cities = {
    'C0': {'location': {'X': 0, 'Y': 50}, 'connections': {'C1', 'C2', 'P01'}},
    'C1': {'location': {'X': 100, 'Y': 50}, 'connections': {'C0', 'C2', 'P01', 'P02'}},
    'C2': {'location': {'X': 50, 'Y': 0}, 'connections': {'C0', 'C1', 'P02'}}
}
state.intermediary_points = {
    'P01': {'location': {'X': 50, 'Y': 100}, 'connections': {'C0', 'C1'}},
    'P02': {'location': {'X': 75, 'Y': 0}, 'connections': {'C1', 'C2'}}
}
state.packets = {
    'P1': {'location': 'C0'},
    'P2': {'location': 'C0'}
}
state.trucks = {
    'T1': {'location': 'C1'},
    'T2': {'location': 'C0'}
}
state.drivers = 
{
    'D1': {'location': 'P01'},
    'D2': {'location': 'C1'}
}
