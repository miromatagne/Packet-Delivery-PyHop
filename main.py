import pyhop

# Descripción del estado inicial del problema
state = pyhop.State('state')
state.city_coordinates = {'C0': {'X': 0, 'Y': 50}, 'C1': {
    'X': 100, 'Y': 50}, 'C2': {'X': 50, 'Y': 0}}
state.intermediary_point_coordintates = {'P_01': {'X': 50, 'Y': 100}, 'P_12': {
    'X': 75, 'Y': 0}}
state.city_connections = {'C0': {'C1', 'C2'},
                          'C1': {'C0', 'C2'}, 'C2': {'C0', 'C1'}}
state.intermediate_point_connections = {'P_01': {'C0', 'C1'},
                                        'P_12': {'C1', 'C2'}}
state.packet_locations = {'P1': 'C0', 'P2': 'C0'}
state.truck_locations = {'T1': 'C1', 'T2': 'C0'}
state.driver_locations = {'D1': 'P_01', 'D2': 'C1'}
