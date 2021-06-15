'''
Created on 19 July 2017

@author: Itay
'''

import platform
import time
import os
import errno
from bitcoinrpc import connection
import operator
from bitcoinrpc.exceptions import _wrap_exception
import tarfile
import os.path
import shutil
import traceback
import configparser
import sys
from files_related_functions import *
from analyze_samples import Logger
import networkx as nx
import createGraph
from dependency_knapsack_solvers import *
from multiprocessing import Pool

block_fees_output_dir_path = None
block_txs_output_dir_path = None
logged_mempool_samples_dir_path = None


def is_coinbase_tx(current_tx):
  return (len(current_tx['vin']) == 1) and ('coinbase' in current_tx['vin'][0]) and ('txid' not in current_tx['vin'][0])

def input_amount(bitcoinCoreConnection,current_vin):
  if 'txid' not in current_vin: # might be a coinbase tx with no fees
    return 0
  else:
    previous_tx_id = current_vin['txid']
    previous_vout_index = current_vin['vout']
    input_tx_data = bitcoinCoreConnection.getrawtransaction(previous_tx_id,verbose=True)
    return input_tx_data['vout'][previous_vout_index]['value']

def block_of_tx_id(bitcoinCoreConnection,tx_id):
    tx_block_hash = bitcoinCoreConnection.getrawtransaction(tx_id,verbose=True)["blockhash"]
    assert (tx_block_hash is not None)
    tx_block_num = bitcoinCoreConnection.getblock(tx_block_hash,verboseLevel=1)["height"]
    assert (tx_block_num is not None)
    return tx_block_num

def get_tx_fees(current_tx):
    # tx inputs
    vin_list = current_tx['vin']
    inputs_sum = sum([input_amount(bitcoinCoreConnection,x) for x in vin_list])

    # tx outputs
    vout_list = current_tx['vout']
    outputs_sum = sum([x['value'] for x in vout_list])
    
    # diff
    tx_fees = inputs_sum - outputs_sum
    assert(tx_fees >= 0)
    return tx_fees


def get_tx_mempool_ancestors(tx_id,current_block):
    ancestor_tx_id_list = []
    #print "\n\nSTART OF get_tx_mempool_ancestors\n\n"
    vin_list = bitcoinCoreConnection.getrawtransaction(tx_id,verbose=True)['vin']
    input_tx_id_list = [current_vin['txid'] for current_vin in vin_list if 'txid' in current_vin]
    
    for current_input_tx_id in input_tx_id_list:
      #print current_input_tx_id
      tx_block = block_of_tx_id(bitcoinCoreConnection,current_input_tx_id)
      assert (int(tx_block) <= int(current_block))

      if int(tx_block) == int(current_block):
        ancestor_tx_id_list.append(current_input_tx_id)
        ancestor_tx_id_list.extend(get_tx_mempool_ancestors(current_input_tx_id,current_block))
    
    return ancestor_tx_id_list

def get_tx_size(current_tx):
    size = current_tx['size']
    assert(size > 0)
    return size
    
def handle_one_block(bitcoinCoreConnection,block_num):
  block_hash = bitcoinCoreConnection.getblockhash(block_num)
  block_data = bitcoinCoreConnection.getblock(block_hash,verboseLevel=2)
  time = block_data['time']
  tx_list = block_data['tx'] 

  total_fees = 0
  for current_tx in tx_list:
    #coinbase tx's don'y pay fees
    if (is_coinbase_tx(current_tx)):
      continue

    tx_fees = get_tx_fees(current_tx)
    #print current_tx['txid'],tx_fees
    total_fees = total_fees + tx_fees

  return total_fees,time



def handle_one_speculative_block(bitcoinCoreConnection,block_num):
  with Logger(logged_mempool_samples_dir_path, None,block_num,block_num) as logger:
    files_list = logger.find_files()
    relevant_sample_path=files_list[-1]
    curr_mempool, time_stamp, block_count = logger.mempool_from_file(relevant_sample_path)  
  

    block_hash = bitcoinCoreConnection.getblockhash(block_num)
    block_data = bitcoinCoreConnection.getblock(block_hash,verboseLevel=2)
    time = block_data['time']
    block_tx_list = block_data['tx'] 

    block_tx_dict = {}
    for current_tx in block_tx_list:
      if not is_coinbase_tx(current_tx):
        block_tx_dict[current_tx["txid"]]=current_tx

    mempool_tx_set = set(curr_mempool.get_tx_list())
    block_tx_set = set(block_tx_dict.keys())

    set_diff = block_tx_set.difference(mempool_tx_set)

    for tx_id in set_diff:
      current_tx = block_tx_dict[tx_id]
      tx_fees = get_tx_fees(current_tx)
      tx_size = get_tx_size(current_tx)
      ancestor_list = get_tx_mempool_ancestors(tx_id,block_num)
      ancestor_set = set(ancestor_list)
      
      #print "Dependencies for",tx_id
      
      
      current_txdata = {'modifiedfee' : tx_fees, 'size' : tx_size, 'depends' : ancestor_list}
      curr_mempool.add_tx(tx_id,current_txdata)

    graph = createGraph.create_graph(curr_mempool)
    
    fees = get_fee_greedy2(graph,1000000)
    
    return fees,time




