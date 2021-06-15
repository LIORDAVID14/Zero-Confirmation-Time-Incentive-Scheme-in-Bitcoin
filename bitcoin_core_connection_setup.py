import configparser
from bitcoinrpc import connection

########################################################################################################
#Generating our bitcoind connection using bitcoind python JSON-RPC connection.
########################################################################################################

bitcoin_core_rpc_connection = None

def connect_to_node():
    config = configparser.ConfigParser()
    config.read('node_config.ini')

    username = config["server"]["username"]
    password = config["server"]["password"]
    hostip = config["server"]["hostip"]
    portnum = config["server"]["portnum"]

    global bitcoin_core_rpc_connection 
    bitcoin_core_rpc_connection = connection.BitcoinConnection(username,
                                                               password,
                                                               host=hostip,
                                                               port=portnum)
    assert (bitcoin_core_rpc_connection is not None)
    return bitcoin_core_rpc_connection


def get_connection():
    if bitcoin_core_rpc_connection is None:
        connect_to_node()
    return bitcoin_core_rpc_connection


if __name__ == "__main__":
    assert (bitcoin_core_rpc_connection is None)
    get_connection()
    assert (bitcoin_core_rpc_connection is not None)
    get_connection()
    assert (bitcoin_core_rpc_connection is not None)
