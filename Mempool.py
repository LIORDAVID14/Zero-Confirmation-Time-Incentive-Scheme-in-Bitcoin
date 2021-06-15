'''
Created on 16/08/2017

@author: Itay
'''

# more information about fields of mempool is available @
# https://bitcoin.org/en/developer-reference#getrawmempool

import sys
import os as os
import tarfile
from decimal import *
import operator



max_block_size = 1000000


def fees_available_from_tx_list(tx_list):
  tx_counter = 0
  accumulated_fees = 0
  accumulated_size = 0
  
  for current_tx in tx_list:
    size = current_tx[1]['size']
    new_size = accumulated_size + size
    if new_size <= max_block_size:
      accumulated_fees = accumulated_fees + current_tx[1]['modifiedfee']
      accumulated_size = new_size
      tx_counter = tx_counter + 1
    else:
      #print "stopping. old size = ",accumulated_size,"added size =",size
      break
      
  return tx_counter, accumulated_fees, accumulated_size



def add_to_dict_of_sets(dictname,key,val):
  if key not in dictname or dictname[key] is None:
    dictname[key] = set()
  dictname[key].add(val)



def verify_dependencies(sorted_tx_list):
  tx_set = set()
  
  for tx_item in sorted_tx_list:
    tx_id = tx_item[0]
    dependecy_set = set(tx_item[1]['depends'])
    assert (dependecy_set.issubset(tx_set))
    tx_set.add(tx_id)



def compare_dependencies(sorted_tx_list,sorted_tx_list_unsettled_dependencies):
  n = len(sorted_tx_list)
  assert (n == len(sorted_tx_list_unsettled_dependencies))
  i = 0
  while i < n:
    if sorted_tx_list[i][0] != sorted_tx_list_unsettled_dependencies[i][0]:
      break
    i = i + 1



def get_fees_size_ratio(tx_dict):
  # this function is only suited for transactions of "getrawmempool", where "size" is actually the virtual size. go figure.
  value = tx_dict[1]
  return value['modifiedfee']/value['size']

