## What is this?

A 4-hr smart contract speed run. Successfully broke the test contract, but lots of TODOs, cleaning up hastily written code, and ideas to explore.

## Installation

```shell
pip install hypothesis web3 solc-select 
```

Ganache
```
npm i -g ganache-cli
```
## Usage

```shell
crytic-compile --export-format standard tests/invariant_breaker.sol
```

```
python fuzzer.py
```