import json
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time
from heapq import heappush, heappop
from math import inf

Recipe = namedtuple('Recipe', ['name', 'check', 'effect', 'cost'])


class State(OrderedDict):
    """ This class is a thin wrapper around an OrderedDict, which is simply a dictionary which keeps the order in
        which elements are added (for consistent key-value pair comparisons). Here, we have provided functionality
        for hashing, should you need to use a state as a key in another dictionary, e.g. distance[state] = 5. By
        default, dictionaries are not hashable. Additionally, when the state is converted to a string, it removes
        all items with quantity 0.
        Use of this state representation is optional, should you prefer another.
    """

    def __key(self):
        return tuple(self.items())

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.__key() < other.__key()

    def copy(self):
        new_state = State()
        new_state.update(self)
        return new_state

    def __str__(self):
        return str(dict(item for item in self.items() if item[1] > 0))


def make_checker(rule):
    # Implement a function that returns a function to determine whether a state meets a
    # rule's requirements. This code runs once, when the rules are constructed before
    # the search is attempted.

    def check(state):
         # This code is called by graph(state) and runs millions of times.
        # Tip: Do something with rule['Consumes'] and rule['Requires'].
        if 'Consumes' in rule:
            for object in rule['Consumes']:
                object_cost = rule['Consumes'][object]
                if state[object] < object_cost:
                    return False

        if 'Requires' in rule:
            for object in rule['Requires']:
                if state[object] <= 0:
                    return False
        return True

    return check


def make_effector(rule):
    # Implement a function that returns a function which transitions from state to
    # new_state given the rule. This code runs once, when the rules are constructed
    # before the search is attempted.

    def effect(state):
        # This code is called by graph(state) and runs millions of times
        # Tip: Do something with rule['Produces'] and rule['Consumes'].
        next_state = state.copy()

        if 'Produces' in rule:
            for object in rule['Produces']:
                next_state[object] += rule['Produces'][object]

        if 'Consumes' in rule:
            for object in rule['Consumes']:
                next_state[object] -= rule['Consumes'][object]

        return next_state

    return effect


def make_goal_checker(goal):
    # Implement a function that returns a function which checks if the state has
    # met the goal criteria. This code runs once, before the search is attempted.

    def is_goal(state):
        # This code is used in the search process and may be called millions of times.
        for object in goal:
            #print("object is ", object)
            if state[object] < goal[object]:
                return False
        return True

    return is_goal


def graph(state):
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.
    for r in all_recipes:
        if r.check(state):
            yield (r.name, r.effect(state), r.cost)


def heuristic(state):
    # Implement your heuristic here!
    tools = ['bench', 'wooden_pickaxe', 'wooden_axe', 'stone_axe', 'stone_pickaxe', 'iron_pickaxe', 'iron_axe','furnace']

    for tool in tools:
        if state[tool] > 1:
            return inf

    if state['iron_axe'] > 1:
        return inf
    elif state['stone_axe'] > 1:
        return inf
    elif state['wooden_axe'] > 1:
        return inf

    if state['iron_pickaxe'] > 1:
        return inf
    elif state['stone_pickaxe'] > 1:
        return inf
    #
    # if state['plank'] > 4:
    #     return inf
    #
    # if state['stick'] > 2:
    #     return inf
    #
    # if state['wood'] > 1:
    #     return inf
    #
    # if state['coal'] > 1:
    #     return inf
    #
    # if state['cobble'] > 8:
    #     return inf
    #
    # if state['ingot'] > 6:
    #     return inf
    #
    # if state['ore'] > 1:
    #     return inf
    #
    return 0

def create_path(came_from, current_state, path):
    path_object = came_from[current_state]
    while path_object[0]:
        path.insert(0, (path_object))
        path_object = came_from[path_object[0]]
    return path

def search(graph, state, is_goal, limit, heuristic):
    print("strt: ", state)
    start_time = time()
    path = []
    start = (0, state)
    open_set = [start]
    closed_set = []
    came_from = {}
    cost_so_far = {}
    came_from[state] = (None, None)
    cost_so_far[state] = 0
    
    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state
    while time() - start_time < limit and open_set:
        #print("open_set is: ", open_set)
        current_cost, current_state = heappop(open_set)
        if is_goal(current_state):
                path.append((current_state, came_from[current_state][1]))
                fin_path = create_path(came_from, current_state, path)
                print('cost ', cost_so_far[current_state])
                print('len ', len(fin_path))
                print(time()-start_time, 'seconds.')
                print("fin: ", fin_path)
                return fin_path
                    
        for neighbor in graph(current_state):
            #print("neighbor is: ", neighbor)
            new_cost = cost_so_far[current_state] + neighbor[2] + heuristic(current_state)
            #new_cost = current_cost + neighbor[2]
            if neighbor[1] not in cost_so_far or new_cost < cost_so_far[neighbor[1]]:
                cost_so_far[neighbor[1]] = new_cost
                entry = (new_cost, neighbor[1])
                open_set.append(entry)
                came_from[neighbor[1]] = (current_state, neighbor[0])
    # Failed to find a path
    print(time() - start_time, 'seconds.')
    print("Failed to find a path from", state, 'within time limit.')
    print("end_state: ", current_state)
    return None

if __name__ == '__main__':
    with open('Crafting.json') as f:
        Crafting = json.load(f)

    # # List of items that can be in your inventory:
    # print('All items:', Crafting['Items'])
    #
    # # List of items in your initial inventory with amounts:
    # print('Initial inventory:', Crafting['Initial'])
    #
    # # List of items needed to be in your inventory at the end of the plan:
    # print('Goal:',Crafting['Goal'])
    #
    # # Dict of crafting recipes (each is a dict):
    # print('Example recipe:','craft stone_pickaxe at bench ->',Crafting['Recipes']['craft stone_pickaxe at bench'])

    # Build rules
    all_recipes = []
    for name, rule in Crafting['Recipes'].items():
        checker = make_checker(rule)
        effector = make_effector(rule)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)

    # Create a function which checks for the goal
    is_goal = make_goal_checker(Crafting['Goal'])

    # Initialize first state from initial inventory
    state = State({key: 0 for key in Crafting['Items']})
    state.update(Crafting['Initial'])

    # Search for a solution
    resulting_plan = search(graph, state, is_goal, 30, heuristic)

    if resulting_plan:
        # Print resulting plan
        for state, action in resulting_plan:
            print('\t',state)
            print(action)
