import networkx as nx
import tx_db


def create_graph(transaction_list):
    # mem_pool is a list that contains elements of the type:
    # (id,[ancestors_id],fee,size)
    graph = nx.DiGraph()
    for current_transaction in transaction_list:
        assert (not current_transaction.get_is_coin_base())
        graph.add_node(current_transaction.get_txid(), fee=float(current_transaction.get_fees()),
                       size=int(current_transaction.get_weight()))

    for current_transaction in transaction_list:
        for ancestor_id in current_transaction.get_total_in_block_ancestors():
            assert (ancestor_id in graph.nodes()), ancestor_id
            graph.add_edge(ancestor_id, current_transaction.get_txid())
    return graph
