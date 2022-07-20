## What is this?

A 4-hr smart contract fuzzer speed run. Successfully broke the test contract, but lots of TODOs, cleaning up hastily written code, and ideas to explore.

I wrote this as a learning exercise after reading through [h0mbre's](https://twitter.com/h0mbre_) blog series, [Fuzzing Like a Caveman](https://h0mbre.github.io/Fuzzing-Like-A-Caveman/), which I highly recommend. A recording of the livestream is available on [Youtube](https://www.youtube.com/watch?v=qdtQ9k3gCX8).

## Installation

```shell
pip install hypothesis web3 solc-select crytic-compile
```
```
solc-select install 0.8.12
solc-select use 0.8.12
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
