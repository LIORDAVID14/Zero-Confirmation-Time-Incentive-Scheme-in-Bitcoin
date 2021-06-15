import networkx as nx
import random
import itertools

# from functools import lru_cache

max_set_size = 10


# Returns all the subsets of the set that it receives as "iterable" that their size is
# is smaller or equal to "size"
def get_subsets_smaller_than_size(iterable, size):
    s = list(iterable)
    return itertools.chain.from_iterable \
        (itertools.combinations(s, r) for \
         r in range(size + 1))


##########################################################################################
# Returns the set of the ancestors of a node "source" in the graph G.
def get_ancestor_set(G, source):
    s = nx.ancestors(G, source)
    s.add(source)
    return s


##########################################################################################
# Returns the sum of the fees of the objects in the set. The set contains only the id's
# and the fees are stored in the node's with the same id in the graph
def fee_of_set(G, set_of_obj):
    return sum([G.node[obj]['fee'] for obj in set_of_obj])


##########################################################################################
# Returns the sum of the size of the objects in the set. The set contains only the id's
# and the fees are stored in the node's with the same id in the graph
def size_of_set(G, set_of_obj):
    return sum([G.node[obj]['size'] for obj in set_of_obj])


##########################################################################################
# Returns a list of the complex sets. A complex set is a set after solving the dependencies.
def get_complex_sets(G):
    list_of_complex_sets = []
    for v in G:
        list_of_complex_sets.append(get_ancestor_set(G, v))
    return list_of_complex_sets


##########################################################################################
# Second version, faster. returns a list that contains tuples of the form :
# (ancestor(v), v, fee of ancestor set, size of ancestor set)
def get_complex_sets2(G):
    list_of_complex_sets = []
    for v in G:
        ancestor = get_ancestor_set(G, v)
        t = [ancestor, v, fee_of_set(G, ancestor), size_of_set(G, ancestor)]
        list_of_complex_sets.append(t)
    return list_of_complex_sets


##########################################################################################
# Returns the set with the best ratio of fee/size from the complex sets.
def get_max_ratio_set(G, list_of_complex_sets):
    ratio_list = [fee_of_set(G, x) / size_of_set(G, x) for x in list_of_complex_sets]
    return list_of_complex_sets[ratio_list.index(max(ratio_list))]


##########################################################################################
# Returns the set with the best ratio of fee/size from the complex sets. For the second
# version of tuples
def get_max_ratio_set2(G, list_of_complex_sets):
    ratio_list = [x[2] / x[3] for x in list_of_complex_sets]
    return list_of_complex_sets[ratio_list.index(max(ratio_list))]


##########################################################################################
# Returns the set with the smallest ratio of fee/size from the complex sets.
def get_min_ratio_set(G, list_of_complex_sets):
    ratio_list = [x[2] / x[3] for x in list_of_complex_sets]
    return list_of_complex_sets[ratio_list.index(min(ratio_list))]


##########################################################################################
# Updates complex list after putting something in the knapsack. 
def update_complex_list(list_of_complex_set, set_to_remove):
    list_of_complex_set.remove(set_to_remove)
    for s in list_of_complex_set:
        for x in set_to_remove:
            if x in s:
                s.remove(x)

    return [x for x in list_of_complex_set if len(x) != 0]


##########################################################################################
# Updates complex list after putting something in the knapsack. Second version
def update_complex_list2(list_of_complex_set, set_to_remove, G):
    list_of_complex_set.remove(set_to_remove)
    for s in list_of_complex_set:
        for x in set_to_remove[0]:
            if x in s[0]:
                s[0].remove(x)
                s[2] -= G.node[x]['fee']
                s[3] -= G.node[x]['size']
    return [x for x in list_of_complex_set if len(x[0]) != 0]


