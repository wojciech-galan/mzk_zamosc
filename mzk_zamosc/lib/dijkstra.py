import math
from typing import Dict
from typing import Set

vertices_ = {
    'a':{
        'b':3,
        'c':4,
        'e':6
    },
    'b':{
        'd':2
    },
    'c':{
        'd':3,
        'e':1
    }
}


def get_vertices_names(vertices:Dict[str, Dict[str, int]]) ->Set[str]:
    ret_set = set(vertices)
    for distances in vertices.values():
        ret_set.update(distances)
    return ret_set


def construct_path(predescessors:Dict[str, str], initial_vertix:str, final_vertix:str):
    ret_list = []
    curr = final_vertix
    while curr != initial_vertix:
        ret_list.append(curr)
        curr = predescessors[curr]
    ret_list.append(initial_vertix)
    return list(reversed(ret_list))


def dijkstra(vertices:Dict[str, Dict[str, int]], initial_vertix:str, final_vertix:str):
    vertices_names = get_vertices_names(vertices)
    distances_from_beginning = {x:math.inf for x in vertices_names}
    distances_from_beginning[initial_vertix] = 0
    predecessors = {}
    while distances_from_beginning:
        minimum = min(distances_from_beginning.items(), key=lambda x: x[1])[0]
        if minimum == final_vertix:
            print(predecessors)
            return construct_path(predecessors, initial_vertix, final_vertix)
        elif minimum not in vertices: # nie ma go wśród wierzchołków rozpoczynających krawędź, nie może więc prowadzić do końcowego
            pass
        else:
            for v, dist in vertices[minimum].items():
                print(f'{minimum}, {v}, {dist} {distances_from_beginning}')
                if distances_from_beginning[v] > distances_from_beginning[minimum]+dist:
                    distances_from_beginning[v] = distances_from_beginning[minimum]+dist
                    predecessors[v] = minimum
        del distances_from_beginning[minimum]
    print(predecessors)
    return construct_path(predecessors, initial_vertix, final_vertix)


if __name__ == '__main__':
    print(dijkstra(vertices_, 'a', 'e'))
    print(dijkstra(vertices_, 'a', 'd'))
    print(dijkstra(vertices_, 'b', 'e'))