import json
from decimal import Decimal
import bitcoin_core_connection_setup
import key_generator
import os
import shutil
import subprocess
import time

########################################################################################################
#Operation function for checking if bitcoind.exe client is running in the background.
########################################################################################################
def process_exists(process_name):
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
    # use buildin check_output right away
    output = subprocess.check_output(call)
    # check in last line for process name
    last_line = output.strip().split('\r\n')[-1]
    # because Fail message could be translated
    return last_line.lower().startswith(process_name.lower())


########################################################################################################
#Transfer function num.1: creates a new transcation FROM A BLOCK (generatetoaddress) between a single person account to a destination. (A -> M)
########################################################################################################
def transaction_Single_To(source, destination, private_key, block_id, money_amount):
    block_struct = connection.getblock(block_id,2) #Using the block_id we will get the parameter for the transcation.
    txid_struct = block_struct.get("tx")
    txid_number = txid_struct[0].get("txid")
    vout_struct = txid_struct[0].get("vout")
    txid_scriptPubKey = vout_struct[0].get("scriptPubKey")
    scriptPubKey = txid_scriptPubKey.get("hex")
    ################### First step: Createrawtransaction ###################
    #From total 50 bitcoins: 25 to Destination, 24.95 to source, 0.05 fee.
    hash_for_sign = connection.createrawtransaction([{"txid": txid_number, "vout": 0}], {source:(money_amount/2)-0.05,destination:(money_amount/2)})
    signraw_inputs = [{"txid": txid_number, "vout": 0,"scriptPubKey": scriptPubKey}]
    ################### Second step: Signrawtransactionwithkey ###################
    signed = connection.signrawtransactionwithkey(hash_for_sign, private_key,signraw_inputs)
    hash_for_send = signed.get("hex")
    ################### Third step: Sendrawtransaction ###################
    result = connection.sendrawtransaction(hash_for_send)
    return result , signraw_inputs


########################################################################################################
#Transfer function num.2: creates a new transcation FROM BACKUP ACCOUNT (M) between a single person account to a destination. (A -> B)
########################################################################################################
def transaction_Single_To_Single(source, destination, private_key, txid_number, M_redeemScript, money_amount):
    ################### First step: Createrawtransaction ###################
    # From total 25 bitcoins: 12.5 to Destination, 12.4 to source, another 0.05 fee.
    hash_for_sign = connection.createrawtransaction([{"txid": txid_number, "vout": 1}], {A.address:12.40, destination:12.5})
    decoded_transaction = connection.decoderawtransaction(hash_for_sign);
    #There are 2 output in the transaction: 0:M. 1:B.
    B_vout = decoded_transaction.get("vout")[1] # Taking output 1 - getting the scriptPubKey for A -> B transaction.
    M_scriptPubKey = (B_vout.get("scriptPubKey")).get("hex")
    signraw_inputs = [{"txid": txid_number, "vout": 2,"scriptPubKey": M_scriptPubKey,"redeemScript": M_redeemScript}]
    ################### Second step: Signrawtransactionwithkey ###################
    signed = connection.signrawtransactionwithkey(hash_for_sign, private_key, signraw_inputs)
    result_signed = signed.get("complete")
    if  result_signed == False:
        return result_signed, signraw_inputs
    hash_for_send = signed.get("hex")
    ################### Third step: Sendrawtransaction ###################
    result_send = connection.sendrawtransaction(hash_for_send)
    return result_send, signraw_inputs


########################################################################################################
#Transfer function num.3: creates a new transcation between a multiSig account to a destination. (M -> B)
########################################################################################################
def transaction_Multi_To_Single(source, destination, private_keys, txid_number, M_redeemScript, money_amount):
    ################### First step: Createrawtransaction ###################
    # From total 25 bitcoins: 12.5 to Destination, 12.4 to source, another 0.05 fee.
    hash_for_sign = connection.createrawtransaction([{"txid": txid_number, "vout": 0}], {A.address:12.40, destination:12.5})
    decoded_transaction = connection.decoderawtransaction(hash_for_sign);
    #There are 2 output in the transaction: 0:M. 1:B.
    B_vout = decoded_transaction.get("vout")[1] # Taking output 1 - getting the scriptPubKey for M -> B transaction.
    M_scriptPubKey = (B_vout.get("scriptPubKey")).get("hex")
    signraw_inputs = [{"txid": txid_number, "vout": 2,"scriptPubKey": M_scriptPubKey,"redeemScript": M_redeemScript}]
    ################### Second step: Signrawtransactionwithkey ###################
    signed = connection.signrawtransactionwithkey(hash_for_sign, private_keys, signraw_inputs)
    result_signed = signed.get("complete")
    if  result_signed == False:
        return result_signed, signraw_inputs
    hash_for_send = signed.get("hex")
    ################### Third step: Sendrawtransaction ###################
    result_send = connection.sendrawtransaction(hash_for_send)
    return result_send, signraw_inputs


