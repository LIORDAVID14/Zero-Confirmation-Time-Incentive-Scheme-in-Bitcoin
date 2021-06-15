# Copyright (c) 2010 Witchspace <witchspace81@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
Connect to Bitcoin server via JSON-RPC.
"""
import sys
from bitcoinrpc.proxy import JSONRPCException, AuthServiceProxy
from bitcoinrpc.exceptions import _wrap_exception, WalletPassphraseIncorrect, WalletAlreadyUnlocked
from bitcoinrpc.data import (ServerInfo, AccountInfo, AddressInfo, TransactionInfo,
                             AddressValidation, WorkItem, MiningInfo)

########################################################################################################
########################################################################################################
#The bitcoin RPC (Python 2.7):
    #Importent notes:
    #Working functions:
        #Getrawmempool.
        #Getblock.
        #Decoderawtransaction.
    #NOT Working functions:
        #Unspentlist.
        #Wallet functions.
########################################################################################################
########################################################################################################

class BitcoinConnection(object):
    """
    A BitcoinConnection object defines a connection to a bitcoin server.
    It is a thin wrapper around a JSON-RPC API connection.

    Up-to-date for SVN revision 198.

    Arguments to constructor:

    - *user* -- Authenticate as user.
    - *password* -- Authentication password.
    - *host* -- Bitcoin JSON-RPC host.
    - *port* -- Bitcoin JSON-RPC port.
    """
    def __init__(self, user, password, host='localhost', port=8331,
                 use_https=False, numberOfRPCAttempts=1, httpTimeout = 30):
        """
        Create a new bitcoin server connection.
        """
        url = 'http{s}://{user}:{password}@{host}:{port}/'.format(
            s='s' if use_https else '',
            user=user, password=password, host=host, port=port)
        self.url = url
        try:
            self.proxy = AuthServiceProxy(url, numberOfAttempts = numberOfRPCAttempts, httpTimeout = httpTimeout) 
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def stop(self):
        """
        Stop bitcoin server.
        """
        try:
            self.proxy.stop()
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def getblock(self, hash,verboseLevel=1):
        """
        Returns information about the given block hash.
        """
        try:
            return self.proxy.getblock(hash,verboseLevel)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def getblocktemplate(self):
        """
        Returns block template to work on. 
        """
        try:
            return self.proxy.getblocktemplate() 
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def getblockcount(self):
        """
        Returns the number of blocks in the longest block chain.
        """
        try:
            return self.proxy.getblockcount()
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def getblockhash(self, index):
        """
        Returns hash of block in best-block-chain at index.

        :param index: index ob the block

        """
        try:
            return self.proxy.getblockhash(index)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def getblocknumber(self):
        """
        Returns the block number of the latest block in the longest block chain.
        Deprecated. Use getblockcount instead.
        """
        return self.getblockcount()

    def getconnectioncount(self):
        """
        Returns the number of connections to other nodes.
        """
        try:
            return self.proxy.getconnectioncount()
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def getdifficulty(self):
        """
        Returns the proof-of-work difficulty as a multiple of the minimum difficulty.
        """
        try:
            return self.proxy.getdifficulty()
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def getgenerate(self):
        """
        Returns :const:`True` or :const:`False`, depending on whether generation is enabled.
        """
        try:
            return self.proxy.getgenerate()
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def setgenerate(self, generate, genproclimit=None, isKeyBlock = None):
        """
        Enable or disable generation (mining) of coins.

        Arguments:

        - *generate* -- is :const:`True` or :const:`False` to turn generation on or off.
        - *genproclimit* -- Number of processors that are used for generation, -1 is unlimited.
        - *iskeyblock* -- Generate key blocks? No argument defaults to not sending anything, 
                          so suitable for the standard (non-ng) client. 

        """
        try:
            if (genproclimit, isKeyBlock) == (None, None): 
                return self.proxy.setgenerate(generate)
            elif genproclimit != None and isKeyBlock == None: 
                return self.proxy.setgenerate(generate, genproclimit)
            elif genproclimit == None and isKeyBlock != None: 
                return self.proxy.setgenerate(generate, 1, isKeyBlock)
            elif genproclimit != None and isKeyBlock != None: 
                return self.proxy.setgenerate(generate, genproclimit, isKeyBlock)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def generate(self, num):
        """
        Enable or disable generation (mining) of coins.

        Arguments:

        - *num* -- number of blocks

        """
        try:
            return self.proxy.generate(num)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def generatetoaddress (self, num,address):
        """
        Enable or disable generation (mining) of coins.

        Arguments:

        - *num* -- number of blocks
        - *address* --
        """
        try:
            return self.proxy.generatetoaddress(num,address)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def gethashespersec(self):
        """
        Returns a recent hashes per second performance measurement while generating.
        """
        try:
            return self.proxy.gethashespersec()
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def getinfo(self):
        """
        Returns an :class:`~bitcoinrpc.data.ServerInfo` object containing various state info.
        """
        try:
            return ServerInfo(**self.proxy.getinfo())
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def getmininginfo(self):
        """
        Returns an :class:`~bitcoinrpc.data.MiningInfo` object containing various
        mining state info.
        """
        try:
            return MiningInfo(**self.proxy.getmininginfo())
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def getnewaddress(self, account=None):
        """
        Returns a new bitcoin address for receiving payments.

        Arguments:

        - *account* -- If account is specified (recommended), it is added to the address book
          so that payments received with the address will be credited to it.

        """
        try:
            if account is None:
                return self.proxy.getnewaddress()
            else:
                return self.proxy.getnewaddress(account)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def getaddressesbylabel(self, account):
        """
        Returns the current bitcoin address for receiving payments to an account.

        Arguments:

        - *account* -- Account for which the address should be returned.

        """
        try:
            return self.proxy.getaddressesbylabel(account)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def getreceivedbylabel(self, label,num):
            """
           getreceivedbylabel "label" ( minconf )

            Returns the total amount received by addresses with <label> in transactions with at least [minconf] confirmations.

            Arguments:
            1. label      (string, required) The selected label, may be the default label using "".
            2. minconf    (numeric, optional, default=1) Only include transactions confirmed at least this many times.

            Result:
            amount              (numeric) The total amount in BTC received for this label.

            Examples:

            Amount received by the default label with at least 1 confirmation
            > bitcoin-cli getreceivedbylabel ""


            """
            try:
                return self.proxy.getreceivedbylabel(label,num)
            except JSONRPCException as e:
                raise _wrap_exception(e.error)

    def setaccount(self, bitcoinaddress, account):
        """
        Sets the account associated with the given address.

        Arguments:

        - *bitcoinaddress* -- Bitcoin address to associate.
        - *account* -- Account to associate the address to.

        """
        try:
            return self.proxy.setaccount(bitcoinaddress, account)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def getaccount(self, bitcoinaddress):
        """
        Returns the account associated with the given address.

        Arguments:

        - *bitcoinaddress* -- Bitcoin address to get account for.
        """
        try:
            return self.proxy.getaccount(bitcoinaddress)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def getaddressesbyaccount(self, account):
        """
        Returns the list of addresses for the given account.

        Arguments:

        - *account* -- Account to get list of addresses for.
        """
        try:
            return self.proxy.getaddressesbyaccount(account)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def sendtoaddress(self, bitcoinaddress, amount, comment=None, comment_to=None):
        """
        Sends *amount* from the server's available balance to *bitcoinaddress*.

        Arguments:

        - *bitcoinaddress* -- Bitcoin address to send to.
        - *amount* -- Amount to send (float, rounded to the nearest 0.01).
        - *minconf* -- Minimum number of confirmations required for transferred balance.
        - *comment* -- Comment for transaction.
        - *comment_to* -- Comment for to-address.

        """
        try:
            if comment is None:
                return self.proxy.sendtoaddress(bitcoinaddress, amount)
            elif comment_to is None:
                return self.proxy.sendtoaddress(bitcoinaddress, amount, comment)
            else:
                return self.proxy.sendtoaddress(bitcoinaddress, amount, comment, comment_to)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def getreceivedbyaddress(self, bitcoinaddress, minconf=1):
        """
        Returns the total amount received by a bitcoin address in transactions with at least a
        certain number of confirmations.

        Arguments:

        - *bitcoinaddress* -- Address to query for total amount.

        - *minconf* -- Number of confirmations to require, defaults to 1.
        """
        try:
            return self.proxy.getreceivedbyaddress(bitcoinaddress, minconf)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def getreceivedbyaccount(self, account, minconf=1):
        """
        Returns the total amount received by addresses with an account in transactions with
        at least a certain number of confirmations.

        Arguments:

        - *account* -- Account to query for total amount.
        - *minconf* -- Number of confirmations to require, defaults to 1.

        """
        try:
            return self.proxy.getreceivedbyaccount(account, minconf)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def gettransaction(self, txid):
        """
        Get detailed information about transaction

        Arguments:

        - *txid* -- Transactiond id for which the info should be returned

        """
        try:
            return TransactionInfo(**self.proxy.gettransaction(txid))
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def getrawtransaction(self, txid, verbose=True):
        """
        Get transaction raw info

        Arguments:

        - *txid* -- Transactiond id for which the info should be returned.
        - *verbose* -- If False, return only the "hex" of the transaction.

        """
        try:
            if verbose:
                #return TransactionInfo(**self.proxy.getrawtransaction(txid, 1))
                return self.proxy.getrawtransaction(txid, 1)
            return self.proxy.getrawtransaction(txid, 0)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def createrawtransaction(self, inputs, outputs):
        """
        Creates a raw transaction spending given inputs
        (a list of dictionaries, each containing a transaction id and an output number),
        sending to given address(es).

        Returns hex-encoded raw transaction.

        Example usage:
        >>> conn.createrawtransaction(
                [{"txid": "a9d4599e15b53f3eb531608ddb31f48c695c3d0b3538a6bda871e8b34f2f430c",
                  "vout": 0}],
                {"mkZBYBiq6DNoQEKakpMJegyDbw2YiNQnHT":50})


        Arguments:

        - *inputs* -- A list of {"txid": txid, "vout": n} dictionaries.
        - *outputs* -- A dictionary mapping (public) addresses to the amount
                       they are to be paid.
        """
        try:
            print ("EFE DEBUG: in:%s, out:%s" % (inputs,outputs))
            sys.stdout.flush()
            return self.proxy.createrawtransaction(inputs, outputs)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def signrawtransactionwithkey(self, hexstring, previous_transactions=None, private_keys=None):
        """
        Sign inputs for raw transaction (serialized, hex-encoded).

        Returns a dictionary with the keys:
            "hex": raw transaction with signature(s) (hex-encoded string)
            "complete": 1 if transaction has a complete set of signature(s), 0 if not

        Arguments:

        - *hexstring* -- A hex string of the transaction to sign.
        - *previous_transactions* -- A (possibly empty) list of dictionaries of the form:
            {"txid": txid, "vout": n, "scriptPubKey": hex, "redeemScript": hex}, representing
            previous transaction outputs that this transaction depends on but may not yet be
            in the block chain.
        - *private_keys* -- A (possibly empty) list of base58-encoded private
            keys that, if given, will be the only keys used to sign the transaction.
        """
        try:
            return dict(self.proxy.signrawtransactionwithkey(hexstring, previous_transactions, private_keys))
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def decoderawtransaction(self, hexstring):
        """
        Produces a human-readable JSON object for a raw transaction.

        Arguments:

        - *hexstring* -- A hex string of the transaction to be decoded.
        """
        try:
            retVal = self.proxy.decoderawtransaction(hexstring)
            return dict(retVal)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def listsinceblock(self, block_hash):
        try:
            res = self.proxy.listsinceblock(block_hash)
            res['transactions'] = [TransactionInfo(**x) for x in res['transactions']]
            return res
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def listreceivedbyaddress(self, minconf=1, includeempty=False):
        """
        Returns a list of addresses.

        Each address is represented with a :class:`~bitcoinrpc.data.AddressInfo` object.

        Arguments:

        - *minconf* -- Minimum number of confirmations before payments are included.
        - *includeempty* -- Whether to include addresses that haven't received any payments.

        """
        try:
            return [AddressInfo(**x) for x in
                    self.proxy.listreceivedbyaddress(minconf, includeempty)]
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def listaccounts(self, minconf=1, as_dict=False):
        """
        Returns a list of account names.

        Arguments:

        - *minconf* -- Minimum number of confirmations before payments are included.
        - *as_dict* -- Returns a dictionary of account names, with their balance as values.
        """
        try:
            if as_dict:
                return dict(self.proxy.listaccounts(minconf))
            else:
                return self.proxy.listaccounts(minconf).keys()
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def listreceivedbyaccount(self, minconf=1, includeempty=False):
        """
        Returns a list of accounts.

        Each account is represented with a :class:`~bitcoinrpc.data.AccountInfo` object.

        Arguments:

        - *minconf* -- Minimum number of confirmations before payments are included.

        - *includeempty* -- Whether to include addresses that haven't received any payments.
        """
        try:
            return [AccountInfo(**x) for x in
                    self.proxy.listreceivedbyaccount(minconf, includeempty)]
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def listtransactions(self, account=None, count=10, from_=0, address=None):
        """
        Returns a list of the last transactions for an account.

        Each transaction is represented with a :class:`~bitcoinrpc.data.TransactionInfo` object.

        Arguments:

        - *account* -- Account to list transactions from. Return transactions from
                       all accounts if None.
        - *count* -- Number of transactions to return.
        - *from_* -- Skip the first <from_> transactions.
        - *address* -- Receive address to consider
        """
        accounts = [account] if account is not None else self.listaccounts(as_dict=True).iterkeys()
        try:
            return [TransactionInfo(**tx) for acc in accounts for
                    tx in self.proxy.listtransactions(acc, count, from_) if
                    address is None or tx["address"] == address]
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def backupwallet(self, destination):
        """
        Safely copies ``wallet.dat`` to *destination*, which can be a directory or a path
        with filename.

        Arguments:
        - *destination* -- directory or path with filename to backup wallet to.

        """
        try:
            return self.proxy.backupwallet(destination)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def validateaddress(self, validateaddress):
        """
        Validate a bitcoin address and return information for it.

        The information is represented by a :class:`~bitcoinrpc.data.AddressValidation` object.

        Arguments: -- Address to validate.


        - *validateaddress*
        """
        try:
            return AddressValidation(**self.proxy.validateaddress(validateaddress))
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def getbalance(self, account=None, minconf=None):
        """
        Get the current balance, either for an account or the total server balance.

        Arguments:
        - *account* -- If this parameter is specified, returns the balance in the account.
        - *minconf* -- Minimum number of confirmations required for transferred balance.

        """
        args = []
        if account:
            args.append(account)
            if minconf is not None:
                args.append(minconf)
        try:
            return self.proxy.getbalance(*args)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def move(self, fromaccount, toaccount, amount, minconf=1, comment=None):
        """
        Move from one account in your wallet to another.

        Arguments:

        - *fromaccount* -- Source account name.
        - *toaccount* -- Destination account name.
        - *amount* -- Amount to transfer.
        - *minconf* -- Minimum number of confirmations required for transferred balance.
        - *comment* -- Comment to add to transaction log.

        """
        try:
            if comment is None:
                return self.proxy.move(fromaccount, toaccount, amount, minconf)
            else:
                return self.proxy.move(fromaccount, toaccount, amount, minconf, comment)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def sendfrom(self, fromaccount, tobitcoinaddress, amount, minconf=1, comment=None,
                 comment_to=None):
        """
        Sends amount from account's balance to bitcoinaddress. This method will fail
        if there is less than amount bitcoins with minconf confirmations in the account's
        balance (unless account is the empty-string-named default account; it
        behaves like the sendtoaddress method). Returns transaction ID on success.

        Arguments:

        - *fromaccount* -- Account to send from.
        - *tobitcoinaddress* -- Bitcoin address to send to.
        - *amount* -- Amount to send (float, rounded to the nearest 0.01).
        - *minconf* -- Minimum number of confirmations required for transferred balance.
        - *comment* -- Comment for transaction.
        - *comment_to* -- Comment for to-address.

        """
        try:
            if comment is None:
                return self.proxy.sendfrom(fromaccount, tobitcoinaddress, amount, minconf)
            elif comment_to is None:
                return self.proxy.sendfrom(fromaccount, tobitcoinaddress, amount, minconf, comment)
            else:
                return self.proxy.sendfrom(fromaccount, tobitcoinaddress, amount, minconf,
                                           comment, comment_to)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def sendmany(self, fromaccount, todict, minconf=1, comment=None):
        """
        Sends specified amounts from account's balance to bitcoinaddresses. This method will fail
        if there is less than total amount bitcoins with minconf confirmations in the account's
        balance (unless account is the empty-string-named default account; Returns transaction ID
        on success.

        Arguments:

        - *fromaccount* -- Account to send from.
        - *todict* -- Dictionary with Bitcoin addresses as keys and amounts as values.
        - *minconf* -- Minimum number of confirmations required for transferred balance.
        - *comment* -- Comment for transaction.

        """
        try:
            if comment is None:
                return self.proxy.sendmany(fromaccount, todict, minconf)
            else:
                return self.proxy.sendmany(fromaccount, todict, minconf, comment)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def verifymessage(self, bitcoinaddress, signature, message):
        """
        Verifies a signature given the bitcoinaddress used to sign,
        the signature itself, and the message that was signed.
        Returns :const:`True` if the signature is valid, and :const:`False` if it is invalid.

        Arguments:

        - *bitcoinaddress* -- the bitcoinaddress used to sign the message
        - *signature* -- the signature to be verified
        - *message* -- the message that was originally signed

        """
        try:
            return self.proxy.verifymessage(bitcoinaddress, signature, message)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def getwork(self, data=None):
        """
        Get work for remote mining, or submit result.
        If data is specified, the server tries to solve the block
        using the provided data and returns :const:`True` if it was successful.
        If not, the function returns formatted hash data (:class:`~bitcoinrpc.data.WorkItem`)
        to work on.

        Arguments:

        - *data* -- Result from remote mining.

        """
        try:
            if data is None:
                # Only if no data provided, it returns a WorkItem
                return WorkItem(**self.proxy.getwork())
            else:
                return self.proxy.getwork(data)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def listunspent(self, minconf=1, maxconf=999999,address="[]"):
        """
        Returns a list of unspent transaction inputs in the wallet.

        Arguments:

        - *minconf* -- Minimum number of confirmations required to be listed.

        - *maxconf* -- Maximal number of confirmations allowed to be listed.


        """
        try:
            return [
                    self.proxy.listunspent(minconf, maxconf,address)]
        except JSONRPCException as e:
            raise _wrap_exception(e.error)
    
    def keypoolrefill(self):
        "Fills the keypool, requires wallet passphrase to be set."
        try:
            self.proxy.keypoolrefill()
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def walletpassphrase(self, passphrase, timeout, dont_raise=False):
        """
        Stores the wallet decryption key in memory for <timeout> seconds.

        - *passphrase* -- The wallet passphrase.

        - *timeout* -- Time in seconds to keep the wallet unlocked
                       (by keeping the passphrase in memory).

        - *dont_raise* -- instead of raising `~bitcoinrpc.exceptions.WalletPassphraseIncorrect`
                          return False.
        """
        try:
            self.proxy.walletpassphrase(passphrase, timeout)
            return True
        except JSONRPCException as e:
            json_exception = _wrap_exception(e.error)
            if dont_raise:
                if isinstance(json_exception, WalletPassphraseIncorrect):
                    return False
                elif isinstance(json_exception, WalletAlreadyUnlocked):
                    return True
            raise json_exception

    def walletlock(self):
        """
        Removes the wallet encryption key from memory, locking the wallet.
        After calling this method, you will need to call walletpassphrase
        again before being able to call any methods which require the wallet
        to be unlocked.
        """
        try:
            return self.proxy.walletlock()
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def walletpassphrasechange(self, oldpassphrase, newpassphrase, dont_raise=False):
        """
        Changes the wallet passphrase from <oldpassphrase> to <newpassphrase>.

        Arguments:

        - *dont_raise* -- instead of raising `~bitcoinrpc.exceptions.WalletPassphraseIncorrect`
                          return False.
        """
        try:
            self.proxy.walletpassphrasechange(oldpassphrase, newpassphrase)
            return True
        except JSONRPCException as e:
            json_exception = _wrap_exception(e.error)
            if dont_raise and isinstance(json_exception, WalletPassphraseIncorrect):
                return False
            raise json_exception

    def getpeerinfo(self): 
        try:
            self.proxy.getpeerinfo() 
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def submitblock(self, hexData): 
        try: 
            return self.proxy.submitblock(hexData) 
        except JSONRPCException as e: 
            raise _wrap_exception(e.error) 

# ITTAY: 

    def getrawmempool(self, verbose = None, countOnly = None):
        """
        Returns all transaction ids in memory pool
        """
        try:
            if verbose != None:
                if countOnly != None:
                    return self.proxy.getrawmempool(verbose, countOnly)
                else:
                    return self.proxy.getrawmempool(verbose)
            else:
                return self.proxy.getrawmempool()
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def gettxout(self, txid, n , mempool = None):
        try:
            return self.proxy.gettxout(txid,n,mempool)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def settxfee(self, amount):
        try:
            return self.proxy.settxfee(amount)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def getbestblockhash(self):
        """
        Returns all transaction ids in memory pool
        """
        try:
            return self.proxy.getbestblockhash() 
        except JSONRPCException as e: 
            raise _wrap_exception(e.error) 

    def logmessage(self, msg):
        """
        Log a message to the bitcoin debug log. 
        """
        try:
            self.proxy.logmessage(msg)
            return True
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def dumpprivkey(self,address):
        """
                        """
        try:
            return self.proxy.dumpprivkey(address)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def addmultisigaddress(self,number,keys):
        """
                """
        try:
            return self.proxy.addmultisigaddress(number,keys)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def sendrawtransaction(self, txnHex): 
        """
        Submits raw transaction (serialized, hex-encoded) to local node and network. 
        """
        try:
            self.proxy.sendrawtransaction(txnHex)
            return True
        except JSONRPCException as e:
            raise _wrap_exception(e.error)

    def setlabel(self, add,name):
        try:
            self.proxy.setlabel(add, name)
        except JSONRPCException as e:
            raise _wrap_exception(e.error)