def txs_in_block(bitcoinCoreConnection,block_num):
  block_hash = bitcoinCoreConnection.getblockhash(block_num)
  block_data = bitcoinCoreConnection.getblock(block_hash,verboseLevel=2)
  time = block_data['time']
  tx_list = block_data['tx'] 
  
  included_tx_list = []
  for current_tx in tx_list:
    #coinbase tx's don'y pay fees
    if (is_coinbase_tx(current_tx)):
      continue

    # tx hash
    current_tx_hash = current_tx['hash']
    size = get_tx_size(current_tx)
    fees = get_tx_fees(current_tx)
    tx_tuple = [current_tx_hash,size,fees, float(fees) / float(size)]
    included_tx_list.append(tx_tuple)

  return included_tx_list


def create_block_summary_file(output_file_path, bitcoinCoreConnection,block_num):
  total_fees,time = handle_one_block(bitcoinCoreConnection,block_num)
  mkdir_p(os.path.dirname(output_file_path))
  fh = open(output_file_path, 'w+')
  lines_list = []
  line_to_write = str(total_fees) + " " + str(time) + "\n"
  lines_list.append(line_to_write)
  fh.writelines(lines_list) 
  fh.close()



def create_block_txs_file(output_file_path, bitcoinCoreConnection,block_num):
  tx_list = txs_in_block(bitcoinCoreConnection,block_num)
  mkdir_p(os.path.dirname(output_file_path))
  fh = open(output_file_path, 'w+')
  lines_list = []

  for current_item in tx_list:
    current_tx = current_item[0]
    size = current_item[1]
    fees = current_item[2]
    ratio = "%.20f" % current_item[3]
    line_to_write = str(current_tx) + "," + str(size) + "," + str(fees) + "," + str(ratio) + "\n"
    lines_list.append(line_to_write)
  fh.writelines(lines_list) 
  fh.close()


def create_speculative_fees_file(output_file_path, bitcoinCoreConnection,block_num):
  total_fees,time = handle_one_speculative_block(bitcoinCoreConnection,block_num)
  mkdir_p(os.path.dirname(output_file_path))
  fh = open(output_file_path, 'w+')
  lines_list = []
  line_to_write = str(total_fees) + " " + str(time) + "\n"
  lines_list.append(line_to_write)
  fh.writelines(lines_list) 
  fh.close()

def handle_block_list(bitcoinCoreConnection,blocks_range):
  for block_num in blocks_range:
    output_file_path = get_output_file_path(output_dir_path=block_fees_output_dir_path,time_stamp=None, block_count=block_num, suffix="_fees_reward.log")
    function_to_create_file = lambda : create_block_summary_file(output_file_path, bitcoinCoreConnection,block_num)
    create_file(output_file_path,function_to_create_file)

    output_file_path = get_output_file_path(output_dir_path=block_fees_output_dir_path,time_stamp=None, block_count=block_num, suffix="_txs.log")
    function_to_create_file = lambda : create_block_txs_file(output_file_path, bitcoinCoreConnection,block_num)
    create_file(output_file_path,function_to_create_file)

    output_file_path = get_output_file_path(output_dir_path=block_fees_output_dir_path,time_stamp=None, block_count=block_num, suffix="_speculative_fees.log")
    function_to_create_file = lambda : create_speculative_fees_file(output_file_path, bitcoinCoreConnection,block_num)
    create_file(output_file_path,function_to_create_file)



def connect_to_node(config):
  username = config["server"]["username"]
  password = config["server"]["password"]
  hostip = config["server"]["hostip"]
  portnum = config["server"]["portnum"]

  bitcoinCoreConnection = connection.BitcoinConnection(username,
                                                password,
                                                host=hostip,
                                                port=portnum)
  return bitcoinCoreConnection


def filter_by_block_number_and_suffix(first_block,last_block,suffix):
  return lambda x : block_in_range_and_suffix(x,first_block,last_block,suffix)


if __name__== "__main__":

  # params from user
  first_block,last_block = get_params(sys)



  # read config
  config = configparser.ConfigParser()
  config.read('sampler_config.ini')
  block_fees_output_dir_path = config["paths"]["block_fees_output_dir_path"]
  block_txs_output_dir_path = config["paths"]["block_txs_output_dir_path"]
  logged_mempool_samples_dir_path = config["paths"]["logged_mempool_samples_dir_path"]
  
  # find relevant files
  blocks_range = range(int(first_block),int(last_block)+1)

  bitcoinCoreConnection = connect_to_node(config)

  handle_block_list(bitcoinCoreConnection,blocks_range)



  





