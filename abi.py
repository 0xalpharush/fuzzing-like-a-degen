import os
import json
from pathlib import Path
from typing import List, Dict

DEFAULT_EXPORT_FOLDER="crytic-export"
DEFAULT_DIR=Path(DEFAULT_EXPORT_FOLDER)


def get_functions() -> (List, Dict):
    functions = {}
    contract_set = set()
    for artifact in DEFAULT_DIR.glob("*.json"):

        with open(artifact.resolve().as_posix()) as crytic_out:
            out_info = json.load(crytic_out)
            c_units = list(out_info["compilation_units"].keys())

            for unit in c_units:
                contracts = out_info["compilation_units"][unit]["contracts"][unit]
                contract_names = list(contracts.keys())

                for contract in contracts:
                    contract_set.add(contract)
                    functions[contract] = [data for data in contracts[contract]["abi"] if data["type"] == "function" and data["stateMutability"] != "view"]
                
                # If the internalType of an input starts with `contract` we should save it,
                # and look for it in the other abis, then deduce which functions are available to us

    return (contract_names, functions)

def get_abi_and_bytecode():
    abi = {}
    bytecode = {}
    contract_set = set()
    for artifact in DEFAULT_DIR.glob("*.json"):

        with open(artifact.resolve().as_posix()) as crytic_out:
            out_info = json.load(crytic_out)
            c_units = list(out_info["compilation_units"].keys())

            for unit in c_units:
                contracts = out_info["compilation_units"][unit]["contracts"][unit]
                contract_names = list(contracts.keys())

                for contract in contracts:
                    contract_set.add(contract)
                    abi[contract] = contracts[contract]["abi"]
                    bytecode[contract] = contracts[contract]["bin"]

    return (abi, bytecode)

def get_abi_by_name(contract_name):
    abi = {}
    for artifact in DEFAULT_DIR.glob("*.json"):

        with open(artifact.resolve().as_posix()) as crytic_out:
            out_info = json.load(crytic_out)
            c_units = list(out_info["compilation_units"].keys())

            for unit in c_units:
                contracts = out_info["compilation_units"][unit]["contracts"][unit]
                
    return contracts[contract_name]["abi"]


if __name__ == "__main__":
    print(get_abi_and_bytecode())