##########################################################################################
# Greedy solution of the dependencies knapsack problem. Receives a graph G which has the
# problem data and the block size. Returns a set of the items which the algorithm thinks
# must be included in the solution. The set includes only the ids.
# @lru_cache()
def get_set_greedy(G, block_size):
    list_of_complex_set = get_complex_sets(G)
    sol = set()
    list_of_complex_set = [s for s in list_of_complex_set if size_of_set(G, s) <= block_size]
    while len(list_of_complex_set) > 0:
        best_ratio_set = get_max_ratio_set(G, list_of_complex_set)
        if size_of_set(G, best_ratio_set) + size_of_set(G, sol) > block_size:
            if fee_of_set(G, best_ratio_set) > fee_of_set(G, sol):
                sol = best_ratio_set
            break
        else:
            for x in best_ratio_set:
                sol.add(x)
            # sol.update(best_ratio_set)
            list_of_complex_set = update_complex_list(list_of_complex_set, best_ratio_set)
    return sol


##########################################################################################
# Second version of the greedy approximation algorithm. Faster than the first one for 
# sparse graphs. Please use this one.
# @lru_cache()
def get_set_greedy2(G, block_size):
    list_of_complex_set = get_complex_sets2(G)
    sol = set()
    list_of_complex_set = [s for s in list_of_complex_set if s[3] <= block_size]
    while len(list_of_complex_set) > 0:
        best_ratio_tuple = get_max_ratio_set2(G, list_of_complex_set)
        if best_ratio_tuple[3] + size_of_set(G, sol) > block_size:
            if best_ratio_tuple[2] > fee_of_set(G, sol) and best_ratio_tuple[3] <= block_size:
                sol = best_ratio_tuple[0]
            break
        else:
            for x in best_ratio_tuple[0]:
                sol.add(x)
            # sol.update(best_ratio_set)
            list_of_complex_set = update_complex_list2(list_of_complex_set, best_ratio_tuple, G)
    return sol


##########################################################################################
# Returns the fee of the greedy solution. First version.
def get_fee_greedy(G, block_size):
    # get_set_greedy.cache_clear()
    return fee_of_set(G, get_set_greedy(G, block_size))


##########################################################################################
# Returns the fee of the greedy solution. Second version. Please use this
def get_fee_greedy2(G, block_size):
    # get_set_greedy2.cache_clear()
    return fee_of_set(G, get_set_greedy2(G, block_size))


##########################################################################################
# Returns the fee of the greedy solution. Second version. Please use this
def get_fees_and_txs(G, block_size):
    # get_set_greedy2.cache_clear()
    set_of_obj = get_set_greedy2(G, block_size)
    return fee_of_set(G, set_of_obj), set_of_obj


##########################################################################################
# incremental greedy solution of the dependencies knapsack problem. Receives a graph G which has the
# problem data, the block size and the previous solution. Returns a set of the items which the algorithm thinks
# must be included in the solution. The set includes only the ids.
# @lru_cache()
def get_set_greedy_inc(G, block_size, last_sol):
    skip_flag = False
    G_s = G.subgraph(list(last_sol))
    new_nodes = [x for x in list(G.nodes()) if x not in last_sol]
    G_new = G.subgraph(new_nodes)
    list_of_complex_sol = get_complex_sets2(G_s)
    min_ratio = get_min_ratio_set(G_s, list_of_complex_sol)
    list_of_added_complex_set = get_complex_sets2(G_new)
    list_of_added_complex_set = [s for s in list_of_added_complex_set if s[3] <= block_size]
    # list_of_added_complex_set = [s for s in list_of_complex_set if s not in list_of_complex_sol and s[3] <= block_size]
    max_ratio = get_max_ratio_set2(G, list_of_added_complex_set)
    max_ratio_value = fee_of_set(G, max_ratio[0]) / size_of_set(G, max_ratio[0])
    sol = set()
    if fee_of_set(G_s, min_ratio[0]) / size_of_set(G_s, min_ratio[0]) > max_ratio_value:
        sol = last_sol
        skip_flag = True
        list_of_complex_sol = set()

    A = list_of_complex_sol.copy()

    if not skip_flag:
        for s in A:
            if fee_of_set(G_s, s[0]) / size_of_set(G_s, s[0]) >= max_ratio_value:
                sol.update(s[0])
                list_of_complex_sol.remove(s)

    list_of_complex_union = list(list_of_complex_sol) + list_of_added_complex_set
    while len(list_of_complex_union) > 0:
        best_ratio_tuple = get_max_ratio_set2(G, list_of_complex_union)
        if best_ratio_tuple[3] + size_of_set(G, sol) > block_size:
            if best_ratio_tuple[2] > fee_of_set(G, sol) and best_ratio_tuple[3] <= block_size:
                sol = best_ratio_tuple[0]
            break
        else:
            for x in best_ratio_tuple[0]:
                sol.add(x)
            # sol.update(best_ratio_set)
            list_of_complex_union = update_complex_list2(list_of_complex_union, best_ratio_tuple, G)
    return sol