#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
#Main:
    #Our main files are (decreasing priority):
    #main_bitcoin.py.
    #connection.py.
    #key_generator.py.
    #bitcoin_core_connection_setup.py.
    #proxy.py.
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################


########################################################################################################
#Intialize system:
    #Finds bitcoind.exe on system processes and kills it.
    #Removes the regtest folder - we do not want any previous transactions - A fresh start.
    #Opens the bitcoind.exe again.
########################################################################################################
if process_exists('bitcoind.exe'):
    os.system('TASKKILL /F /IM bitcoind.exe')
time.sleep(3)
myPath = "C:\\Users\\LIORD\\AppData\\Roaming\\Bitcoin\\regtest"
if os.path.exists(myPath):
    shutil.rmtree(myPath)
subprocess.Popen(["C:\\Program Files\\Bitcoin\\daemon\\bitcoind.exe", "-regtest","-deprecatedrpc=generate"])
time.sleep(7)


########################################################################################################
#Generates a key for every account on our system:
    #We are working under regtest mode, Therefore we need to create addresses and keys according these instructions:
    #For creating an address: Adding b"\x6f": b"\x6f" + hash160.
    #For creating a full key: Adding 'EF': 'EF' + binascii.hexlify(priv_key).decode().
    #For creating a public key: Adding '04': '04' + binascii.hexlify(vk.to_string()).decode().
########################################################################################################
A = key_generator.Person() #A is the buyer.
A.key_generator_func()
B = key_generator.Person() #B is the seller.
B.key_generator_func()
M = key_generator.Person() #M is the middle-man.
M.key_generator_func()


########################################################################################################
#Generating our bitcoind connection using bitcoind python JSON-RPC connection.
########################################################################################################
connection = bitcoin_core_connection_setup.connect_to_node()

################### Initializing fee for every transaction ###################
fee_transaction = 0.05  # We decided to take 0.05 bitcoins fee from the transaction.

########################################################################################################
#Generates blocks for each of A and D, and the enviroment:
########################################################################################################
block1_struct = connection.generatetoaddress(1,A.address) #Generates BLOCK 1 to A address.
block1_id = block1_struct[0] #BLOCK 1 id.
generate_enviroment = connection.generate(100) #Generates BLOCKS 2 - 101 to the blockchain - only then block1_struct will enter the blockchain.

#If we want to check block information:
# block_struct_A_to_B = connection.getblock(block1_id,2)

########################################################################################################
#Generates the addresses for the multisig - the M account:
########################################################################################################
M_public_keys=[] #We are building a multisig account using both A and M key.
M_public_keys.append(A.public_key)
M_public_keys.append(M.public_key)
M_PrivateKeys=[] #We need both A and M keys for A -> B OR M -> B transactions in the payment simulation.
M_PrivateKeys.append(A.private_key)
M_PrivateKeys.append(M.private_key)
A_privateKey = [] #We need A key's for signing A -> M transaction. also for A -> B in the payment simulation.
A_privateKey.append(A.private_key)

#If we want to check blockchain information:
# mining_info = connection.getmininginfo()


########################################################################################################
#Generates the multisig (M account) address and redeemScript for next transactions:
########################################################################################################
M_block_struct = connection.addmultisigaddress(2, M_public_keys) #Creates ,multisig address from A and M => M multisig.
M_Multisig_Address = M_block_struct.get("address") #Getting M multisig address.
M_redeemScript = M_block_struct.get("redeemScript") #Getting M redeemScript.


########################################################################################################
#In the past: A -> M, cause there's a need to be a backup money for the A -> B transaction in the future.
#A transfer 25 bitcoins to M, A gets back his 24.95 bitcoin, and the fee is 0.05 bitcoins.
########################################################################################################
M_input = transaction_Single_To(A.address, M_Multisig_Address, A_privateKey, block1_id, 50) #Transaction A -> M. We will use vout:1 for next trascation as an input.
mempool_1 = connection.getrawmempool(True) #Using the mempool we will take the A-> M txid transaction and use it for A -> B OR M -> B transaction.
M_txid = mempool_1.keys()[0] #The txid of A -> M transaction.
generate_enviroment = connection.generate(100) #Generates BLOCKS to the blockchain - only then M_txid will enter the blockchain.


