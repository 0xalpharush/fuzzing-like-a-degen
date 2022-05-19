import sys
import random
from web3 import Web3, HTTPProvider, Account
from node import fixture_ganache
from abi import get_abi_and_bytecode, get_abi_by_name
from strategy import get_strategies
from hypothesis import given, settings, note

class InvariantException(Exception):
    """Invariant function is not defined properly."""
    pass

def deploy_contract(w3, ganache, contract_names):
    """Deploy contract to the local ganache network."""
    abis, bytecodes = get_abi_and_bytecode()
    targets = []
    deployed_abis = []
    for contract in contract_names:
        abi = abis[contract]
        bytecode = bytecodes[contract]
        signed_txn = w3.eth.account.sign_transaction(
            dict(
                nonce=w3.eth.get_transaction_count(ganache.eth_address),
                maxFeePerGas=20000000000,
                maxPriorityFeePerGas=1,
                gas=15000000,
                to=b"",
                data="0x" + bytecode,
                chainId=1,
            ),
            ganache.eth_privkey,
        )
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        address = w3.eth.get_transaction_receipt(tx_hash)["contractAddress"]
        target = w3.eth.contract(address, abi=abi)

        if "setUp" in target.functions:
            # TODO record which contracts are deployed 
            # remove this from functions to fuzz
            func = target.functions["setUp"]
            func().transact({'from' : w3.eth.default_account.address})

            # We only fuzz contracts that have setUp functions
            for info in target.abi:
                if info["type"] == "function" and info["stateMutability"] == "view":
                    for ret in info["outputs"]:
                        internal_type = ret["internalType"]
                        if internal_type.startswith("contract"):
                            deployed = target.functions[info["name"]]().call({'from' : w3.eth.default_account.address})
                        
                        #TODO Deal with edge that contract names are the same
                        contract_name = internal_type.split(" ")[1]
                        deployed_abi = get_abi_by_name(contract_name)
                        targets.append(w3.eth.contract(abi=deployed_abi, address=deployed))

            targets.append(target)

    return targets


def fuzz(fuzz_runs):
    # Ganache node
    ganache, proc = fixture_ganache() 

    # Provider
    w3 = Web3(HTTPProvider(ganache.provider, request_kwargs={"timeout": 30}))
    w3.eth.default_account = Account.from_key(ganache.eth_privkey)
    account = w3.eth.default_account.address
    try: 
        assert w3.isConnected()
    except:
        ganache_gen.throw()
        sys.exit(-1)

    contract_names, functions = get_strategies()
    targets = deploy_contract(w3, ganache, contract_names)
    invariants, fuzz_candidates = collect_functions(contract_names, functions, targets)

    while fuzz_runs > 0:
        fuzz_run(invariants, random.choice(fuzz_candidates), account)
        fuzz_runs -= 1

    proc.kill()
    proc.wait()

def collect_functions(contract_names, functions, targets):
    invariants = []
    fuzz_candidates = []
    for contract in contract_names:
        for func in functions[contract]:
            is_invariant = False
            func_to_call = func["name"]

            if func_to_call.startswith("invariant"):
                try:
                    assert len(func["outputs"]) == 1 and func["outputs"][0]["internalType"] == "bool"
                except:
                    raise InvariantException(f"{func_to_call} should have one boolean return value")
                
                is_invariant = True

            if func_to_call.startswith("setUp"):
                continue

            # TODO make sure duplicate function names don't cause strategy confusion
            for target in targets:
                if func_to_call in target.functions:
                    if is_invariant:
                        invariants.append(target.functions[func_to_call])
                    else:
                        fuzz_candidates.append((target.functions[func_to_call], func["strategy"]))

    return invariants, fuzz_candidates

# Long term, we want two fuzzing strategies:
# 1) FIND THE PERMUTATION OF CALLS
#   Execute the function once and the some other function (random)
# 2) FIND INTERESTING INPUTS:
#   Execute the function X number of times in sequence 
#   - Ideally, this would be guided coverage 
#   - We could use this corpus/ inputs as a seed for the first test case
def fuzz_run(invariants, fuzz_candidates, account):
    func, strat = fuzz_candidates

    @settings(max_examples=1000)
    @given(strat)
    def execute_fuzz(arg):
        print(f"{func}({arg})")
        note(f"Counterexample: {func}({arg!r})")
        # TODO encode multi-arg func properly
        func(arg).transact({'from' : account})
        for invariant in invariants:
            result = invariant().call({'from' : account})
            print(invariant)
            print(result)
            assert(result)
    try:
        execute_fuzz()
    except AssertionError:
        print("Invariant broken")

    

if __name__ == "__main__":
    fuzz(10)