class Mempool:


    def add_tx(self,txid, txdata):
      assert (txid not in self.txs_dict.keys())
      self.txs_dict[txid]=txdata


    def read_dict_from_file(self):
		with open(self.untarred_file_path, 'r') as myfile:
			data=myfile.read()
			self.txs_dict = eval(data)


    def create_untarred_file(self):
		dir_path = os.path.dirname(os.path.realpath(self.file_path))
		tar = tarfile.open(self.file_path)
		tar.extractall(path=dir_path)
		tar.close()    
   
 
    def list_all_numbers_of_dependency(self):
		values_list = [i['ancestorcount'] for i in self.txs_dict.values()]
		values_set = set(values_list)
		return values_set

    def get_tx_number(self,filtered_list):
		tx_number = len(filtered_list)
		return tx_number

    def get_total_fees(self,filtered_list):
		total_fees = sum(i['modifiedfee'] for i in filtered_list)
		return total_fees

    def get_total_sizes(self,filtered_list):
		total_sizes = sum(i['size'] for i in filtered_list)
		return total_sizes

    def get_total_ancestor_fees(self,filtered_list):
		total_fees = sum(i['ancestorfees'] for i in filtered_list)
		return total_fees

    def get_total_ancestor_sizes(self,filtered_list):
		total_fees = sum(i['ancestorsize'] for i in filtered_list)
		return total_fees
   
    def get_stats_dict(self):
		values_set = self.list_all_numbers_of_dependency()
		stats_dict = {}
		for value in values_set:
			single_stats_dict = {}
			filtered_list = filter(lambda x: x['ancestorcount']==value, self.txs_dict.values())
			single_stats_dict['number_of_txs'] = self.get_tx_number(filtered_list)
			single_stats_dict['total_fees'] = self.get_total_fees(filtered_list)
			single_stats_dict['total_sizes'] = self.get_total_sizes(filtered_list)
			stats_dict[value] = single_stats_dict
		return stats_dict        



    def mark_dependency(self,current_tx_id,unaccounted_for_dependency_tx_ids_set):
      for current_dependent_tx_id in unaccounted_for_dependency_tx_ids_set:
        add_to_dict_of_sets(self.values_depend_on_key_dict,current_dependent_tx_id,current_tx_id)
        add_to_dict_of_sets(self.key_depends_on_values_dict,current_tx_id,current_dependent_tx_id)

        
    def handle_dependent_tx(self,current_tx_item):
      current_tx_id = current_tx_item[0]
      unaccounted_for_dependency_tx_ids_set = self.current_dependency_set - self.covered_transaction_ids_set
      self.mark_dependency(current_tx_id,unaccounted_for_dependency_tx_ids_set)
      self.awaiting_transactions_list.append(current_tx_item)
    
    def are_there_no_waiting_txs_dependent_on_input_tx(self,current_tx_id):
      return current_tx_id not in self.values_depend_on_key_dict or self.values_depend_on_key_dict[current_tx_id] is None

    def add_transaction_to_final_list(self,current_tx_item):
      self.setteled_sorted_tx_list.append(current_tx_item)
      self.covered_transaction_ids_set.add(current_tx_item[0])

    def clear_dependencies(self,current_tx_id):
      is_a_dependency_completely_cleared = False
      check1 = False
      check2 = False
      if current_tx_id in self.values_depend_on_key_dict:
        for current_dependent_tx_id in self.values_depend_on_key_dict[current_tx_id]:
          self.key_depends_on_values_dict[current_dependent_tx_id].remove(current_tx_id)
          if (len(self.key_depends_on_values_dict[current_dependent_tx_id]) == 0):
            is_a_dependency_completely_cleared = True
      else:
        check1 = True
      if current_tx_id in self.values_depend_on_key_dict:
        self.values_depend_on_key_dict[current_tx_id].clear()
        self.values_depend_on_key_dict[current_tx_id] = None
      else:
        check2 = True
      return is_a_dependency_completely_cleared or (check1 and check2)
	
 
    def find_new_independent_tx(self):
      tx_to_add = None
      # iterate forward while allowing deletion of items
      i = 0
      n = len(self.awaiting_transactions_list)
      while i < n:
      	current_attempt_tx = self.awaiting_transactions_list[i]
      	current_attempt_tx_id = current_attempt_tx[0]
      	if len(self.key_depends_on_values_dict[current_attempt_tx_id]) == 0:
      		tx_to_add = self.awaiting_transactions_list[i]
      		del self.awaiting_transactions_list[i]
      		n = n - 1
      		break
      	else:
      		i = i + 1
      return tx_to_add


    def handle_independent_tx(self,current_tx_item):
      # add the transaction
      self.add_transaction_to_final_list(current_tx_item)
  	
      # check if any dependencies were updated
      current_tx_id = current_tx_item[0]

      # remove dependecies, check if an update is available
      tx_becomes_independent_flag = self.clear_dependencies(current_tx_id)
      
      
      if tx_becomes_independent_flag:
      	tx_to_add = self.find_new_independent_tx()
      	if tx_to_add is not None:
      		self.handle_independent_tx(tx_to_add)

  	
  	# HERE
    def settle_dependencies(self,sorted_tx_list_unsettled_dependencies):
      self.values_depend_on_key_dict = {}
      self.key_depends_on_values_dict = {}
      
      self.covered_transaction_ids_set = set()
      self.awaiting_transactions_list = []
      self.setteled_sorted_tx_list = []
      
      for current_tx_item in sorted_tx_list_unsettled_dependencies:
      	self.current_dependency_list = current_tx_item[1]['depends']
      	self.current_dependency_set = set(self.current_dependency_list)
      

      	if self.current_dependency_set.issubset(self.covered_transaction_ids_set):
          self.handle_independent_tx(current_tx_item)
      	else:
          self.handle_dependent_tx(current_tx_item)
      
      assert (len(self.awaiting_transactions_list) == 0)
      return self.setteled_sorted_tx_list	
  	
    def get_sorted_txs(self):
      sorted_tx_list_unsettled_dependencies = sorted(self.txs_dict.items(), key=lambda x: get_fees_size_ratio(x),reverse=True)
      return sorted_tx_list_unsettled_dependencies
      
    def get_time_stamp_and_block_count(self):
      return self.time_stamp,self.block_count
  

    def set_time_stamp_and_block_count(self):
      filename, file_extension = os.path.splitext(self.untarred_file_path)           
      basename = os.path.basename(filename)
      split_basename = basename.split("_")
      
      if (len(split_basename) == 7):
        self.block_count = split_basename[0]
        first_index = len(self.block_count)+1
        self.time_stamp = basename[first_index:]
      elif (len(split_basename) == 8):  
        assert (split_basename[0] == split_basename[1])
        self.block_count = split_basename[0]
        first_index = (len(self.block_count)+1)*2
        self.time_stamp = basename[first_index:]
      else:
        print len(split_basename)
        assert (False)

    def parse_file(self):
  		self.create_untarred_file()
  		self.read_dict_from_file()
  		#os.remove(untarred_file_path)

    def get_results(self):
      sorted_tx_list_unsettled_dependencies = self.get_sorted_txs()
      sorted_tx_list = self.settle_dependencies(sorted_tx_list_unsettled_dependencies)      
      return fees_available_from_tx_list(sorted_tx_list_unsettled_dependencies),fees_available_from_tx_list(sorted_tx_list)


    def get_tx_list(self):
      return  self.txs_dict.keys()

    def __init__(self, file_path):
  		self.file_path = file_path
  		self.untarred_file_path = file_path.replace(".tar.gz","")


  		self.time_stamp = ""
  		self.block_count = 0
  		self.set_time_stamp_and_block_count()
  
  		# self.txs_dict = {} 
  		self.parse_file()


    def print_dict(self):
  		for key,value in self.txs_dict.items():
  			print key,value,"\n"

    def __enter__(self):
      return self
    
    def __exit__(self, exc_type, exc_value, traceback):
      pass


if __name__== "__main__":

  assert (len(sys.argv)==2) , "please provide tar.gz file path"
  file_path = sys.argv[1]
  with Mempool(file_path) as currMempool:
    stats_dict = currMempool.get_stats_dict()
    #print stats_dict
    #print currMempool.get_time_stamp_and_block_count()
    currMempool.print_dict()
    
    sorted_tx_list_unsettled_dependencies = currMempool.get_sorted_txs()
    sorted_tx_list = currMempool.settle_dependencies(sorted_tx_list_unsettled_dependencies)
      
    #verify_dependencies(sorted_tx_list)
    #compare_dependencies(sorted_tx_list,sorted_tx_list_unsettled_dependencies)

        
        