########################################################################################################
#There are 25 bitcoins in M multisig account.
#A needs to pay 12.5 bitcoins to B.
#B gets his 12.5 bitcoins for the item, A gets back 12.45 bitcoins, and the transaction fee is 0.05 bitcoins.
########################################################################################################

########################################################################################################
#There are 2 scenarios:
    #THE GOOD CASE:
    #FLAG 1: A -> B. A did his part in the purchase and therefore there is no need for M to send the money again to B.
    #THE BAD CASE:
    #FLAG 2: M -> B. A didn't do his part in the purchase and therefore M comes in to action and transfer the backup money to B.

#Third scenario:
    #M is waiting for A to make the A -> B transaction. after a timeout and A did NOT send to money to B: the M -> B transaction will happen.
########################################################################################################

#Choose your simulation:
flag = 1

#THE GOOD CASE:
if flag == 1: #A -> B, (BUT NOT M -> B), because we use the same input(A->M output) for both transactions.
    result_A_B_transaction, send_A_to_B = transaction_Single_To_Single(A.address, B.address, A_privateKey, M_txid, M_redeemScript, 25)   # Transaction A -> B. Should success.
    generate_enviroment = connection.generate(100)  # Waiting for the M -> B transaction to be valid in the blockchain.
    result_M_B_transaction, send_M_to_B = transaction_Multi_To_Single(M_Multisig_Address, B.address, M_PrivateKeys, M_txid, M_redeemScript, 25)  # Transaction M -> B. Should fail.
    generate_enviroment = connection.generate(100) #Waiting for the M -> B transaction to be valid in the blockchain.
    if result_M_B_transaction == False: #Validation check.
        print("The transaction from A -> B succeeded")
        print("The transaction from M -> B could not pass")
    mempool_2 = connection.getrawmempool(True) #Using the mempool we are checking the A -> B transaction.

#THE BAD CASE:
elif flag == 2: #M -> B, (BUT NOT A -> B), because we use the same input(A->M output) for both transactions.
    result_M_B_transaction, send_M_to_B = transaction_Multi_To_Single(M_Multisig_Address, B.address, M_PrivateKeys, M_txid, M_redeemScript, 25)  # Transaction M -> B. Should Success.
    generate_enviroment = connection.generate(100) #Waiting for the M -> B transaction to be valid in the blockchain.
    result_A_B_transaction, send_A_to_B = transaction_Single_To_Single(A.address, B.address, A_privateKey, M_txid, M_redeemScript, 25)   # Transaction A -> B. Should fail.
    generate_enviroment = connection.generate(100)  # Waiting for the M -> B transaction to be valid in the blockchain.
    if result_A_B_transaction == False: #Validation check.
        print("The transaction from M -> B succeeded")
        print("The transaction from A -> B could not pass")
    mempool_3 = connection.getrawmempool(True) #Using the mempool we are checking the M -> B transaction.

#TIME SIMULATION M -> B (BAD CASE):
elif flag == 3: #M is waiting for A to make the A -> B transaction. after a timeout and A did NOT send to money to B: the M -> B transaction will happen.
    ################### Start waiting: BLOCK NUMBER 201 ###################
    start_block_number = connection.getblocknumber() #Checking the current number of blocks in the blockchain - BLOCK NUMBER 201.
    current_block_number = start_block_number #Initilazing parameter for while.
    wait_time = 500; #We want to wait at least 500 new blocks before we will make the M -> B transaction.
    while(current_block_number - start_block_number < wait_time):
        generate_enviroment = connection.generate(100)  # Waiting for the M -> B transaction to be valid in the blockchain.
        current_block_number = connection.getblocknumber() #Checking the current number of blocks in the blockchain - BLOCK NUMBER 201.
        print("Current block number: " , current_block_number)
    result_M_B_transaction, send_M_to_B = transaction_Multi_To_Single(M_Multisig_Address, B.address, M_PrivateKeys, M_txid, M_redeemScript, 25)  # Transaction M -> B. Should Success.
    generate_enviroment = connection.generate(100) #Waiting for the M -> B transaction to be valid in the blockchain.
    if result_M_B_transaction == True: #Validation check.
        print("After a time-out, trying to send M -> B transaction")
        print("The transaction from M -> B succeeded")
    mempool_4 = connection.getrawmempool(True) #Using the mempool we are checking the M -> B transaction.



########################################################################################################
#End of main.
########################################################################################################