##########################################################################################
# Returns the fee of the incremental version of the greedy algorithm.
def get_fee_greedy_inc(G, block_size, last_sol):
    get_set_greedy_inc.cache_clear()
    return fee_of_set(G, get_set_greedy_inc(G, block_size, frozenset(last_sol)))


##########################################################################################
# Recudes the bigger_set to "max size" (defined at top). The rest of the elements are 
# moved to smaller_set. The reduction is done according to par.
def reduce_sets(smaller_set, bigger_set, par):
    if par == "relation":
        bigger_set = sorted(bigger_set, key=lambda node: (node[1]['fee']) / (node[1]['size']), reverse=True)
    elif par == "random":
        random.shuffle(bigger_set)
    elif par == "fee":
        bigger_set = sorted(bigger_set, key=lambda node: (node[1]['fee']), reverse=True)
    elif par == "size":
        bigger_set = sorted(bigger_set, key=lambda node: (node[1]['size']), reverse=False)
    for x in bigger_set[max_set_size:]:
        smaller_set.append(x)
    return bigger_set[:max_set_size]


##########################################################################################
# Returns the solution of (1+epsilon).
# @lru_cache()
def generalized_greedy(G, epsilon, block_size):
    skip_flag = False
    get_set_greedy2.cache_clear()
    sol_greedy = get_set_greedy2(G, block_size)
    greedy_value = fee_of_set(G, sol_greedy)
    a = epsilon * greedy_value
    elements = list(G.nodes.data())

    smaller_than_a = [e for e in elements if e[1]['fee'] < a]  # must be a list of ID
    greater_than_a = [e for e in elements if e[1]['fee'] >= a]

    if len(greater_than_a) == 0:
        return sol_greedy
    if len(greater_than_a) > max_set_size:
        greater_than_a = reduce_sets(smaller_than_a, greater_than_a, 'fee')

    smaller_than_a = [e[0] for e in smaller_than_a]  # must be a list of ID
    greater_than_a = [e[0] for e in greater_than_a]
    T = set()
    V_best = set()
    best = 0
    all_subsets = list(get_subsets_smaller_than_size(greater_than_a,
                                                     min(int(2 / epsilon), len(greater_than_a))))

    parsed_all_subsets = [set(subset) for subset in all_subsets]  # now every subset is a set

    # calculating ancestors
    ancestor = {}
    for v in G.nodes():
        ancestor[v] = get_ancestor_set(G, v)

    # beginning iteration for all subsets in VaC

    for J in parsed_all_subsets:

        if (len(J) == 0):
            continue

        if size_of_set(G, J) > block_size:
            continue

        T = J.copy()

        for v in J:
            ancestor_of_v = ancestor[v]
            for u in ancestor_of_v:
                if ((u in greater_than_a) and (u not in J)):
                    skip_flag = True
                    break
                if u in smaller_than_a:
                    T.add(u)

        if skip_flag:
            skip_flag = False
            continue

        if size_of_set(G, T) > block_size:
            continue

        B = set(smaller_than_a)
        B.difference_update(T)

        temp = set(greater_than_a)
        temp.difference_update(J)

        for u in smaller_than_a:
            ancestor_of_u = ancestor[u]
            if len(temp.intersection(ancestor_of_u)) > 0:
                B.remove(u)

        G_b = G.subgraph(list(B))

        sol_of_greedy = get_set_greedy2(G_b, block_size - size_of_set(G, T))

        fee_of_J = fee_of_set(G, T) + fee_of_set(G, sol_of_greedy)

        if fee_of_J > best:
            best = fee_of_J
            V_best = T.union(set(sol_of_greedy))

    return V_best


##########################################################################################
# Returns the solution value of (1+epsilon)
def get_fee_generalized_greedy(G, epsilon, block_size):
    generalized_greedy.cache_clear()
    return fee_of_set(G, generalized_greedy(G, epsilon, block_size))
