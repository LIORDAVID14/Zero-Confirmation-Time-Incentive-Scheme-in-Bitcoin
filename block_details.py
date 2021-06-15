from files_related_functions import get_params
import bitcoin_core_connection_setup
import tx_db
import sys

bitcoin_core_rpc_connection = bitcoin_core_connection_setup.get_connection()


def block_tx_list(block_num):
    block_hash = bitcoin_core_rpc_connection.getblockhash(int(block_num))
    block_data = bitcoin_core_rpc_connection.getblock(block_hash, verboseLevel=1)
    tx_id_list = block_data['tx']
    return tx_id_list


def block_summary(block_num):
    tx_id_list = block_tx_list(block_num)
    fees_sum = 0
    count = 0
    total = len(tx_id_list)
    for tx_id in tx_id_list:
        print (block_num, count, "/" , total, " ", tx_id)
        count = count + 1
        # print tx_id
        tx = tx_db.Transaction(tx_id)
        # print "finished creating obj"
        if tx.get_fees() is not None:
            fees_sum = fees_sum + tx.get_fees()

    return len(tx_id_list), fees_sum


if __name__ == "__main__":
    # params from user
    first_block, last_block = get_params(sys)

    # find relevant files
    blocks_range = range(int(first_block), int(last_block)+1)

    for current_block in blocks_range:
        # print current_block
        list_len, fees_sum = block_summary(current_block)
        print (current_block, list_len, fees_sum)
