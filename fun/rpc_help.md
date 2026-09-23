# Bitcoin Core RPC Reference

Auto-generated from `bitcoin-cli help <command>`.


## Blockchain

### dumptxoutset

```
dumptxoutset "path" ( "type" {"rollback":n,"in_memory":bool,...} )

Write the serialized UTXO set to a file. This can be used in loadtxoutset afterwards if this snapshot height is supported in the chainparams as well.
This creates a temporary UTXO database when rolling back, keeping the main chain intact. Should the node experience an unclean shutdown the temporary database may need to be removed from the datadir manually.
For deep rollbacks, make sure to use no RPC timeout (bitcoin-cli -rpcclienttimeout=0) as it may take several minutes.

Arguments:
1. path       (string, required) Path to the output file. If relative, will be prefixed by datadir.
2. type       (string, optional, default="") The type of snapshot to create. Can be "latest" to create a snapshot of the current UTXO set or "rollback" to temporarily roll back the state of the node to a historical block before creating the snapshot of a historical UTXO set. This parameter can be omitted if a separate "rollback" named parameter is specified indicating the height or hash of a specific historical block. If "rollback" is specified and separate "rollback" named parameter is not specified, this will roll back to the latest valid snapshot block that can currently be loaded with loadtxoutset.
3. options    (json object, optional) Options object that can be used to pass named arguments, listed below.

Named Arguments:
rollback     (string or numeric, optional) Height or hash of the block to roll back to before creating the snapshot. Note: The further this number is from the tip, the longer this process will take. Consider setting a higher -rpcclienttimeout value in this case.
in_memory    (boolean, optional, default=false) If true, the temporary UTXO-set database used during rollback is kept entirely in memory. This can significantly speed up the process but requires sufficient free RAM (over 10 GB on mainnet).

Result:
{                             (json object)
  "coins_written" : n,        (numeric) the number of coins written in the snapshot
  "base_hash" : "hex",        (string) the hash of the base of the snapshot
  "base_height" : n,          (numeric) the height of the base of the snapshot
  "path" : "str",             (string) the absolute path that the snapshot was written to
  "txoutset_hash" : "hex",    (string) the hash of the UTXO set contents
  "nchaintx" : n              (numeric) the number of transactions in the chain up to and including the base block
}

Examples:
> bitcoin-cli -rpcclienttimeout=0 dumptxoutset utxo.dat latest
> bitcoin-cli -rpcclienttimeout=0 dumptxoutset utxo.dat rollback
> bitcoin-cli -rpcclienttimeout=0 -named dumptxoutset utxo.dat rollback=853456
> bitcoin-cli -rpcclienttimeout=0 -named dumptxoutset utxo.dat rollback=853456 in_memory=true
```

### getbestblockhash

```
getbestblockhash

Returns the hash of the best (tip) block in the most-work fully-validated chain.

Result:
"hex"    (string) the block hash, hex-encoded

Examples:
> bitcoin-cli getbestblockhash 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getbestblockhash", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getblock

```
getblock "blockhash" ( verbosity )

If verbosity is 0, returns a string that is serialized, hex-encoded data for block 'hash'.
If verbosity is 1, returns an Object with information about block <hash>.
If verbosity is 2, returns an Object with information about block <hash> and information about each transaction.
If verbosity is 3, returns an Object with information about block <hash> and information about each transaction, including prevout information for inputs (only for unpruned blocks in the current best chain).

Arguments:
1. blockhash    (string, required) The block hash
2. verbosity    (numeric, optional, default=1) 0 for hex-encoded data, 1 for a JSON object, 2 for JSON object with transaction data, and 3 for JSON object with transaction data including prevout information for inputs

Result (for verbosity = 0):
"hex"    (string) A string that is serialized, hex-encoded data for block 'hash'

Result (for verbosity = 1):
{                                 (json object)
  "hash" : "hex",                 (string) the block hash (same as provided)
  "confirmations" : n,            (numeric) The number of confirmations, or -1 if the block is not on the main chain
  "size" : n,                     (numeric) The block size
  "strippedsize" : n,             (numeric) The block size excluding witness data
  "weight" : n,                   (numeric) The block weight as defined in BIP 141
  "coinbase_tx" : {               (json object) Coinbase transaction metadata
    "version" : n,                (numeric) The coinbase transaction version
    "locktime" : n,               (numeric) The coinbase transaction's locktime (nLockTime)
    "sequence" : n,               (numeric) The coinbase input's sequence number (nSequence)
    "coinbase" : "hex",           (string) The coinbase input's script
    "witness" : "hex"             (string, optional) The coinbase input's first (and only) witness stack element, if present
  },
  "height" : n,                   (numeric) The block height or index
  "version" : n,                  (numeric) The block version
  "versionHex" : "hex",           (string) The block version formatted in hexadecimal
  "merkleroot" : "hex",           (string) The merkle root
  "tx" : [                        (json array) The transaction ids
    "hex",                        (string) The transaction id
    ...
  ],
  "time" : xxx,                   (numeric) The block time expressed in UNIX epoch time
  "mediantime" : xxx,             (numeric) The median block time expressed in UNIX epoch time
  "nonce" : n,                    (numeric) The nonce
  "bits" : "hex",                 (string) nBits: compact representation of the block difficulty target
  "target" : "hex",               (string) The difficulty target
  "difficulty" : n,               (numeric) The difficulty
  "chainwork" : "hex",            (string) Expected number of hashes required to produce the chain up to this block (in hex)
  "nTx" : n,                      (numeric) The number of transactions in the block
  "previousblockhash" : "hex",    (string, optional) The hash of the previous block (if available)
  "nextblockhash" : "hex"         (string, optional) The hash of the next block (if available)
}

Result (for verbosity = 2):
{                   (json object)
  ...,              Same output as verbosity = 1
  "tx" : [          (json array)
    {               (json object)
      ...,          The transactions in the format of the getrawtransaction RPC. Different from verbosity = 1 "tx" result
      "fee" : n     (numeric, optional) The transaction fee in BTC, omitted if block undo data is not available
    },
    ...
  ]
}

Result (for verbosity = 3):
{                                        (json object)
  ...,                                   Same output as verbosity = 2
  "tx" : [                               (json array)
    {                                    (json object)
      "vin" : [                          (json array)
        {                                (json object)
          ...,                           The same output as verbosity = 2
          "prevout" : {                  (json object, optional) (Only if undo information is available)
            "generated" : true|false,    (boolean) Coinbase or not
            "height" : n,                (numeric) The height of the prevout
            "value" : n,                 (numeric) The value in BTC
            "scriptPubKey" : {           (json object)
              "asm" : "str",             (string) Disassembly of the output script
              "desc" : "str",            (string) Inferred descriptor for the output
              "hex" : "hex",             (string) The raw output script bytes, hex-encoded
              "address" : "str",         (string, optional) The Bitcoin address (only if a well-defined address exists)
              "type" : "str"             (string) The type (one of: nonstandard, anchor, pubkey, pubkeyhash, scripthash, multisig, nulldata, witness_v0_scripthash, witness_v0_keyhash, witness_v1_taproot, witness_unknown)
            }
          }
        },
        ...
      ]
    },
    ...
  ]
}

Examples:
> bitcoin-cli getblock "00000000c937983704a73af28acdec37b049d214adbda81d7e2a3dd146f6ed09"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getblock", "params": ["00000000c937983704a73af28acdec37b049d214adbda81d7e2a3dd146f6ed09"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getblockchaininfo

```
getblockchaininfo

Returns an object containing various state info regarding blockchain processing.

Result:
{                                         (json object)
  "chain" : "str",                        (string) current network name (main, test, testnet4, signet, regtest)
  "blocks" : n,                           (numeric) the height of the most-work fully-validated chain. The genesis block has height 0
  "headers" : n,                          (numeric) the current number of headers we have validated
  "bestblockhash" : "str",                (string) the hash of the currently best block
  "bits" : "hex",                         (string) nBits: compact representation of the block difficulty target
  "target" : "hex",                       (string) the difficulty target
  "difficulty" : n,                       (numeric) the current difficulty
  "time" : xxx,                           (numeric) the block time expressed in UNIX epoch time
  "mediantime" : xxx,                     (numeric) the median block time expressed in UNIX epoch time
  "verificationprogress" : n,             (numeric) estimate of verification progress [0..1]
  "initialblockdownload" : true|false,    (boolean) (debug information) estimate of whether this node is in Initial Block Download mode
  "backgroundvalidation" : {              (json object, optional) state info regarding background validation process
    "snapshotheight" : n,                 (numeric) the height of the snapshot block. Background validation verifies the chain from genesis up to this height
    "blocks" : n,                         (numeric) the height of the most-work background fully-validated chain. The genesis block has height 0
    "bestblockhash" : "str",              (string) the hash of the currently best block validated in the background
    "mediantime" : xxx,                   (numeric) the median block time expressed in UNIX epoch time
    "verificationprogress" : n,           (numeric) estimate of background verification progress [0..1]
    "chainwork" : "hex"                   (string) total amount of work in background validated chain, in hexadecimal
  },
  "chainwork" : "hex",                    (string) total amount of work in active chain, in hexadecimal
  "size_on_disk" : n,                     (numeric) the estimated size of the block and undo files on disk
  "pruned" : true|false,                  (boolean) if the blocks are subject to pruning
  "pruneheight" : n,                      (numeric, optional) the first block unpruned, all previous blocks were pruned (only present if pruning is enabled)
  "automatic_pruning" : true|false,       (boolean, optional) whether automatic pruning is enabled (only present if pruning is enabled)
  "prune_target_size" : n,                (numeric, optional) the target size used by pruning (only present if automatic pruning is enabled)
  "signet_challenge" : "hex",             (string, optional) the block challenge (aka. block script), in hexadecimal (only present if the current network is a signet)
  "warnings" : [                          (json array) any network and blockchain warnings (run with `-deprecatedrpc=warnings` to return the latest warning as a single string)
    "str",                                (string) warning
    ...
  ]
}

Examples:
> bitcoin-cli getblockchaininfo 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getblockchaininfo", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getblockcount

```
getblockcount

Returns the height of the most-work fully-validated chain.
The genesis block has height 0.

Result:
n    (numeric) The current block count

Examples:
> bitcoin-cli getblockcount 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getblockcount", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getblockfilter

```
getblockfilter "blockhash" ( "filtertype" )

Retrieve a BIP 157 content filter for a particular block.

Arguments:
1. blockhash     (string, required) The hash of the block
2. filtertype    (string, optional, default="basic") The type name of the filter

Result:
{                      (json object)
  "filter" : "hex",    (string) the hex-encoded filter data
  "header" : "hex"     (string) the hex-encoded filter header
}

Examples:
> bitcoin-cli getblockfilter "00000000c937983704a73af28acdec37b049d214adbda81d7e2a3dd146f6ed09" "basic"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getblockfilter", "params": ["00000000c937983704a73af28acdec37b049d214adbda81d7e2a3dd146f6ed09", "basic"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getblockfrompeer

```
getblockfrompeer "blockhash" peer_id

Attempt to fetch block from a given peer.

We must have the header for this block, e.g. using submitheader.
The block will not have any undo data which can limit the usage of the block data in a context where the undo data is needed.
Subsequent calls for the same block may cause the response from the previous peer to be ignored.
Peers generally ignore requests for a stale block that they never fully verified, or one that is more than a month old.
When a peer does not respond with a block, we will disconnect.
Note: The block could be re-pruned as soon as it is received.

Returns an empty JSON object if the request was successfully scheduled.

Arguments:
1. blockhash    (string, required) The block hash to try to fetch
2. peer_id      (numeric, required) The peer to fetch it from (see getpeerinfo for peer IDs)

Result:
{}    (empty JSON object)

Examples:
> bitcoin-cli getblockfrompeer "00000000c937983704a73af28acdec37b049d214adbda81d7e2a3dd146f6ed09" 0
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getblockfrompeer", "params": ["00000000c937983704a73af28acdec37b049d214adbda81d7e2a3dd146f6ed09", 0]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getblockhash

```
getblockhash height

Returns hash of block in best-block-chain at height provided.

Arguments:
1. height    (numeric, required) The height index

Result:
"hex"    (string) The block hash

Examples:
> bitcoin-cli getblockhash 1000
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getblockhash", "params": [1000]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getblockheader

```
getblockheader "blockhash" ( verbose )

If verbose is false, returns a string that is serialized, hex-encoded data for blockheader 'hash'.
If verbose is true, returns an Object with information about blockheader <hash>.

Arguments:
1. blockhash    (string, required) The block hash
2. verbose      (boolean, optional, default=true) true for a json object, false for the hex-encoded data

Result (for verbose = true):
{                                 (json object)
  "hash" : "hex",                 (string) the block hash (same as provided)
  "confirmations" : n,            (numeric) The number of confirmations, or -1 if the block is not on the main chain
  "height" : n,                   (numeric) The block height or index
  "version" : n,                  (numeric) The block version
  "versionHex" : "hex",           (string) The block version formatted in hexadecimal
  "merkleroot" : "hex",           (string) The merkle root
  "time" : xxx,                   (numeric) The block time expressed in UNIX epoch time
  "mediantime" : xxx,             (numeric) The median block time expressed in UNIX epoch time
  "nonce" : n,                    (numeric) The nonce
  "bits" : "hex",                 (string) nBits: compact representation of the block difficulty target
  "target" : "hex",               (string) The difficulty target
  "difficulty" : n,               (numeric) The difficulty
  "chainwork" : "hex",            (string) Expected number of hashes required to produce the current chain
  "nTx" : n,                      (numeric) The number of transactions in the block
  "previousblockhash" : "hex",    (string, optional) The hash of the previous block (if available)
  "nextblockhash" : "hex"         (string, optional) The hash of the next block (if available)
}

Result (for verbose=false):
"hex"    (string) A string that is serialized, hex-encoded data for block 'hash'

Examples:
> bitcoin-cli getblockheader "00000000c937983704a73af28acdec37b049d214adbda81d7e2a3dd146f6ed09"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getblockheader", "params": ["00000000c937983704a73af28acdec37b049d214adbda81d7e2a3dd146f6ed09"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getblockstats

```
getblockstats hash_or_height ( stats )

Compute per block statistics for a given window. All amounts are in satoshis.
It won't work for some heights with pruning.

Arguments:
1. hash_or_height    (string or numeric, required) The block hash or height of the target block
2. stats             (json array, optional, default=all values) Values to plot (see result below)
     [
       "height",     (string) Selected statistic
       "time",       (string) Selected statistic
       ...
     ]

Result:
{                                (json object)
  "avgfee" : n,                  (numeric, optional) Average fee in the block
  "avgfeerate" : n,              (numeric, optional) Average feerate (in satoshis per virtual byte)
  "avgtxsize" : n,               (numeric, optional) Average transaction size
  "blockhash" : "hex",           (string, optional) The block hash (to check for potential reorgs)
  "feerate_percentiles" : [      (json array, optional) Feerates at the 10th, 25th, 50th, 75th, and 90th percentile weight unit (in satoshis per virtual byte)
    n,                           (numeric) The 10th percentile feerate
    n,                           (numeric) The 25th percentile feerate
    n,                           (numeric) The 50th percentile feerate
    n,                           (numeric) The 75th percentile feerate
    n                            (numeric) The 90th percentile feerate
  ],
  "height" : n,                  (numeric, optional) The height of the block
  "ins" : n,                     (numeric, optional) The number of inputs (excluding coinbase)
  "maxfee" : n,                  (numeric, optional) Maximum fee in the block
  "maxfeerate" : n,              (numeric, optional) Maximum feerate (in satoshis per virtual byte)
  "maxtxsize" : n,               (numeric, optional) Maximum transaction size
  "medianfee" : n,               (numeric, optional) Truncated median fee in the block
  "mediantime" : n,              (numeric, optional) The block median time past
  "mediantxsize" : n,            (numeric, optional) Truncated median transaction size
  "minfee" : n,                  (numeric, optional) Minimum fee in the block
  "minfeerate" : n,              (numeric, optional) Minimum feerate (in satoshis per virtual byte)
  "mintxsize" : n,               (numeric, optional) Minimum transaction size
  "outs" : n,                    (numeric, optional) The number of outputs
  "subsidy" : n,                 (numeric, optional) The block subsidy
  "swtotal_size" : n,            (numeric, optional) Total size of all segwit transactions
  "swtotal_weight" : n,          (numeric, optional) Total weight of all segwit transactions
  "swtxs" : n,                   (numeric, optional) The number of segwit transactions
  "time" : n,                    (numeric, optional) The block time
  "total_out" : n,               (numeric, optional) Total amount in all outputs (excluding coinbase and thus reward [ie subsidy + totalfee])
  "total_size" : n,              (numeric, optional) Total size of all non-coinbase transactions
  "total_weight" : n,            (numeric, optional) Total weight of all non-coinbase transactions
  "totalfee" : n,                (numeric, optional) The fee total
  "txs" : n,                     (numeric, optional) The number of transactions (including coinbase)
  "utxo_increase" : n,           (numeric, optional) The increase/decrease in the number of unspent outputs (not discounting op_return and similar)
  "utxo_size_inc" : n,           (numeric, optional) The increase/decrease in size for the utxo index (not discounting op_return and similar)
  "utxo_increase_actual" : n,    (numeric, optional) The increase/decrease in the number of unspent outputs, not counting unspendables
  "utxo_size_inc_actual" : n     (numeric, optional) The increase/decrease in size for the utxo index, not counting unspendables
}

Examples:
> bitcoin-cli getblockstats '"00000000c937983704a73af28acdec37b049d214adbda81d7e2a3dd146f6ed09"' '["minfeerate","avgfeerate"]'
> bitcoin-cli getblockstats 1000 '["minfeerate","avgfeerate"]'
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getblockstats", "params": ["00000000c937983704a73af28acdec37b049d214adbda81d7e2a3dd146f6ed09", ["minfeerate","avgfeerate"]]}' -H 'content-type: application/json' http://127.0.0.1:8332/
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getblockstats", "params": [1000, ["minfeerate","avgfeerate"]]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getchainstates

```
getchainstates

Return information about chainstates.

Result:
{                                      (json object)
  "headers" : n,                       (numeric) the number of headers seen so far
  "chainstates" : [                    (json array) list of the chainstates ordered by work, with the most-work (active) chainstate last
    {                                  (json object)
      "blocks" : n,                    (numeric) number of blocks in this chainstate
      "bestblockhash" : "hex",         (string) blockhash of the tip
      "bits" : "hex",                  (string) nBits: compact representation of the block difficulty target
      "target" : "hex",                (string) The difficulty target
      "difficulty" : n,                (numeric) difficulty of the tip
      "verificationprogress" : n,      (numeric) progress towards the network tip
      "snapshot_blockhash" : "hex",    (string, optional) the base block of the snapshot this chainstate is based on, if any
      "coins_db_cache_bytes" : n,      (numeric) size of the coinsdb cache
      "coins_tip_cache_bytes" : n,     (numeric) size of the coinstip cache
      "validated" : true|false         (boolean) whether the chainstate is fully validated. True if all blocks in the chainstate were validated, false if the chain is based on a snapshot and the snapshot has not yet been validated.
    },
    ...
  ]
}

Examples:
> bitcoin-cli getchainstates 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getchainstates", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getchaintips

```
getchaintips

Return information about all known tips in the block tree, including the main chain as well as orphaned branches.

Result:
[                        (json array)
  {                      (json object)
    "height" : n,        (numeric) height of the chain tip
    "hash" : "hex",      (string) block hash of the tip
    "branchlen" : n,     (numeric) zero for main chain, otherwise length of branch connecting the tip to the main chain
    "status" : "str"     (string) status of the chain, "active" for the main chain
                         Possible values for status:
                         1.  "invalid"               This branch contains at least one invalid block
                         2.  "headers-only"          Not all blocks for this branch are available, but the headers are valid
                         3.  "valid-headers"         All blocks are available for this branch, but they were never fully validated
                         4.  "valid-fork"            This branch is not part of the active chain, but is fully validated
                         5.  "active"                This is the tip of the active main chain, which is certainly valid
  },
  ...
]

Examples:
> bitcoin-cli getchaintips 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getchaintips", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getchaintxstats

```
getchaintxstats ( nblocks "blockhash" )

Compute statistics about the total number and rate of transactions in the chain.

Arguments:
1. nblocks      (numeric, optional, default=one month) Size of the window in number of blocks
2. blockhash    (string, optional, default=chain tip) The hash of the block that ends the window.

Result:
{                                       (json object)
  "time" : xxx,                         (numeric) The timestamp for the final block in the window, expressed in UNIX epoch time
  "txcount" : n,                        (numeric, optional) The total number of transactions in the chain up to that point, if known. It may be unknown when using assumeutxo.
  "window_final_block_hash" : "hex",    (string) The hash of the final block in the window
  "window_final_block_height" : n,      (numeric) The height of the final block in the window.
  "window_block_count" : n,             (numeric) Size of the window in number of blocks
  "window_interval" : n,                (numeric, optional) The elapsed time in the window in seconds. Only returned if "window_block_count" is > 0
  "window_tx_count" : n,                (numeric, optional) The number of transactions in the window. Only returned if "window_block_count" is > 0 and if txcount exists for the start and end of the window.
  "txrate" : n                          (numeric, optional) The average rate of transactions per second in the window. Only returned if "window_interval" is > 0 and if window_tx_count exists.
}

Examples:
> bitcoin-cli getchaintxstats 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getchaintxstats", "params": [2016]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getdeploymentinfo

```
getdeploymentinfo ( "blockhash" )

Returns an object containing various state info regarding deployments of consensus changes.
Consensus changes for which the new rules are enforced from genesis are not listed in "deployments".

Arguments:
1. blockhash    (string, optional, default="hash of current chain tip") The block hash at which to query deployment state

Result:
{                                       (json object)
  "hash" : "str",                       (string) requested block hash (or tip)
  "height" : n,                         (numeric) requested block height (or tip)
  "script_flags" : [                    (json array) script verify flags for the block
    "str",                              (string) a script verify flag
    ...
  ],
  "deployments" : {                     (json object)
    "xxxx" : {                          (json object) name of the deployment
      "type" : "str",                   (string) one of "buried", "bip9"
      "height" : n,                     (numeric, optional) height of the first block which the rules are or will be enforced (only for "buried" type, or "bip9" type with "active" status)
      "active" : true|false,            (boolean) true if the rules are enforced for the mempool and the next block
      "bip9" : {                        (json object, optional) status of bip9 softforks (only for "bip9" type)
        "bit" : n,                      (numeric, optional) the bit (0-28) in the block version field used to signal this softfork (only for "started" and "locked_in" status)
        "start_time" : xxx,             (numeric) the minimum median time past of a block at which the bit gains its meaning
        "timeout" : xxx,                (numeric) the median time past of a block at which the deployment is considered failed if not yet locked in
        "min_activation_height" : n,    (numeric) minimum height of blocks for which the rules may be enforced
        "status" : "str",               (string) status of deployment at specified block (one of "defined", "started", "locked_in", "active", "failed")
        "since" : n,                    (numeric) height of the first block to which the status applies
        "status_next" : "str",          (string) status of deployment at the next block
        "statistics" : {                (json object, optional) numeric statistics about signalling for a softfork (only for "started" and "locked_in" status)
          "period" : n,                 (numeric) the length in blocks of the signalling period
          "threshold" : n,              (numeric, optional) the number of blocks with the version bit set required to activate the feature (only for "started" status)
          "elapsed" : n,                (numeric) the number of blocks elapsed since the beginning of the current period
          "count" : n,                  (numeric) the number of blocks with the version bit set in the current period
          "possible" : true|false       (boolean, optional) returns false if there are not enough blocks left in this period to pass activation threshold (only for "started" status)
        },
        "signalling" : "str"            (string, optional) indicates blocks that signalled with a # and blocks that did not with a -
      }
    },
    ...
  }
}

Examples:
> bitcoin-cli getdeploymentinfo 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getdeploymentinfo", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getdescriptoractivity

```
getdescriptoractivity ["blockhash",...] [scanobjects,...] ( include_mempool )

Get spend and receive activity associated with a set of descriptors for a set of blocks. This command pairs well with the `relevant_blocks` output of `scanblocks()`.
This call may take several minutes. If you encounter timeouts, try specifying no RPC timeout (bitcoin-cli -rpcclienttimeout=0)

Arguments:
1. blockhashes                   (json array, required) The list of blockhashes to examine for activity. Order doesn't matter. Must be along main chain or an error is thrown.
                                 
     [
       "blockhash",              (string) A valid blockhash
       ...
     ]
2. scanobjects                   (json array, required) The list of descriptors (scan objects) to examine for activity. Every scan object is either a string descriptor or an object:
     [
       "descriptor",             (string) An output descriptor
       {                         (json object) An object with output descriptor and metadata
         "desc": "str",          (string, required) An output descriptor
         "range": n or [n,n],    (numeric or array, optional, default=1000) The range of HD chain indexes to explore (either end or [begin,end])
       },
       ...
     ]
3. include_mempool               (boolean, optional, default=true) Whether to include unconfirmed activity

Result:
{                                (json object)
  "activity" : [                 (json array) events
    {                            (json object)
      "type" : "str",            (string) always 'spend'
      "amount" : n,              (numeric) The total amount in BTC of the spent output
      "blockhash" : "hex",       (string, optional) The blockhash this spend appears in (omitted if unconfirmed)
      "height" : n,              (numeric, optional) Height of the spend (omitted if unconfirmed)
      "spend_txid" : "hex",      (string) The txid of the spending transaction
      "spend_vin" : n,           (numeric) The input index of the spend
      "prevout_txid" : "hex",    (string) The txid of the prevout
      "prevout_vout" : n,        (numeric) The vout of the prevout
      "prevout_spk" : {          (json object)
        "asm" : "str",           (string) Disassembly of the output script
        "desc" : "str",          (string) Inferred descriptor for the output
        "hex" : "hex",           (string) The raw output script bytes, hex-encoded
        "address" : "str",       (string, optional) The Bitcoin address (only if a well-defined address exists)
        "type" : "str"           (string) The type (one of: nonstandard, anchor, pubkey, pubkeyhash, scripthash, multisig, nulldata, witness_v0_scripthash, witness_v0_keyhash, witness_v1_taproot, witness_unknown)
      }
    },
    {                            (json object)
      "type" : "str",            (string) always 'receive'
      "amount" : n,              (numeric) The total amount in BTC of the new output
      "blockhash" : "hex",       (string, optional) The block that this receive is in (omitted if unconfirmed)
      "height" : n,              (numeric, optional) The height of the receive (omitted if unconfirmed)
      "txid" : "hex",            (string) The txid of the receiving transaction
      "vout" : n,                (numeric) The vout of the receiving output
      "output_spk" : {           (json object)
        "asm" : "str",           (string) Disassembly of the output script
        "desc" : "str",          (string) Inferred descriptor for the output
        "hex" : "hex",           (string) The raw output script bytes, hex-encoded
        "address" : "str",       (string, optional) The Bitcoin address (only if a well-defined address exists)
        "type" : "str"           (string) The type (one of: nonstandard, anchor, pubkey, pubkeyhash, scripthash, multisig, nulldata, witness_v0_scripthash, witness_v0_keyhash, witness_v1_taproot, witness_unknown)
      }
    },
    ...
  ]
}

Examples:
> bitcoin-cli getdescriptoractivity '["000000000000000000001347062c12fded7c528943c8ce133987e2e2f5a840ee"]' '["addr(bc1qzl6nsgqzu89a66l50cvwapnkw5shh23zarqkw9)"]'
```

### getdifficulty

```
getdifficulty

Returns the proof-of-work difficulty as a multiple of the minimum difficulty.

Result:
n    (numeric) the proof-of-work difficulty as a multiple of the minimum difficulty.

Examples:
> bitcoin-cli getdifficulty 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getdifficulty", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getmempoolancestors

```
getmempoolancestors "txid" ( verbose )

If txid is in the mempool, returns all in-mempool ancestors.

Arguments:
1. txid       (string, required) The transaction id (must be in mempool)
2. verbose    (boolean, optional, default=false) True for a json object, false for array of transaction ids

Result (for verbose = false):
[           (json array)
  "hex",    (string) The transaction id of an in-mempool ancestor transaction
  ...
]

Result (for verbose = true):
{                                  (json object)
  "transactionid" : {              (json object)
    "vsize" : n,                   (numeric) (DEPRECATED) Was previously erroneously described as the BIP 141 vsize, but is actually sigops-adjusted vsize.
                                   Use vsize_bip141 to actually get that behavior or switch to the explicit vsize_adjusted for retained behavior.
    "vsize_bip141" : n,            (numeric) Virtual transaction size as defined in BIP 141.
                                   This is different from actual serialized size for witness transactions as witness data is discounted.
    "vsize_adjusted" : n,          (numeric) Maximum of sigop-adjusted size (-bytespersigop) and virtual transaction size as defined in BIP 141.
    "weight" : n,                  (numeric) transaction weight as defined in BIP 141.
    "time" : xxx,                  (numeric) local time transaction entered pool in seconds since 1 Jan 1970 GMT
    "height" : n,                  (numeric) block height when transaction entered pool
    "descendantcount" : n,         (numeric) number of in-mempool descendant transactions (including this one)
    "descendantsize" : n,          (numeric) virtual transaction size of in-mempool descendants (including this one)
    "ancestorcount" : n,           (numeric) number of in-mempool ancestor transactions (including this one)
    "ancestorsize" : n,            (numeric) virtual transaction size of in-mempool ancestors (including this one)
    "chunkweight" : n,             (numeric) sigops-adjusted weight (as defined in BIP 141 and modified by '-bytespersigop') of this transaction's chunk
    "wtxid" : "hex",               (string) hash of serialized transaction, including witness data
    "fees" : {                     (json object)
      "base" : n,                  (numeric) transaction fee, denominated in BTC
      "modified" : n,              (numeric) transaction fee with fee deltas used for mining priority, denominated in BTC
      "ancestor" : n,              (numeric) transaction fees of in-mempool ancestors (including this one) with fee deltas used for mining priority, denominated in BTC
      "descendant" : n,            (numeric) transaction fees of in-mempool descendants (including this one) with fee deltas used for mining priority, denominated in BTC
      "chunk" : n                  (numeric) transaction fees of chunk, denominated in BTC
    },
    "depends" : [                  (json array) unconfirmed transactions used as inputs for this transaction
      "hex",                       (string) parent transaction id
      ...
    ],
    "spentby" : [                  (json array) unconfirmed transactions spending outputs from this transaction
      "hex",                       (string) child transaction id
      ...
    ],
    "unbroadcast" : true|false     (boolean) Whether this transaction is currently unbroadcast (initial broadcast not yet acknowledged by any peers)
  },
  ...
}

Examples:
> bitcoin-cli getmempoolancestors "mytxid"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getmempoolancestors", "params": ["mytxid"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getmempoolcluster

```
getmempoolcluster "txid"

Returns mempool data for given cluster

Arguments:
1. txid    (string, required) The txid of a transaction in the cluster

Result:
{                           (json object)
  "clusterweight" : n,      (numeric) total sigops-adjusted weight (as defined in BIP 141 and modified by '-bytespersigop')
  "txcount" : n,            (numeric) number of transactions
  "chunks" : [              (json array) chunks in this cluster (in mining order)
    {                       (json object)
      "chunkfee" : n,       (numeric) fees of the transactions in this chunk
      "chunkweight" : n,    (numeric) sigops-adjusted weight of all transactions in this chunk
      "txs" : [             (json array) transactions in this chunk in mining order
        "hex",              (string) transaction id
        ...
      ]
    },
    ...
  ]
}

Examples:
> bitcoin-cli getmempoolcluster txid
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getmempoolcluster", "params": ["txid"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getmempooldescendants

```
getmempooldescendants "txid" ( verbose )

If txid is in the mempool, returns all in-mempool descendants.

Arguments:
1. txid       (string, required) The transaction id (must be in mempool)
2. verbose    (boolean, optional, default=false) True for a json object, false for array of transaction ids

Result (for verbose = false):
[           (json array)
  "hex",    (string) The transaction id of an in-mempool descendant transaction
  ...
]

Result (for verbose = true):
{                                  (json object)
  "transactionid" : {              (json object)
    "vsize" : n,                   (numeric) (DEPRECATED) Was previously erroneously described as the BIP 141 vsize, but is actually sigops-adjusted vsize.
                                   Use vsize_bip141 to actually get that behavior or switch to the explicit vsize_adjusted for retained behavior.
    "vsize_bip141" : n,            (numeric) Virtual transaction size as defined in BIP 141.
                                   This is different from actual serialized size for witness transactions as witness data is discounted.
    "vsize_adjusted" : n,          (numeric) Maximum of sigop-adjusted size (-bytespersigop) and virtual transaction size as defined in BIP 141.
    "weight" : n,                  (numeric) transaction weight as defined in BIP 141.
    "time" : xxx,                  (numeric) local time transaction entered pool in seconds since 1 Jan 1970 GMT
    "height" : n,                  (numeric) block height when transaction entered pool
    "descendantcount" : n,         (numeric) number of in-mempool descendant transactions (including this one)
    "descendantsize" : n,          (numeric) virtual transaction size of in-mempool descendants (including this one)
    "ancestorcount" : n,           (numeric) number of in-mempool ancestor transactions (including this one)
    "ancestorsize" : n,            (numeric) virtual transaction size of in-mempool ancestors (including this one)
    "chunkweight" : n,             (numeric) sigops-adjusted weight (as defined in BIP 141 and modified by '-bytespersigop') of this transaction's chunk
    "wtxid" : "hex",               (string) hash of serialized transaction, including witness data
    "fees" : {                     (json object)
      "base" : n,                  (numeric) transaction fee, denominated in BTC
      "modified" : n,              (numeric) transaction fee with fee deltas used for mining priority, denominated in BTC
      "ancestor" : n,              (numeric) transaction fees of in-mempool ancestors (including this one) with fee deltas used for mining priority, denominated in BTC
      "descendant" : n,            (numeric) transaction fees of in-mempool descendants (including this one) with fee deltas used for mining priority, denominated in BTC
      "chunk" : n                  (numeric) transaction fees of chunk, denominated in BTC
    },
    "depends" : [                  (json array) unconfirmed transactions used as inputs for this transaction
      "hex",                       (string) parent transaction id
      ...
    ],
    "spentby" : [                  (json array) unconfirmed transactions spending outputs from this transaction
      "hex",                       (string) child transaction id
      ...
    ],
    "unbroadcast" : true|false     (boolean) Whether this transaction is currently unbroadcast (initial broadcast not yet acknowledged by any peers)
  },
  ...
}

Examples:
> bitcoin-cli getmempooldescendants "mytxid"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getmempooldescendants", "params": ["mytxid"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getmempoolentry

```
getmempoolentry "txid"

Returns mempool data for given transaction

Arguments:
1. txid    (string, required) The transaction id (must be in mempool)

Result:
{                                (json object)
  "vsize" : n,                   (numeric) (DEPRECATED) Was previously erroneously described as the BIP 141 vsize, but is actually sigops-adjusted vsize.
                                 Use vsize_bip141 to actually get that behavior or switch to the explicit vsize_adjusted for retained behavior.
  "vsize_bip141" : n,            (numeric) Virtual transaction size as defined in BIP 141.
                                 This is different from actual serialized size for witness transactions as witness data is discounted.
  "vsize_adjusted" : n,          (numeric) Maximum of sigop-adjusted size (-bytespersigop) and virtual transaction size as defined in BIP 141.
  "weight" : n,                  (numeric) transaction weight as defined in BIP 141.
  "time" : xxx,                  (numeric) local time transaction entered pool in seconds since 1 Jan 1970 GMT
  "height" : n,                  (numeric) block height when transaction entered pool
  "descendantcount" : n,         (numeric) number of in-mempool descendant transactions (including this one)
  "descendantsize" : n,          (numeric) virtual transaction size of in-mempool descendants (including this one)
  "ancestorcount" : n,           (numeric) number of in-mempool ancestor transactions (including this one)
  "ancestorsize" : n,            (numeric) virtual transaction size of in-mempool ancestors (including this one)
  "chunkweight" : n,             (numeric) sigops-adjusted weight (as defined in BIP 141 and modified by '-bytespersigop') of this transaction's chunk
  "wtxid" : "hex",               (string) hash of serialized transaction, including witness data
  "fees" : {                     (json object)
    "base" : n,                  (numeric) transaction fee, denominated in BTC
    "modified" : n,              (numeric) transaction fee with fee deltas used for mining priority, denominated in BTC
    "ancestor" : n,              (numeric) transaction fees of in-mempool ancestors (including this one) with fee deltas used for mining priority, denominated in BTC
    "descendant" : n,            (numeric) transaction fees of in-mempool descendants (including this one) with fee deltas used for mining priority, denominated in BTC
    "chunk" : n                  (numeric) transaction fees of chunk, denominated in BTC
  },
  "depends" : [                  (json array) unconfirmed transactions used as inputs for this transaction
    "hex",                       (string) parent transaction id
    ...
  ],
  "spentby" : [                  (json array) unconfirmed transactions spending outputs from this transaction
    "hex",                       (string) child transaction id
    ...
  ],
  "unbroadcast" : true|false     (boolean) Whether this transaction is currently unbroadcast (initial broadcast not yet acknowledged by any peers)
}

Examples:
> bitcoin-cli getmempoolentry "mytxid"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getmempoolentry", "params": ["mytxid"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getmempoolinfo

```
getmempoolinfo

Returns details on the active state of the TX memory pool.

Result:
{                                       (json object)
  "loaded" : true|false,                (boolean) True if the initial load attempt of the persisted mempool finished
  "size" : n,                           (numeric) Current tx count
  "bytes" : n,                          (numeric) Sum of all virtual transaction sizes as defined in BIP 141. Differs from actual serialized size because witness data is discounted
  "usage" : n,                          (numeric) Total memory usage for the mempool
  "total_fee" : n,                      (numeric) Total fees for the mempool in BTC, ignoring modified fees through prioritisetransaction
  "maxmempool" : n,                     (numeric) Maximum memory usage for the mempool
  "mempoolminfee" : n,                  (numeric) Minimum fee rate in BTC/kvB for tx to be accepted. Is the maximum of minrelaytxfee and minimum mempool fee
  "minrelaytxfee" : n,                  (numeric) Current minimum relay fee for transactions
  "incrementalrelayfee" : n,            (numeric) minimum fee rate increment for mempool limiting or replacement in BTC/kvB
  "unbroadcastcount" : n,               (numeric) Current number of transactions that haven't passed initial broadcast yet
  "permitbaremultisig" : true|false,    (boolean) True if the mempool accepts transactions with bare multisig outputs
  "maxdatacarriersize" : n,             (numeric) Maximum number of bytes that can be used by OP_RETURN outputs in the mempool
  "limitclustercount" : n,              (numeric) Maximum number of transactions that can be in a cluster (configured by -limitclustercount)
  "limitclustersize" : n,               (numeric) Maximum size of a cluster in virtual bytes (configured by -limitclustersize)
  "optimal" : true|false                (boolean) If the mempool is in a known-optimal transaction ordering
}

Examples:
> bitcoin-cli getmempoolinfo 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getmempoolinfo", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getrawmempool

```
getrawmempool ( verbose mempool_sequence )

Returns all transaction ids in memory pool as a json array of string transaction ids.

Hint: use getmempoolentry to fetch a specific transaction from the mempool.

Arguments:
1. verbose             (boolean, optional, default=false) True for a json object, false for array of transaction ids
2. mempool_sequence    (boolean, optional, default=false) If verbose=false, returns a json object with transaction list and mempool sequence number attached.

Result (for verbose = false):
[           (json array)
  "hex",    (string) The transaction id
  ...
]

Result (for verbose = true):
{                                  (json object)
  "transactionid" : {              (json object)
    "vsize" : n,                   (numeric) (DEPRECATED) Was previously erroneously described as the BIP 141 vsize, but is actually sigops-adjusted vsize.
                                   Use vsize_bip141 to actually get that behavior or switch to the explicit vsize_adjusted for retained behavior.
    "vsize_bip141" : n,            (numeric) Virtual transaction size as defined in BIP 141.
                                   This is different from actual serialized size for witness transactions as witness data is discounted.
    "vsize_adjusted" : n,          (numeric) Maximum of sigop-adjusted size (-bytespersigop) and virtual transaction size as defined in BIP 141.
    "weight" : n,                  (numeric) transaction weight as defined in BIP 141.
    "time" : xxx,                  (numeric) local time transaction entered pool in seconds since 1 Jan 1970 GMT
    "height" : n,                  (numeric) block height when transaction entered pool
    "descendantcount" : n,         (numeric) number of in-mempool descendant transactions (including this one)
    "descendantsize" : n,          (numeric) virtual transaction size of in-mempool descendants (including this one)
    "ancestorcount" : n,           (numeric) number of in-mempool ancestor transactions (including this one)
    "ancestorsize" : n,            (numeric) virtual transaction size of in-mempool ancestors (including this one)
    "chunkweight" : n,             (numeric) sigops-adjusted weight (as defined in BIP 141 and modified by '-bytespersigop') of this transaction's chunk
    "wtxid" : "hex",               (string) hash of serialized transaction, including witness data
    "fees" : {                     (json object)
      "base" : n,                  (numeric) transaction fee, denominated in BTC
      "modified" : n,              (numeric) transaction fee with fee deltas used for mining priority, denominated in BTC
      "ancestor" : n,              (numeric) transaction fees of in-mempool ancestors (including this one) with fee deltas used for mining priority, denominated in BTC
      "descendant" : n,            (numeric) transaction fees of in-mempool descendants (including this one) with fee deltas used for mining priority, denominated in BTC
      "chunk" : n                  (numeric) transaction fees of chunk, denominated in BTC
    },
    "depends" : [                  (json array) unconfirmed transactions used as inputs for this transaction
      "hex",                       (string) parent transaction id
      ...
    ],
    "spentby" : [                  (json array) unconfirmed transactions spending outputs from this transaction
      "hex",                       (string) child transaction id
      ...
    ],
    "unbroadcast" : true|false     (boolean) Whether this transaction is currently unbroadcast (initial broadcast not yet acknowledged by any peers)
  },
  ...
}

Result (for verbose = false and mempool_sequence = true):
{                            (json object)
  "txids" : [                (json array)
    "hex",                   (string) The transaction id
    ...
  ],
  "mempool_sequence" : n     (numeric) The mempool sequence value.
}

Examples:
> bitcoin-cli getrawmempool true
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getrawmempool", "params": [true]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### gettxout

```
gettxout "txid" n ( include_mempool )

Returns details about an unspent transaction output.

Arguments:
1. txid               (string, required) The transaction id
2. n                  (numeric, required) vout number
3. include_mempool    (boolean, optional, default=true) Whether to include the mempool. Note that an unspent output that is spent in the mempool won't appear.

Result (If the UTXO was not found):
null    (json null)

Result (Otherwise):
{                             (json object)
  "bestblock" : "hex",        (string) The hash of the block at the tip of the chain
  "confirmations" : n,        (numeric) The number of confirmations
  "value" : n,                (numeric) The transaction value in BTC
  "scriptPubKey" : {          (json object)
    "asm" : "str",            (string) Disassembly of the output script
    "desc" : "str",           (string) Inferred descriptor for the output
    "hex" : "hex",            (string) The raw output script bytes, hex-encoded
    "type" : "str",           (string) The type, eg pubkeyhash
    "address" : "str"         (string, optional) The Bitcoin address (only if a well-defined address exists)
  },
  "coinbase" : true|false     (boolean) Coinbase or not
}

Examples:

Get unspent transactions
> bitcoin-cli listunspent 

View the details
> bitcoin-cli gettxout "txid" 1

As a JSON-RPC call
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "gettxout", "params": ["txid", 1]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### gettxoutproof

```
gettxoutproof ["txid",...] ( "blockhash" )

Returns a hex-encoded proof that "txid" was included in a block.

NOTE: By default this function only works sometimes. This is when there is an
unspent output in the utxo for this transaction. To make it always work,
you need to maintain a transaction index, using the -txindex command line option or
specify the block in which the transaction is included manually (by blockhash).

Arguments:
1. txids          (json array, required) The txids to filter
     [
       "txid",    (string) A transaction hash
       ...
     ]
2. blockhash      (string, optional) If specified, looks for txid in the block with this hash

Result:
"str"    (string) A string that is a serialized, hex-encoded data for the proof.
```

### gettxoutsetinfo

```
gettxoutsetinfo ( "hash_type" hash_or_height use_index )

Returns statistics about the unspent transaction output set.
Note this call may take some time if you are not using coinstatsindex.

Arguments:
1. hash_type         (string, optional, default="hash_serialized_3") Which UTXO set hash should be calculated. Options: 'hash_serialized_3' (the legacy algorithm), 'muhash', 'none'.
2. hash_or_height    (string or numeric, optional, default=the current best block) The block hash or height of the target height (only available with coinstatsindex).
3. use_index         (boolean, optional, default=true) Use coinstatsindex, if available.

Result:
{                                     (json object)
  "height" : n,                       (numeric) The block height (index) of the returned statistics
  "bestblock" : "hex",                (string) The hash of the block at which these statistics are calculated
  "txouts" : n,                       (numeric) The number of unspent transaction outputs
  "bogosize" : n,                     (numeric) Database-independent, meaningless metric indicating the UTXO set size
  "hash_serialized_3" : "hex",        (string, optional) The serialized hash (only present if 'hash_serialized_3' hash_type is chosen)
  "muhash" : "hex",                   (string, optional) The serialized hash (only present if 'muhash' hash_type is chosen)
  "transactions" : n,                 (numeric, optional) The number of transactions with unspent outputs (not available when coinstatsindex is used)
  "disk_size" : n,                    (numeric, optional) The estimated size of the chainstate on disk (not available when coinstatsindex is used)
  "total_amount" : n,                 (numeric) The total amount of coins in the UTXO set
  "total_unspendable_amount" : n,     (numeric, optional) The total amount of coins permanently excluded from the UTXO set (only available if coinstatsindex is used)
  "block_info" : {                    (json object, optional) Info on amounts in the block at this block height (only available if coinstatsindex is used)
    "prevout_spent" : n,              (numeric) Total amount of all prevouts spent in this block
    "coinbase" : n,                   (numeric) Coinbase subsidy amount of this block
    "new_outputs_ex_coinbase" : n,    (numeric) Total amount of new outputs created by this block
    "unspendable" : n,                (numeric) Total amount of unspendable outputs created in this block
    "unspendables" : {                (json object) Detailed view of the unspendable categories
      "genesis_block" : n,            (numeric) The unspendable amount of the Genesis block subsidy
      "bip30" : n,                    (numeric) Transactions overridden by duplicates (no longer possible with BIP30)
      "scripts" : n,                  (numeric) Amounts sent to scripts that are unspendable (for example OP_RETURN outputs)
      "unclaimed_rewards" : n         (numeric) Fee rewards that miners did not claim in their coinbase transaction
    }
  }
}

Examples:
> bitcoin-cli gettxoutsetinfo 
> bitcoin-cli gettxoutsetinfo "none"
> bitcoin-cli gettxoutsetinfo "none" 1000
> bitcoin-cli gettxoutsetinfo "none" '"00000000c937983704a73af28acdec37b049d214adbda81d7e2a3dd146f6ed09"'
> bitcoin-cli -named gettxoutsetinfo hash_type='muhash' use_index='false'
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "gettxoutsetinfo", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "gettxoutsetinfo", "params": ["none"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "gettxoutsetinfo", "params": ["none", 1000]}' -H 'content-type: application/json' http://127.0.0.1:8332/
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "gettxoutsetinfo", "params": ["none", "00000000c937983704a73af28acdec37b049d214adbda81d7e2a3dd146f6ed09"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### gettxspendingprevout

```
gettxspendingprevout [{"txid":"hex","vout":n},...] ( {"mempool_only":bool,"return_spending_tx":bool,...} )

Scans the mempool (and the txospenderindex, if available) to find transactions spending any of the given outputs

Arguments:
1. outputs                 (json array, required) The transaction outputs that we want to check, and within each, the txid (string) vout (numeric).
     [
       {                   (json object)
         "txid": "hex",    (string, required) The transaction id
         "vout": n,        (numeric, required) The output number
       },
       ...
     ]
2. options                 (json object, optional) Options object that can be used to pass named arguments, listed below.

Named Arguments:
mempool_only          (boolean, optional, default=true if txospenderindex unavailable, otherwise false) If false and mempool lacks a relevant spend, use txospenderindex (throws an exception if not available).
return_spending_tx    (boolean, optional, default=false) If true, return the full spending tx.

Result:
[                              (json array)
  {                            (json object)
    "txid" : "hex",            (string) the transaction id of the checked output
    "vout" : n,                (numeric) the vout value of the checked output
    "spendingtxid" : "hex",    (string, optional) the transaction id of the mempool transaction spending this output (omitted if unspent)
    "spendingtx" : "hex",      (string, optional) the transaction spending this output (only if return_spending_tx is set, omitted if unspent)
    "blockhash" : "hex"        (string, optional) the hash of the spending block (omitted if unspent or the spending tx is not confirmed)
  },
  ...
]

Examples:
> bitcoin-cli gettxspendingprevout "[{\"txid\":\"a08e6907dbbd3d809776dbfc5d82e371b764ed838b5655e72f463568df1aadf0\",\"vout\":3}]"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "gettxspendingprevout", "params": ["[{\"txid\":\"a08e6907dbbd3d809776dbfc5d82e371b764ed838b5655e72f463568df1aadf0\",\"vout\":3}]"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
> bitcoin-cli -named gettxspendingprevout outputs='[{"txid":"a08e6907dbbd3d809776dbfc5d82e371b764ed838b5655e72f463568df1aadf0","vout":3}]' return_spending_tx=true
```

### importmempool

```
importmempool "filepath" ( options )

Import a mempool.dat file and attempt to add its contents to the mempool.
Warning: Importing untrusted files is dangerous, especially if metadata from the file is taken over.

Arguments:
1. filepath    (string, required) The mempool file
2. options     (json object, optional) Options object that can be used to pass named arguments, listed below.

Named Arguments:
use_current_time            (boolean, optional, default=true) Whether to use the current system time or use the entry time metadata from the mempool file.
                            Warning: Importing untrusted metadata may lead to unexpected issues and undesirable behavior.
apply_fee_delta_priority    (boolean, optional, default=false) Whether to apply the fee delta metadata from the mempool file.
                            It will be added to any existing fee deltas.
                            The fee delta can be set by the prioritisetransaction RPC.
                            Warning: Importing untrusted metadata may lead to unexpected issues and undesirable behavior.
                            Only set this bool if you understand what it does.
apply_unbroadcast_set       (boolean, optional, default=false) Whether to apply the unbroadcast set metadata from the mempool file.
                            Warning: Importing untrusted metadata may lead to unexpected issues and undesirable behavior.

Result:
{}    (empty JSON object)

Examples:
> bitcoin-cli importmempool /path/to/mempool.dat
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "importmempool", "params": ["/path/to/mempool.dat"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### loadtxoutset

```
loadtxoutset "path"

Load the serialized UTXO set from a file.
Once this snapshot is loaded, its contents will be deserialized into a second chainstate data structure, which is then used to sync to the network's tip. Meanwhile, the original chainstate will complete the initial block download process in the background, eventually validating up to the block that the snapshot is based upon.

The result is a usable bitcoind instance that is current with the network tip in a matter of minutes rather than hours. UTXO snapshot are typically obtained from third-party sources (HTTP, torrent, etc.) which is reasonable since their contents are always checked by hash.

You can find more information on this process in the `assumeutxo` design document (<https://github.com/bitcoin/bitcoin/blob/master/doc/design/assumeutxo.md>).

Arguments:
1. path    (string, required) path to the snapshot file. If relative, will be prefixed by datadir.

Result:
{                        (json object)
  "coins_loaded" : n,    (numeric) the number of coins loaded from the snapshot
  "tip_hash" : "hex",    (string) the hash of the base of the snapshot
  "base_height" : n,     (numeric) the height of the base of the snapshot
  "path" : "str"         (string) the absolute path that the snapshot was loaded from
}

Examples:
> bitcoin-cli -rpcclienttimeout=0 loadtxoutset utxo.dat
```

### preciousblock

```
preciousblock "blockhash"

Treats a block as if it were received before others with the same work.

A later preciousblock call can override the effect of an earlier one.

The effects of preciousblock are not retained across restarts.

Arguments:
1. blockhash    (string, required) the hash of the block to mark as precious

Result:
null    (json null)

Examples:
> bitcoin-cli preciousblock "blockhash"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "preciousblock", "params": ["blockhash"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### pruneblockchain

```
pruneblockchain height

Attempts to delete block and undo data up to a specified height or timestamp, if eligible for pruning.
Requires `-prune` to be enabled at startup. While pruned data may be re-fetched in some cases (e.g., via `getblockfrompeer`), local deletion is irreversible.

Arguments:
1. height    (numeric, required) The block height to prune up to. May be set to a discrete height, or to a UNIX epoch time
             to prune blocks whose block time is at least 2 hours older than the provided timestamp.

Result:
n    (numeric) Height of the last block pruned

Examples:
> bitcoin-cli pruneblockchain 1000
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "pruneblockchain", "params": [1000]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### savemempool

```
savemempool

Dumps the mempool to disk. It will fail until the previous dump is fully loaded.

Result:
{                        (json object)
  "filename" : "str"     (string) the directory and file where the mempool was saved
}

Examples:
> bitcoin-cli savemempool 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "savemempool", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### scanblocks

```
scanblocks "action" ( [scanobjects,...] start_height stop_height "filtertype" options )

Return relevant blockhashes for given descriptors (requires blockfilterindex).
This call may take several minutes. Make sure to use no RPC timeout (bitcoin-cli -rpcclienttimeout=0)

Arguments:
1. action                        (string, required) The action to execute
                                 "start" for starting a scan
                                 "abort" for aborting the current scan (returns true when abort was successful)
                                 "status" for progress report (in %) of the current scan
2. scanobjects                   (json array, optional) Array of scan objects. Required for "start" action
                                 Every scan object is either a string descriptor or an object:
     [
       "descriptor",             (string) An output descriptor
       {                         (json object) An object with output descriptor and metadata
         "desc": "str",          (string, required) An output descriptor
         "range": n or [n,n],    (numeric or array, optional, default=1000) The range of HD chain indexes to explore (either end or [begin,end])
       },
       ...
     ]
3. start_height                  (numeric, optional, default=0) Height to start to scan from
4. stop_height                   (numeric, optional, default=chain tip) Height to stop to scan
5. filtertype                    (string, optional, default="basic") The type name of the filter
6. options                       (json object, optional) Options object that can be used to pass named arguments, listed below.

Named Arguments:
filter_false_positives    (boolean, optional, default=false) Filter false positives (slower and may fail on pruned nodes). Otherwise they may occur at a rate of 1/M

Result (when action=='status' and no scan is in progress - possibly already completed):
null    (json null)

Result (When action=='start'; only returns after scan completes):
{                              (json object)
  "from_height" : n,           (numeric) The height we started the scan from
  "to_height" : n,             (numeric) The height we ended the scan at
  "relevant_blocks" : [        (json array) Blocks that may have matched a scanobject.
    "hex",                     (string) A relevant blockhash
    ...
  ],
  "completed" : true|false     (boolean) true if the scan process was not aborted
}

Result (when action=='status' and a scan is currently in progress):
{                          (json object)
  "progress" : n,          (numeric) Approximate percent complete
  "current_height" : n     (numeric) Height of the block currently being scanned
}

Result (when action=='abort'):
true|false    (boolean) True if scan will be aborted (not necessarily before this RPC returns), or false if there is no scan to abort

Examples:
> bitcoin-cli scanblocks start '["addr(bcrt1q4u4nsgk6ug0sqz7r3rj9tykjxrsl0yy4d0wwte)"]' 300000
> bitcoin-cli scanblocks start '["addr(bcrt1q4u4nsgk6ug0sqz7r3rj9tykjxrsl0yy4d0wwte)"]' 100 150 basic
> bitcoin-cli scanblocks status
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "scanblocks", "params": ["start", ["addr(bcrt1q4u4nsgk6ug0sqz7r3rj9tykjxrsl0yy4d0wwte)"], 300000]}' -H 'content-type: application/json' http://127.0.0.1:8332/
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "scanblocks", "params": ["start", ["addr(bcrt1q4u4nsgk6ug0sqz7r3rj9tykjxrsl0yy4d0wwte)"], 100, 150, "basic"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "scanblocks", "params": ["status"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### scantxoutset

```
scantxoutset "action" ( [scanobjects,...] )

Scans the unspent transaction output set for entries that match certain output descriptors.
Examples of output descriptors are:
    addr(<address>)                      Outputs whose output script corresponds to the specified address (does not include P2PK)
    raw(<hex script>)                    Outputs whose output script equals the specified hex-encoded bytes
    combo(<pubkey>)                      P2PK, P2PKH, P2WPKH, and P2SH-P2WPKH outputs for the given pubkey
    pkh(<pubkey>)                        P2PKH outputs for the given pubkey
    sh(multi(<n>,<pubkey>,<pubkey>,...)) P2SH-multisig outputs for the given threshold and pubkeys
    tr(<pubkey>)                         P2TR
    tr(<pubkey>,{pk(<pubkey>)})          P2TR with single fallback pubkey in tapscript
    rawtr(<pubkey>)                      P2TR with the specified key as output key rather than inner
    wsh(and_v(v:pk(<pubkey>),after(2)))  P2WSH miniscript with mandatory pubkey and a timelock

In the above, <pubkey> either refers to a fixed public key in hexadecimal notation, or to an xpub/xprv optionally followed by one
or more path elements separated by "/", and optionally ending in "/*" (unhardened), or "/*'" or "/*h" (hardened) to specify all
unhardened or hardened child keys.
In the latter case, a range needs to be specified by below if different from 1000.
For more information on output descriptors, see the documentation in the doc/descriptors.md file.

Arguments:
1. action                        (string, required) The action to execute
                                 "start" for starting a scan
                                 "abort" for aborting the current scan (returns true when abort was successful)
                                 "status" for progress report (in %) of the current scan
2. scanobjects                   (json array, optional) Array of scan objects. Required for "start" action
                                 Every scan object is either a string descriptor or an object:
     [
       "descriptor",             (string) An output descriptor
       {                         (json object) An object with output descriptor and metadata
         "desc": "str",          (string, required) An output descriptor
         "range": n or [n,n],    (numeric or array, optional, default=1000) The range of HD chain indexes to explore (either end or [begin,end])
       },
       ...
     ]

Result (when action=='start'; only returns after scan completes):
{                                 (json object)
  "success" : true|false,         (boolean) Whether the scan was completed
  "txouts" : n,                   (numeric) The number of unspent transaction outputs scanned
  "height" : n,                   (numeric) The block height at which the scan was done
  "bestblock" : "hex",            (string) The hash of the block at the tip of the chain
  "unspents" : [                  (json array)
    {                             (json object)
      "txid" : "hex",             (string) The transaction id
      "vout" : n,                 (numeric) The vout value
      "scriptPubKey" : "hex",     (string) The output script
      "desc" : "str",             (string) A specialized descriptor for the matched output script
      "amount" : n,               (numeric) The total amount in BTC of the unspent output
      "coinbase" : true|false,    (boolean) Whether this is a coinbase output
      "height" : n,               (numeric) Height of the unspent transaction output
      "blockhash" : "hex",        (string) Blockhash of the unspent transaction output
      "confirmations" : n         (numeric) Number of confirmations of the unspent transaction output when the scan was done
    },
    ...
  ],
  "total_amount" : n              (numeric) The total amount of all found unspent outputs in BTC
}

Result (when action=='abort'):
true|false    (boolean) True if scan will be aborted (not necessarily before this RPC returns), or false if there is no scan to abort

Result (when action=='status' and a scan is currently in progress):
{                    (json object)
  "progress" : n     (numeric) Approximate percent complete
}

Result (when action=='status' and no scan is in progress - possibly already completed):
null    (json null)

Examples:
> bitcoin-cli scantxoutset start '["raw(76a91411b366edfc0a8b66feebae5c2e25a7b6a5d1cf3188ac)#fm24fxxy"]'
> bitcoin-cli scantxoutset status
> bitcoin-cli scantxoutset abort
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "scantxoutset", "params": ["start", ["raw(76a91411b366edfc0a8b66feebae5c2e25a7b6a5d1cf3188ac)#fm24fxxy"]]}' -H 'content-type: application/json' http://127.0.0.1:8332/
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "scantxoutset", "params": ["status"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "scantxoutset", "params": ["abort"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### verifychain

```
verifychain ( checklevel nblocks )

Verifies blockchain database.

Arguments:
1. checklevel    (numeric, optional, default=3, range=0-4) How thorough the block verification is:
                 - level 0 reads the blocks from disk
                 - level 1 verifies block validity
                 - level 2 verifies undo data
                 - level 3 checks disconnection of tip blocks
                 - level 4 tries to reconnect the blocks
                 - each level includes the checks of the previous levels
2. nblocks       (numeric, optional, default=6, 0=all) The number of blocks to check.

Result:
true|false    (boolean) Verification finished successfully. If false, check debug log for reason.

Examples:
> bitcoin-cli verifychain 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "verifychain", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### verifytxoutproof

```
verifytxoutproof "proof"

Verifies that a proof points to a transaction in a block, returning the transaction it commits to
and throwing an RPC error if the block is not in our best chain

Arguments:
1. proof    (string, required) The hex-encoded proof generated by gettxoutproof

Result:
[           (json array)
  "hex",    (string) The txid(s) which the proof commits to, or empty array if the proof cannot be validated.
  ...
]
```

### waitforblock

```
waitforblock "blockhash" ( timeout )

Waits for a specific new block and returns useful info about it.

Returns the current block on timeout or exit.

Make sure to use no RPC timeout (bitcoin-cli -rpcclienttimeout=0)

Arguments:
1. blockhash    (string, required) Block hash to wait for.
2. timeout      (numeric, optional, default=0) Time in milliseconds to wait for a response. 0 indicates no timeout.

Result:
{                    (json object)
  "hash" : "hex",    (string) The blockhash
  "height" : n       (numeric) Block height
}

Examples:
> bitcoin-cli waitforblock "0000000000079f8ef3d2c688c244eb7a4570b24c9ed7b4a8c619eb02596f8862" 1000
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "waitforblock", "params": ["0000000000079f8ef3d2c688c244eb7a4570b24c9ed7b4a8c619eb02596f8862", 1000]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### waitforblockheight

```
waitforblockheight height ( timeout )

Waits for (at least) block height and returns the height and hash
of the current tip.

Returns the current block on timeout or exit.

Make sure to use no RPC timeout (bitcoin-cli -rpcclienttimeout=0)

Arguments:
1. height     (numeric, required) Block height to wait for.
2. timeout    (numeric, optional, default=0) Time in milliseconds to wait for a response. 0 indicates no timeout.

Result:
{                    (json object)
  "hash" : "hex",    (string) The blockhash
  "height" : n       (numeric) Block height
}

Examples:
> bitcoin-cli waitforblockheight 100 1000
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "waitforblockheight", "params": [100, 1000]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### waitfornewblock

```
waitfornewblock ( timeout "current_tip" )

Waits for any new block and returns useful info about it.

Returns the current block on timeout or exit.

Make sure to use no RPC timeout (bitcoin-cli -rpcclienttimeout=0)

Arguments:
1. timeout        (numeric, optional, default=0) Time in milliseconds to wait for a response. 0 indicates no timeout.
2. current_tip    (string, optional) Method waits for the chain tip to differ from this.

Result:
{                    (json object)
  "hash" : "hex",    (string) The blockhash
  "height" : n       (numeric) Block height
}

Examples:
> bitcoin-cli waitfornewblock 1000
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "waitfornewblock", "params": [1000]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```


## Control

### getmemoryinfo

```
getmemoryinfo ( "mode" )

Returns an object containing information about memory usage.

Arguments:
1. mode    (string, optional, default="stats") determines what kind of information is returned.
           - "stats" returns general statistics about memory usage in the daemon.
           - "mallocinfo" returns an XML string describing low-level heap state (only available if compiled with glibc).

Result (mode "stats"):
{                         (json object)
  "locked" : {            (json object) Information about locked memory manager
    "used" : n,           (numeric) Number of bytes used
    "free" : n,           (numeric) Number of bytes available in current arenas
    "total" : n,          (numeric) Total number of bytes managed
    "locked" : n,         (numeric) Amount of bytes that succeeded locking. If this number is smaller than total, locking pages failed at some point and key data could be swapped to disk.
    "chunks_used" : n,    (numeric) Number allocated chunks
    "chunks_free" : n     (numeric) Number unused chunks
  }
}

Result (mode "mallocinfo"):
"str"    (string) "<malloc version="1">..."

Examples:
> bitcoin-cli getmemoryinfo 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getmemoryinfo", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getopenrpcinfo

```
getopenrpcinfo ( show_hidden )

Returns an OpenRPC document for currently available RPC commands.

Arguments:
1. show_hidden    (boolean, optional, default=false) Also include hidden RPC commands and arguments.

Result:
{                                                      (json object)
  "openrpc" : "str",                                   (string) OpenRPC specification version.
  "info" : {                                           (json object) Metadata about this JSON-RPC interface.
    "title" : "str",                                   (string) API title.
    "version" : "str",                                 (string) Bitcoin Core version string.
    "description" : "str"                              (string) API description.
  },
  "methods" : [                                        (json array) Documented RPC methods.
    {                                                  (json object) An RPC method description object.
      "name" : "str",                                  (string) Method name.
      "description" : "str",                           (string) Method description.
      "params" : [                                     (json array) Method parameters.
        {                                              (json object) A parameter.
          "name" : "str",                              (string) Parameter name.
          "required" : true|false,                     (boolean) Whether the parameter is required.
          "schema" : xxx,                              (any) JSON Schema for the parameter.
          "description" : "str",                       (string, optional) Parameter description.
          "x-bitcoin-aliases" : [                      (json array, optional) Alternative parameter names.
            "str",                                     (string) An alias.
            ...
          ],
          "x-bitcoin-placeholder" : true|false,        (boolean, optional) Whether the parameter is retained only for compatibility.
          "x-bitcoin-also-positional" : true|false     (boolean, optional) Whether the parameter can also be passed positionally.
        },
        ...
      ],
      "result" : {                                     (json object) Method result.
        "name" : "str",                                (string) Result name.
        "schema" : xxx                                 (any) JSON Schema for the result. Numeric schemas may include "x-bitcoin-unit" property: "amount" which denotes a Bitcoin amount in BTC.
      },
      "x-bitcoin-category" : "str"                     (string) RPC category.
    },
    ...
  ]
}

Examples:
> bitcoin-cli getopenrpcinfo 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getopenrpcinfo", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getrpcinfo

```
getrpcinfo

Returns details of the RPC server.

Result:
{                          (json object)
  "active_commands" : [    (json array) All active commands
    {                      (json object) Information about an active command
      "method" : "str",    (string) The name of the RPC command
      "duration" : n       (numeric) The running time in microseconds
    },
    ...
  ],
  "logpath" : "str"        (string) The complete file path to the debug log
}

Examples:
> bitcoin-cli getrpcinfo 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getrpcinfo", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### help

```
help ( "command" )

List all commands, or get help for a specified command.

Arguments:
1. command    (string, optional, default=all commands) The command to get help on

Result:
"str"    (string) The help text
```

### logging

```
logging ( ["include_category",...] ["exclude_category",...] )

Gets and sets the logging configuration.
When called without an argument, returns the list of categories with status that are currently being debug logged or not.
When called with arguments, adds or removes categories from debug logging and return the lists above.
The arguments are evaluated in order "include", "exclude".
If an item is both included and excluded, it will thus end up being excluded.
The valid logging categories are: addrman, bench, blockstorage, cmpctblock, coindb, estimatefee, http, i2p, ipc, kernel, leveldb, mempool, mempoolrej, net, privatebroadcast, proxy, prune, qt, rand, reindex, rpc, scan, selectcoins, tor, txpackages, txreconciliation, validation, walletdb, zmq
In addition, the following are available as category names with special meanings:
  - "all",  "1" : represent all logging categories.

Arguments:
1. include                    (json array, optional) The categories to add to debug logging
     [
       "include_category",    (string) the valid logging category
       ...
     ]
2. exclude                    (json array, optional) The categories to remove from debug logging
     [
       "exclude_category",    (string) the valid logging category
       ...
     ]

Result:
{                             (json object) keys are the logging categories, and values indicates its status
  "category" : true|false,    (boolean) if being debug logged or not. false:inactive, true:active
  ...
}

Examples:
> bitcoin-cli logging "[\"all\"]" "[\"http\"]"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "logging", "params": [["all"], ["leveldb"]]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### rpc.discover

```
rpc.discover

Returns an OpenRPC schema as a description of this service.

Result:
{                                                      (json object)
  "openrpc" : "str",                                   (string) OpenRPC specification version.
  "info" : {                                           (json object) Metadata about this JSON-RPC interface.
    "title" : "str",                                   (string) API title.
    "version" : "str",                                 (string) Bitcoin Core version string.
    "description" : "str"                              (string) API description.
  },
  "methods" : [                                        (json array) Documented RPC methods.
    {                                                  (json object) An RPC method description object.
      "name" : "str",                                  (string) Method name.
      "description" : "str",                           (string) Method description.
      "params" : [                                     (json array) Method parameters.
        {                                              (json object) A parameter.
          "name" : "str",                              (string) Parameter name.
          "required" : true|false,                     (boolean) Whether the parameter is required.
          "schema" : xxx,                              (any) JSON Schema for the parameter.
          "description" : "str",                       (string, optional) Parameter description.
          "x-bitcoin-aliases" : [                      (json array, optional) Alternative parameter names.
            "str",                                     (string) An alias.
            ...
          ],
          "x-bitcoin-placeholder" : true|false,        (boolean, optional) Whether the parameter is retained only for compatibility.
          "x-bitcoin-also-positional" : true|false     (boolean, optional) Whether the parameter can also be passed positionally.
        },
        ...
      ],
      "result" : {                                     (json object) Method result.
        "name" : "str",                                (string) Result name.
        "schema" : xxx                                 (any) JSON Schema for the result. Numeric schemas may include "x-bitcoin-unit" property: "amount" which denotes a Bitcoin amount in BTC.
      },
      "x-bitcoin-category" : "str"                     (string) RPC category.
    },
    ...
  ]
}

Examples:
> bitcoin-cli rpc.discover 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "rpc.discover", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### stop

```
stop

Request a graceful shutdown of Bitcoin Core.

Result:
"str"    (string) A string with the content 'Bitcoin Core stopping'
```

### uptime

```
uptime

Returns the total uptime of the server.

Result:
n    (numeric) The number of seconds that the server has been running

Examples:
> bitcoin-cli uptime 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "uptime", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```


## Mining

### getblocktemplate

```
getblocktemplate {"mode":"str","capabilities":["str",...],"rules":["segwit","str",...],"longpollid":"str","data":"hex"}

If the request parameters include a 'mode' key, that is used to explicitly select between the default 'template' request or a 'proposal'.
It returns data needed to construct a block to work on.
For full specification, see BIPs 22, 23, 9, and 145:
    https://github.com/bitcoin/bips/blob/master/bip-0022.mediawiki
    https://github.com/bitcoin/bips/blob/master/bip-0023.mediawiki
    https://github.com/bitcoin/bips/blob/master/bip-0009.mediawiki#getblocktemplate_changes
    https://github.com/bitcoin/bips/blob/master/bip-0145.mediawiki

Arguments:
1. template_request            (json object, required) Format of the template
     {
       "mode": "str",          (string, optional) This must be set to "template", "proposal" (see BIP 23), or omitted
       "capabilities": [       (json array, optional) A list of strings
         "str",                (string) client side supported feature, 'longpoll', 'coinbasevalue', 'proposal', 'serverlist', 'workid'
         ...
       ],
       "rules": [              (json array, required) A list of strings
         "segwit",             (string, required) (literal) indicates client side segwit support
         "str",                (string) other client side supported softfork deployment
         ...
       ],
       "longpollid": "str",    (string, optional) delay processing request until the result would vary significantly from the "longpollid" of a prior template
       "data": "hex",          (string, optional) proposed block data to check, encoded in hexadecimal; valid only for mode="proposal"
     }

Result (If the proposal was accepted with mode=='proposal'):
null    (json null)

Result (If the proposal was not accepted with mode=='proposal'):
"str"    (string) According to BIP22

Result (Otherwise):
{                                          (json object)
  "version" : n,                           (numeric) The preferred block version
  "rules" : [                              (json array) specific block rules that are to be enforced
    "str",                                 (string) name of a rule the client must understand to some extent; see BIP 9 for format
    ...
  ],
  "vbavailable" : {                        (json object) set of pending, supported versionbit (BIP 9) softfork deployments
    "rulename" : n,                        (numeric) identifies the bit number as indicating acceptance and readiness for the named softfork rule
    ...
  },
  "capabilities" : [                       (json array)
    "str",                                 (string) A supported feature, for example 'proposal'
    ...
  ],
  "vbrequired" : n,                        (numeric) bit mask of versionbits the server requires set in submissions
  "previousblockhash" : "str",             (string) The hash of current highest block
  "transactions" : [                       (json array) contents of non-coinbase transactions that should be included in the next block
    {                                      (json object)
      "data" : "hex",                      (string) transaction data encoded in hexadecimal (byte-for-byte)
      "txid" : "hex",                      (string) transaction hash excluding witness data, shown in byte-reversed hex
      "hash" : "hex",                      (string) transaction hash including witness data, shown in byte-reversed hex
      "depends" : [                        (json array) array of numbers
        n,                                 (numeric) transactions before this one (by 1-based index in 'transactions' list) that must be present in the final block if this one is
        ...
      ],
      "fee" : n,                           (numeric) difference in value between transaction inputs and outputs (in satoshis); for coinbase transactions, this is a negative Number of the total collected block fees (ie, not including the block subsidy); if key is not present, fee is unknown and clients MUST NOT assume there isn't one
      "sigops" : n,                        (numeric) total SigOps cost, as counted for purposes of block limits; if key is not present, sigop cost is unknown and clients MUST NOT assume it is zero
      "weight" : n                         (numeric) total transaction weight, as counted for purposes of block limits
    },
    ...
  ],
  "coinbaseaux" : {                        (json object) data that should be included in the coinbase's scriptSig content
    "key" : "hex",                         (string) values must be in the coinbase (keys may be ignored)
    ...
  },
  "coinbasevalue" : n,                     (numeric) maximum allowable input to coinbase transaction, including the generation award and transaction fees (in satoshis)
  "longpollid" : "str",                    (string) an id to include with a request to longpoll on an update to this template
  "target" : "str",                        (string) The hash target
  "mintime" : xxx,                         (numeric) The minimum timestamp appropriate for the next block time, expressed in UNIX epoch time. Adjusted for the proposed BIP94 timewarp rule.
  "mutable" : [                            (json array) list of ways the block template may be changed
    "str",                                 (string) A way the block template may be changed, e.g. 'time', 'transactions', 'prevblock'
    ...
  ],
  "noncerange" : "hex",                    (string) A range of valid nonces
  "sigoplimit" : n,                        (numeric) limit of sigops in blocks
  "sizelimit" : n,                         (numeric) limit of block size
  "weightlimit" : n,                       (numeric, optional) limit of block weight
  "curtime" : xxx,                         (numeric) current timestamp in UNIX epoch time. Adjusted for the proposed BIP94 timewarp rule.
  "bits" : "str",                          (string) compressed target of next block
  "height" : n,                            (numeric) The height of the next block
  "signet_challenge" : "hex",              (string, optional) Only on signet
  "default_witness_commitment" : "hex"     (string, optional) a valid witness commitment for the unmodified block template
}

Examples:
> bitcoin-cli getblocktemplate '{"rules": ["segwit"]}'
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getblocktemplate", "params": [{"rules": ["segwit"]}]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getmininginfo

```
getmininginfo

Returns a json object containing mining-related information.

Result:
{                                (json object)
  "blocks" : n,                  (numeric) The current block
  "currentblockweight" : n,      (numeric, optional) The block weight (including reserved weight for block header, txs count and coinbase tx) of the last assembled block (only present if a block was ever assembled)
  "currentblocktx" : n,          (numeric, optional) The number of block transactions (excluding coinbase) of the last assembled block (only present if a block was ever assembled)
  "bits" : "hex",                (string) The current nBits, compact representation of the block difficulty target
  "difficulty" : n,              (numeric) The current difficulty
  "target" : "hex",              (string) The current target
  "networkhashps" : n,           (numeric) The network hashes per second
  "pooledtx" : n,                (numeric) The size of the mempool
  "blockmintxfee" : n,           (numeric) Minimum feerate of packages selected for block inclusion in BTC/kvB
  "chain" : "str",               (string) current network name (main, test, testnet4, signet, regtest)
  "signet_challenge" : "hex",    (string, optional) The block challenge (aka. block script), in hexadecimal (only present if the current network is a signet)
  "next" : {                     (json object) The next block
    "height" : n,                (numeric) The next height
    "bits" : "hex",              (string) The next target nBits
    "difficulty" : n,            (numeric) The next difficulty
    "target" : "hex"             (string) The next target
  },
  "warnings" : [                 (json array) any network and blockchain warnings (run with `-deprecatedrpc=warnings` to return the latest warning as a single string)
    "str",                       (string) warning
    ...
  ]
}

Examples:
> bitcoin-cli getmininginfo 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getmininginfo", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getnetworkhashps

```
getnetworkhashps ( nblocks height )

Returns the estimated network hashes per second based on the last n blocks.
Pass in [blocks] to override # of blocks, -1 specifies since last difficulty change.
Pass in [height] to estimate the network speed at the time when a certain block was found.

Arguments:
1. nblocks    (numeric, optional, default=120) The number of previous blocks to calculate estimate from, or -1 for blocks since last difficulty change.
2. height     (numeric, optional, default=-1) To estimate at the time of the given height.

Result:
n    (numeric) Hashes per second estimated

Examples:
> bitcoin-cli getnetworkhashps 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getnetworkhashps", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getprioritisedtransactions

```
getprioritisedtransactions

Returns a map of all user-created (see prioritisetransaction) fee deltas by txid, and whether the tx is present in mempool.

Result:
{                                 (json object) prioritisation keyed by txid
  "<transactionid>" : {           (json object)
    "fee_delta" : n,              (numeric) transaction fee delta in satoshis
    "in_mempool" : true|false,    (boolean) whether this transaction is currently in mempool
    "modified_fee" : n            (numeric, optional) modified fee in satoshis. Only returned if in_mempool=true
  },
  ...
}

Examples:
> bitcoin-cli getprioritisedtransactions 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getprioritisedtransactions", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### prioritisetransaction

```
prioritisetransaction "txid" ( dummy ) fee_delta

Accepts the transaction into mined blocks at a higher (or lower) priority

Arguments:
1. txid         (string, required) The transaction id.
2. dummy        (numeric, optional) API-Compatibility for previous API. Must be zero or null.
                DEPRECATED. For forward compatibility use named arguments and omit this parameter.
3. fee_delta    (numeric, required) The fee value (in satoshis) to add (or subtract, if negative).
                Note, that this value is not a fee rate. It is a value to modify absolute fee of the TX.
                The fee is not actually paid, only the algorithm for selecting transactions into a block
                considers the transaction as it would have paid a higher (or lower) fee.

Result:
true|false    (boolean) Returns true

Examples:
> bitcoin-cli prioritisetransaction "txid" 0.0 10000
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "prioritisetransaction", "params": ["txid", 0.0, 10000]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### submitblock

```
submitblock "hexdata" ( "dummy" )

Attempts to submit new block to network.
See https://en.bitcoin.it/wiki/BIP_0022 for full specification.

Arguments:
1. hexdata    (string, required) the hex-encoded block data to submit
2. dummy      (string, optional, default=ignored) dummy value, for compatibility with BIP22. This value is ignored.

Result (If the block was accepted):
null    (json null)

Result (Otherwise):
"str"    (string) According to BIP22

Examples:
> bitcoin-cli submitblock "mydata"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "submitblock", "params": ["mydata"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### submitheader

```
submitheader "hexdata"

Decode the given hexdata as a header and submit it as a candidate chain tip if valid.
Throws when the header is invalid.

Arguments:
1. hexdata    (string, required) the hex-encoded block header data

Result:
null    (json null) None

Examples:
> bitcoin-cli submitheader "aabbcc"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "submitheader", "params": ["aabbcc"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```


## Network

### addnode

```
addnode "node" "command" ( v2transport )

Attempts to add or remove a node from the addnode list.
Or try a connection to a node once.
Nodes added using addnode (or -connect) are protected from DoS disconnection and are not required to be
full nodes/support SegWit as other outbound peers are (though such peers will not be synced from).
Addnode connections are limited to 8 at a time and are counted separately from the -maxconnections limit.

Arguments:
1. node           (string, required) The IP address/hostname optionally followed by :port of the peer to connect to
2. command        (string, required) 'add' to add a node to the list, 'remove' to remove a node from the list, 'onetry' to try a connection to the node once
3. v2transport    (boolean, optional, default=set by -v2transport) Attempt to connect using BIP324 v2 transport protocol (ignored for 'remove' command)

Result:
null    (json null)

Examples:
> bitcoin-cli addnode "192.168.0.6:8333" "onetry" true
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "addnode", "params": ["192.168.0.6:8333", "onetry", true]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### clearbanned

```
clearbanned

Clear all banned IPs.

Result:
null    (json null)

Examples:
> bitcoin-cli clearbanned 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "clearbanned", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### disconnectnode

```
disconnectnode ( "address" nodeid )

Immediately disconnects from the specified peer node.

Strictly one out of 'address' and 'nodeid' can be provided to identify the node.

To disconnect by nodeid, either set 'address' to the empty string, or call using the named 'nodeid' argument only.

Arguments:
1. address    (string, optional, default=fallback to nodeid) The IP address/port of the node
2. nodeid     (numeric, optional, default=fallback to address) The node ID (see getpeerinfo for node IDs)

Result:
null    (json null)

Examples:
> bitcoin-cli disconnectnode "192.168.0.6:8333"
> bitcoin-cli disconnectnode "" 1
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "disconnectnode", "params": ["192.168.0.6:8333"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "disconnectnode", "params": ["", 1]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### exportasmap

```
exportasmap "path"

Export the embedded ASMap data to a file. Any existing file at the path will be overwritten.

Arguments:
1. path    (string, required) Path to the output file. If relative, will be prefixed by datadir.

Result:
{                         (json object)
  "path" : "str",         (string) the absolute path that the ASMap data was written to
  "bytes_written" : n,    (numeric) the number of bytes written to the file
  "file_hash" : "hex"     (string) the SHA256 hash of the exported ASMap data
}

Examples:
> bitcoin-cli exportasmap "asmap.dat"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "exportasmap", "params": ["asmap.dat"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getaddednodeinfo

```
getaddednodeinfo ( "node" )

Returns information about the given added node, or all added nodes
(note that onetry addnodes are not listed here)

Arguments:
1. node    (string, optional, default=all nodes) If provided, return information about this specific node, otherwise all nodes are returned.

Result:
[                                (json array)
  {                              (json object)
    "addednode" : "str",         (string) The node IP address or name (as provided to addnode)
    "connected" : true|false,    (boolean) If connected
    "addresses" : [              (json array) Only when connected = true
      {                          (json object)
        "address" : "str",       (string) The bitcoin server IP and port we're connected to
        "connected" : "str"      (string) connection, inbound or outbound
      },
      ...
    ]
  },
  ...
]

Examples:
> bitcoin-cli getaddednodeinfo "192.168.0.201"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getaddednodeinfo", "params": ["192.168.0.201"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getaddrmaninfo

```
getaddrmaninfo

Provides information about the node's address manager by returning the number of addresses in the `new` and `tried` tables and their sum for all networks.

Result:
{                   (json object) json object with network type as keys
  "network" : {     (json object) the network (ipv4, ipv6, onion, i2p, cjdns, all_networks)
    "new" : n,      (numeric) number of addresses in the new table, which represent potential peers the node has discovered but hasn't yet successfully connected to.
    "tried" : n,    (numeric) number of addresses in the tried table, which represent peers the node has successfully connected to in the past.
    "total" : n     (numeric) total number of addresses in both new/tried tables
  },
  ...
}

Examples:
> bitcoin-cli getaddrmaninfo 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getaddrmaninfo", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getconnectioncount

```
getconnectioncount

Returns the number of connections to other nodes.

Result:
n    (numeric) The connection count

Examples:
> bitcoin-cli getconnectioncount 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getconnectioncount", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getnettotals

```
getnettotals

Returns information about network traffic, including bytes in, bytes out,
and current system time.

Result:
{                                              (json object)
  "totalbytesrecv" : n,                        (numeric) Total bytes received
  "totalbytessent" : n,                        (numeric) Total bytes sent
  "timemillis" : xxx,                          (numeric) Current system UNIX epoch time in milliseconds
  "uploadtarget" : {                           (json object)
    "timeframe" : n,                           (numeric) Length of the measuring timeframe in seconds
    "target" : n,                              (numeric) Target in bytes
    "target_reached" : true|false,             (boolean) True if target is reached
    "serve_historical_blocks" : true|false,    (boolean) True if serving historical blocks
    "bytes_left_in_cycle" : n,                 (numeric) Bytes left in current time cycle
    "time_left_in_cycle" : n                   (numeric) Seconds left in current time cycle
  }
}

Examples:
> bitcoin-cli getnettotals 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getnettotals", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getnetworkinfo

```
getnetworkinfo

Returns an object containing various state info regarding P2P networking.

Result:
{                                                    (json object)
  "version" : n,                                     (numeric) the server version
  "subversion" : "str",                              (string) the server subversion string
  "protocolversion" : n,                             (numeric) the protocol version
  "localservices" : "hex",                           (string) the services we offer to the network
  "localservicesnames" : [                           (json array) the services we offer to the network, in human-readable form
    "str",                                           (string) the service name
    ...
  ],
  "localrelay" : true|false,                         (boolean) true if transaction relay is requested from peers
  "timeoffset" : n,                                  (numeric) the time offset
  "tx_send_rate" : n,                                (numeric) configured target for maximum number of transactions per second to send to inbound peers
  "inv_buckets" : {                                  (json object)
    "inbound/outbound" : {                           (json object) connection direction
      "backlog" : n,                                 (numeric) number of queued txs to announce
      "count_tok" : n,                               (numeric) tokens available to be consumed per-transaction
      "size_tok" : n                                 (numeric) tokens available to be consumed per-byte
    },
    ...
  },
  "connections" : n,                                 (numeric) the total number of connections
  "connections_in" : n,                              (numeric) the number of inbound connections
  "connections_out" : n,                             (numeric) the number of outbound connections
  "networkactive" : true|false,                      (boolean) whether p2p networking is enabled
  "networks" : [                                     (json array) information per network
    {                                                (json object)
      "name" : "str",                                (string) network (ipv4, ipv6, onion, i2p, cjdns)
      "limited" : true|false,                        (boolean) is the network limited using -onlynet?
      "reachable" : true|false,                      (boolean) is the network reachable?
      "proxy" : "str",                               (string) ("host:port") the proxy that is used for this network, or empty if none
      "proxy_randomize_credentials" : true|false     (boolean) Whether randomized credentials are used
    },
    ...
  ],
  "asmap_version" : "hex",                           (string, optional) the SHA256 hash of the asmap data used for IP bucketing (only displayed if the -asmap config option is set)
  "relayfee" : n,                                    (numeric) minimum relay fee rate for transactions in BTC/kvB
  "incrementalfee" : n,                              (numeric) minimum fee rate increment for mempool limiting or replacement in BTC/kvB
  "localaddresses" : [                               (json array) list of local addresses
    {                                                (json object)
      "address" : "str",                             (string) network address
      "port" : n,                                    (numeric) network port
      "score" : n                                    (numeric) relative score
    },
    ...
  ],
  "warnings" : [                                     (json array) any network and blockchain warnings (run with `-deprecatedrpc=warnings` to return the latest warning as a single string)
    "str",                                           (string) warning
    ...
  ]
}

Examples:
> bitcoin-cli getnetworkinfo 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getnetworkinfo", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getnodeaddresses

```
getnodeaddresses ( count "network" )

Return known addresses, after filtering for quality and recency.
These can potentially be used to find new peers in the network.
The total number of addresses known to the node may be higher.

Arguments:
1. count      (numeric, optional, default=1) The maximum number of addresses to return. Specify 0 to return all known addresses.
2. network    (string, optional, default=all networks) Return only addresses of the specified network. Can be one of: ipv4, ipv6, onion, i2p, cjdns.

Result:
[                         (json array)
  {                       (json object)
    "time" : xxx,         (numeric) The UNIX epoch time when the node was last seen
    "services" : n,       (numeric) The services offered by the node
    "address" : "str",    (string) The address of the node
    "port" : n,           (numeric) The port number of the node
    "network" : "str"     (string) The network (ipv4, ipv6, onion, i2p, cjdns) the node connected through
  },
  ...
]

Examples:
> bitcoin-cli getnodeaddresses 8
> bitcoin-cli getnodeaddresses 4 "i2p"
> bitcoin-cli -named getnodeaddresses network=onion count=12
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getnodeaddresses", "params": [8]}' -H 'content-type: application/json' http://127.0.0.1:8332/
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getnodeaddresses", "params": [4, "i2p"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getpeerinfo

```
getpeerinfo

Returns data about each connected network peer as a json array of objects.

Result:
[                                         (json array)
  {                                       (json object)
    "id" : n,                             (numeric) Peer index
    "addr" : "str",                       (string) (host:port) The IP address/hostname optionally followed by :port of the peer
    "addrbind" : "str",                   (string, optional) (ip:port) Bind address of the connection to the peer
    "addrlocal" : "str",                  (string, optional) (ip:port) Local address as reported by the peer
    "network" : "str",                    (string) Network (ipv4, ipv6, onion, i2p, cjdns, not_publicly_routable)
    "mapped_as" : n,                      (numeric, optional) Mapped AS (Autonomous System) number at the end of the BGP route to the peer, used for diversifying
                                          peer selection (only displayed if the -asmap config option is set)
    "services" : "hex",                   (string) The services offered
    "servicesnames" : [                   (json array) the services offered, in human-readable form
      "str",                              (string) the service name if it is recognised
      ...
    ],
    "relaytxes" : true|false,             (boolean) Whether we relay transactions to this peer
    "last_inv_sequence" : n,              (numeric) Mempool sequence number of this peer's last INV
    "inv_to_send" : n,                    (numeric) How many txs we have queued to announce to this peer
    "lastsend" : xxx,                     (numeric) The UNIX epoch time of the last send
    "lastrecv" : xxx,                     (numeric) The UNIX epoch time of the last receive
    "last_transaction" : xxx,             (numeric) The UNIX epoch time of the last valid transaction received from this peer
    "last_block" : xxx,                   (numeric) The UNIX epoch time of the last block received from this peer
    "bytessent" : n,                      (numeric) The total bytes sent
    "bytesrecv" : n,                      (numeric) The total bytes received
    "conntime" : xxx,                     (numeric) The UNIX epoch time of the connection
    "timeoffset" : n,                     (numeric) The time offset in seconds
    "pingtime" : n,                       (numeric, optional) The last ping time in seconds, if any
    "minping" : n,                        (numeric, optional) The minimum observed ping time in seconds, if any
    "pingwait" : n,                       (numeric, optional) The duration in seconds of an outstanding ping (if non-zero)
    "version" : n,                        (numeric) The peer version, such as 70001
    "subver" : "str",                     (string) The string version
    "inbound" : true|false,               (boolean) Inbound (true) or Outbound (false)
    "bip152_hb_to" : true|false,          (boolean) Whether we selected peer as (compact blocks) high-bandwidth peer
    "bip152_hb_from" : true|false,        (boolean) Whether peer selected us as (compact blocks) high-bandwidth peer
    "presynced_headers" : n,              (numeric) The current height of header pre-synchronization with this peer, or -1 if no low-work sync is in progress
    "synced_headers" : n,                 (numeric) The last header we have in common with this peer
    "synced_blocks" : n,                  (numeric) The last block we have in common with this peer
    "inflight" : [                        (json array)
      n,                                  (numeric) The heights of blocks we're currently asking from this peer
      ...
    ],
    "addr_relay_enabled" : true|false,    (boolean) Whether we participate in address relay with this peer
    "addr_processed" : n,                 (numeric) The total number of addresses processed, excluding those dropped due to rate limiting
    "addr_rate_limited" : n,              (numeric) The total number of addresses dropped due to rate limiting
    "permissions" : [                     (json array) Any special permissions that have been granted to this peer
      "str",                              (string) bloomfilter (allow requesting BIP37 filtered blocks and transactions),
                                          noban (do not ban for misbehavior; implies download),
                                          forcerelay (relay transactions that are already in the mempool; implies relay),
                                          relay (relay even in -blocksonly mode, and unlimited transaction announcements),
                                          mempool (allow requesting BIP35 mempool contents),
                                          download (allow getheaders during IBD, no disconnect after maxuploadtarget limit),
                                          addr (responses to GETADDR avoid hitting the cache and contain random records with the most up-to-date info).
                                          
      ...
    ],
    "minfeefilter" : n,                   (numeric) The minimum fee rate for transactions this peer accepts
    "bytessent_per_msg" : {               (json object)
      "msg" : n,                          (numeric) The total bytes sent aggregated by message type
                                          When a message type is not listed in this json object, the bytes sent are 0.
                                          Only known message types can appear as keys in the object.
      ...
    },
    "bytesrecv_per_msg" : {               (json object)
      "msg" : n,                          (numeric) The total bytes received aggregated by message type
                                          When a message type is not listed in this json object, the bytes received are 0.
                                          Only known message types can appear as keys in the object and all bytes received
                                          of unknown message types are listed under '*other*'.
      ...
    },
    "connection_type" : "str",            (string) Type of connection: 
                                          outbound-full-relay (default automatic connections),
                                          block-relay-only (does not relay transactions or addresses),
                                          inbound (initiated by the peer),
                                          manual (added via addnode RPC or -addnode/-connect configuration options),
                                          addr-fetch (short-lived automatic connection for soliciting addresses),
                                          feeler (short-lived automatic connection for testing addresses),
                                          private-broadcast (short-lived automatic connection for broadcasting privacy-sensitive transactions).
                                          Please note this output is unlikely to be stable in upcoming releases as we iterate to
                                          best capture connection behaviors.
    "transport_protocol_type" : "str",    (string) Type of transport protocol: 
                                          detecting (peer could be v1 or v2),
                                          v1 (plaintext transport protocol),
                                          v2 (BIP324 encrypted transport protocol).
                                          
    "session_id" : "str"                  (string) The session ID for this connection, or "" if there is none ("v2" transport protocol only).
                                          
  },
  ...
]

Examples:
> bitcoin-cli getpeerinfo 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getpeerinfo", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### listbanned

```
listbanned

List all manually banned IPs/Subnets.

Result:
[                              (json array)
  {                            (json object)
    "address" : "str",         (string) The IP/Subnet of the banned node
    "ban_created" : xxx,       (numeric) The UNIX epoch time the ban was created
    "banned_until" : xxx,      (numeric) The UNIX epoch time the ban expires
    "ban_duration" : xxx,      (numeric) The ban duration, in seconds
    "time_remaining" : xxx     (numeric) The time remaining until the ban expires, in seconds
  },
  ...
]

Examples:
> bitcoin-cli listbanned 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "listbanned", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### ping

```
ping

Requests that a ping be sent to all other nodes, to measure ping time.
Results are provided in getpeerinfo.
Ping command is handled in queue with all other commands, so it measures processing backlog, not just network ping.

Result:
null    (json null)

Examples:
> bitcoin-cli ping 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "ping", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### setban

```
setban "subnet" "command" ( bantime absolute )

Attempts to add or remove an IP/Subnet from the banned list.

Arguments:
1. subnet      (string, required) The IP/Subnet (see getpeerinfo for nodes IP) with an optional netmask (default is /32 = single IP)
2. command     (string, required) 'add' to add an IP/Subnet to the list, 'remove' to remove an IP/Subnet from the list
3. bantime     (numeric, optional, default=0) time in seconds how long (or until when if [absolute] is set) the IP is banned (0 or empty means using the default time of 24h which can also be overwritten by the -bantime startup argument)
4. absolute    (boolean, optional, default=false) If set, the bantime must be an absolute timestamp expressed in UNIX epoch time

Result:
null    (json null)

Examples:
> bitcoin-cli setban "192.168.0.6" "add" 86400
> bitcoin-cli setban "192.168.0.0/24" "add"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "setban", "params": ["192.168.0.6", "add", 86400]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### setnetworkactive

```
setnetworkactive state

Disable/enable all p2p network activity.

Arguments:
1. state    (boolean, required) true to enable networking, false to disable

Result:
true|false    (boolean) The value that was passed in
```


## Rawtransactions

### abortprivatebroadcast

```
abortprivatebroadcast "id"

Abort private broadcast attempts for a transaction currently being privately broadcast.
The transaction will be removed from the private broadcast queue.
This method is only available when running with -privatebroadcast enabled.

Arguments:
1. id    (string, required) A transaction identifier to abort. It will be matched against both txid and wtxid for all transactions in the private broadcast queue.
         If the provided id matches a txid that corresponds to multiple transactions with different wtxids, multiple transactions will be removed and returned.

Result:
{                               (json object)
  "removed_transactions" : [    (json array) Transactions removed from the private broadcast queue
    {                           (json object)
      "txid" : "hex",           (string) The transaction hash in hex
      "wtxid" : "hex",          (string) The transaction witness hash in hex
      "hex" : "hex"             (string) The serialized, hex-encoded transaction data
    },
    ...
  ]
}

Examples:
> bitcoin-cli abortprivatebroadcast "id"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "abortprivatebroadcast", "params": ["id"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### analyzepsbt

```
analyzepsbt "psbt"

Analyzes and provides information about the current status of a PSBT and its inputs

Arguments:
1. psbt    (string, required) A base64 string of a PSBT

Result:
{                                   (json object)
  "inputs" : [                      (json array, optional)
    {                               (json object)
      "has_utxo" : true|false,      (boolean) Whether a UTXO is provided
      "is_final" : true|false,      (boolean) Whether the input is finalized
      "missing" : {                 (json object, optional) Things that are missing that are required to complete this input
        "pubkeys" : [               (json array, optional)
          "hex",                    (string) Public key ID, hash160 of the public key, of a public key whose BIP 32 derivation path is missing
          ...
        ],
        "signatures" : [            (json array, optional)
          "hex",                    (string) Public key ID, hash160 of the public key, of a public key whose signature is missing
          ...
        ],
        "redeemscript" : "hex",     (string, optional) Hash160 of the redeem script that is missing
        "witnessscript" : "hex"     (string, optional) SHA256 of the witness script that is missing
      },
      "next" : "str"                (string, optional) Role of the next person that this input needs to go to
    },
    ...
  ],
  "estimated_vsize" : n,            (numeric, optional) Estimated vsize of the final signed transaction
  "estimated_feerate" : n,          (numeric, optional) Estimated feerate of the final signed transaction in BTC/kvB. Shown only if all UTXO slots in the PSBT have been filled
  "fee" : n,                        (numeric, optional) The transaction fee paid. Shown only if all UTXO slots in the PSBT have been filled
  "next" : "str",                   (string) Role of the next person that this psbt needs to go to
  "error" : "str"                   (string, optional) Error message (if there is one)
}

Examples:
> bitcoin-cli analyzepsbt "psbt"
```

### combinepsbt

```
combinepsbt ["psbt",...]

Combine multiple partially signed Bitcoin transactions into one transaction.
Implements the Combiner role.

Arguments:
1. txs            (json array, required) The base64 strings of partially signed transactions
     [
       "psbt",    (string) A base64 string of a PSBT
       ...
     ]

Result:
"str"    (string) The base64-encoded partially signed transaction

Examples:
> bitcoin-cli combinepsbt '["mybase64_1", "mybase64_2", "mybase64_3"]'
```

### combinerawtransaction

```
combinerawtransaction ["hexstring",...]

Combine multiple partially signed transactions into one transaction.
The combined transaction may be another partially signed transaction or a 
fully signed transaction.

Arguments:
1. txs                 (json array, required) The hex strings of partially signed transactions
     [
       "hexstring",    (string) A hex-encoded raw transaction
       ...
     ]

Result:
"str"    (string) The hex-encoded raw transaction with signature(s)

Examples:
> bitcoin-cli combinerawtransaction '["myhex1", "myhex2", "myhex3"]'
```

### converttopsbt

```
converttopsbt "hexstring" ( permitsigdata iswitness psbt_version )

Converts a network serialized transaction to a PSBT. This should be used only with createrawtransaction and fundrawtransaction
createpsbt and walletcreatefundedpsbt should be used for new applications.

Arguments:
1. hexstring        (string, required) The hex string of a raw transaction
2. permitsigdata    (boolean, optional, default=false) If true, any signatures in the input will be discarded and conversion
                    will continue. If false, RPC will fail if any signatures are present.
3. iswitness        (boolean, optional, default=depends on heuristic tests) Whether the transaction hex is a serialized witness transaction.
                    If iswitness is not present, heuristic tests will be used in decoding.
                    If true, only witness deserialization will be tried.
                    If false, only non-witness deserialization will be tried.
                    This boolean should reflect whether the transaction has inputs
                    (e.g. fully valid, or on-chain transactions), if known by the caller.
4. psbt_version     (numeric, optional, default=2) The PSBT version number to use.

Result:
"str"    (string) The resulting raw transaction (base64-encoded string)

Examples:

Create a transaction
> bitcoin-cli createrawtransaction "[{\"txid\":\"myid\",\"vout\":0}]" "[{\"data\":\"00010203\"}]"

Convert the transaction to a PSBT
> bitcoin-cli converttopsbt "rawtransaction"
```

### createpsbt

```
createpsbt [{"txid":"hex","vout":n,"sequence":n},...] [{"address":amount,...},{"data":"hex"},...] ( locktime replaceable version psbt_version )

Creates a transaction in the Partially Signed Transaction format.
Implements the Creator role.
Note that the transaction's inputs are not signed, and
it is not stored in the wallet or transmitted to the network.

Arguments:
1. inputs                      (json array, required) The inputs
     [
       {                       (json object)
         "txid": "hex",        (string, required) The transaction id
         "vout": n,            (numeric, required) The output number
         "sequence": n,        (numeric, optional, default=depends on the value of the 'replaceable' and 'locktime' arguments) The sequence number
       },
       ...
     ]
2. outputs                     (json array, required) The outputs specified as key-value pairs.
                               Each key may only appear once, i.e. there can only be one 'data' output, and no address may be duplicated.
                               At least one output of either type must be specified.
                               For compatibility reasons, a dictionary, which holds the key-value pairs directly, is also
                               accepted as second parameter.
     [
       {                       (json object)
         "address": amount,    (numeric or string, required) A key-value pair. The key (string) is the bitcoin address, the value (float or string) is the amount in BTC
         ...
       },
       {                       (json object)
         "data": "hex",        (string, required) A key-value pair. The key must be "data", the value is hex-encoded data that becomes a part of an OP_RETURN output
       },
       ...
     ]
3. locktime                    (numeric, optional, default=0) Raw locktime. Non-0 value also locktime-activates inputs
4. replaceable                 (boolean, optional, default=true) Marks this transaction as BIP125-replaceable.
                               Allows this transaction to be replaced by a transaction with higher fees. If provided, it is an error if explicit sequence numbers are incompatible.
5. version                     (numeric, optional, default=2) Transaction version
6. psbt_version                (numeric, optional, default=2) The PSBT version number to use.

Result:
"str"    (string) The resulting raw transaction (base64-encoded string)

Examples:
> bitcoin-cli createpsbt "[{\"txid\":\"myid\",\"vout\":0}]" "[{\"address\":0.01}]"
```

### createrawtransaction

```
createrawtransaction [{"txid":"hex","vout":n,"sequence":n},...] [{"address":amount,...},{"data":"hex"},...] ( locktime replaceable version )

Create a transaction spending the given inputs and creating new outputs.
Outputs can be addresses or data.
Returns hex-encoded raw transaction.
Note that the transaction's inputs are not signed, and
it is not stored in the wallet or transmitted to the network.

Arguments:
1. inputs                      (json array, required) The inputs
     [
       {                       (json object)
         "txid": "hex",        (string, required) The transaction id
         "vout": n,            (numeric, required) The output number
         "sequence": n,        (numeric, optional, default=depends on the value of the 'replaceable' and 'locktime' arguments) The sequence number
       },
       ...
     ]
2. outputs                     (json array, required) The outputs specified as key-value pairs.
                               Each key may only appear once, i.e. there can only be one 'data' output, and no address may be duplicated.
                               At least one output of either type must be specified.
                               For compatibility reasons, a dictionary, which holds the key-value pairs directly, is also
                               accepted as second parameter.
     [
       {                       (json object)
         "address": amount,    (numeric or string, required) A key-value pair. The key (string) is the bitcoin address, the value (float or string) is the amount in BTC
         ...
       },
       {                       (json object)
         "data": "hex",        (string, required) A key-value pair. The key must be "data", the value is hex-encoded data that becomes a part of an OP_RETURN output
       },
       ...
     ]
3. locktime                    (numeric, optional, default=0) Raw locktime. Non-0 value also locktime-activates inputs
4. replaceable                 (boolean, optional, default=true) Marks this transaction as BIP125-replaceable.
                               Allows this transaction to be replaced by a transaction with higher fees. If provided, it is an error if explicit sequence numbers are incompatible.
5. version                     (numeric, optional, default=2) Transaction version

Result:
"hex"    (string) hex string of the transaction

Examples:
> bitcoin-cli createrawtransaction "[{\"txid\":\"myid\",\"vout\":0}]" "[{\"address\":0.01}]"
> bitcoin-cli createrawtransaction "[{\"txid\":\"myid\",\"vout\":0}]" "[{\"data\":\"00010203\"}]"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "createrawtransaction", "params": ["[{\"txid\":\"myid\",\"vout\":0}]", "[{\"address\":0.01}]"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "createrawtransaction", "params": ["[{\"txid\":\"myid\",\"vout\":0}]", "[{\"data\":\"00010203\"}]"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### decodepsbt

```
decodepsbt "psbt"

Return a JSON object representing the serialized, base64-encoded partially signed Bitcoin transaction.

Arguments:
1. psbt    (string, required) The PSBT base64 string

Result:
{                                          (json object)
  "tx" : {                                 (json object, optional) The decoded network-serialized unsigned transaction.
    ...                                    The layout is the same as the output of decoderawtransaction.
  },
  "global_xpubs" : [                       (json array)
    {                                      (json object)
      "xpub" : "str",                      (string) The extended public key this path corresponds to
      "master_fingerprint" : "hex",        (string) The fingerprint of the master key
      "path" : "str"                       (string) The path
    },
    ...
  ],
  "tx_version" : n,                        (numeric, optional) The version number of the unsigned transaction. Not to be confused with PSBT version
  "fallback_locktime" : n,                 (numeric, optional) The locktime to fallback to if no inputs specify a required locktime.
  "input_count" : n,                       (numeric, optional) The number of inputs in this psbt
  "output_count" : n,                      (numeric, optional) The number of outputs in this psbt.
  "inputs_modifiable" : true|false,        (boolean, optional) Whether inputs can be modified
  "outputs_modifiable" : true|false,       (boolean, optional) Whether outputs can be modified
  "has_sighash_single" : true|false,       (boolean, optional) Whether this PSBT has SIGHASH_SINGLE inputs
  "psbt_version" : n,                      (numeric, optional) The PSBT version number. Not to be confused with the unsigned transaction version
  "proprietary" : [                        (json array) The global proprietary map
    {                                      (json object)
      "identifier" : "hex",                (string) The hex string for the proprietary identifier
      "subtype" : n,                       (numeric) The number for the subtype
      "key" : "hex",                       (string) The hex for the key
      "value" : "hex"                      (string) The hex for the value
    },
    ...
  ],
  "unknown" : {                            (json object) The unknown global fields
    "key" : "hex",                         (string) (key-value pair) An unknown key-value pair
    ...
  },
  "inputs" : [                             (json array)
    {                                      (json object)
      "non_witness_utxo" : {               (json object, optional) Decoded network transaction for non-witness UTXOs
        ...                                The layout is the same as the output of decoderawtransaction.
      },
      "witness_utxo" : {                   (json object, optional) Transaction output for witness UTXOs
        "amount" : n,                      (numeric) The value in BTC
        "scriptPubKey" : {                 (json object)
          "asm" : "str",                   (string) Disassembly of the output script
          "desc" : "str",                  (string) Inferred descriptor for the output
          "hex" : "hex",                   (string) The raw output script bytes, hex-encoded
          "type" : "str",                  (string) The type, eg 'pubkeyhash'
          "address" : "str"                (string, optional) The Bitcoin address (only if a well-defined address exists)
        }
      },
      "partial_signatures" : {             (json object, optional)
        "pubkey" : "str",                  (string) The public key and signature that corresponds to it.
        ...
      },
      "sighash" : "str",                   (string, optional) The sighash type to be used
      "redeem_script" : {                  (json object, optional)
        "asm" : "str",                     (string) Disassembly of the redeem script
        "hex" : "hex",                     (string) The raw redeem script bytes, hex-encoded
        "type" : "str"                     (string) The type, eg 'pubkeyhash'
      },
      "witness_script" : {                 (json object, optional)
        "asm" : "str",                     (string) Disassembly of the witness script
        "hex" : "hex",                     (string) The raw witness script bytes, hex-encoded
        "type" : "str"                     (string) The type, eg 'pubkeyhash'
      },
      "bip32_derivs" : [                   (json array, optional)
        {                                  (json object)
          "pubkey" : "str",                (string) The public key with the derivation path as the value.
          "master_fingerprint" : "str",    (string) The fingerprint of the master key
          "path" : "str"                   (string) The path
        },
        ...
      ],
      "final_scriptSig" : {                (json object, optional)
        "asm" : "str",                     (string) Disassembly of the final signature script
        "hex" : "hex"                      (string) The raw final signature script bytes, hex-encoded
      },
      "final_scriptwitness" : [            (json array, optional)
        "hex",                             (string) hex-encoded witness data (if any)
        ...
      ],
      "ripemd160_preimages" : {            (json object, optional)
        "hash" : "str",                    (string) The hash and preimage that corresponds to it.
        ...
      },
      "sha256_preimages" : {               (json object, optional)
        "hash" : "str",                    (string) The hash and preimage that corresponds to it.
        ...
      },
      "hash160_preimages" : {              (json object, optional)
        "hash" : "str",                    (string) The hash and preimage that corresponds to it.
        ...
      },
      "hash256_preimages" : {              (json object, optional)
        "hash" : "str",                    (string) The hash and preimage that corresponds to it.
        ...
      },
      "previous_txid" : "hex",             (string, optional) TXID of the transaction containing the output being spent by this input
      "previous_vout" : n,                 (numeric, optional) Index of the output being spent
      "sequence" : n,                      (numeric, optional) Sequence number for this input
      "time_locktime" : n,                 (numeric, optional) Time-based locktime required for this input
      "height_locktime" : n,               (numeric, optional) Height-based locktime required for this input
      "taproot_key_path_sig" : "hex",      (string, optional) hex-encoded signature for the Taproot key path spend
      "taproot_script_path_sigs" : [       (json array, optional)
        {                                  (json object, optional) The signature for the pubkey and leaf hash combination
          "pubkey" : "str",                (string) The x-only pubkey for this signature
          "leaf_hash" : "str",             (string) The leaf hash for this signature
          "sig" : "str"                    (string) The signature itself
        },
        ...
      ],
      "taproot_scripts" : [                (json array, optional)
        {                                  (json object)
          "script" : "hex",                (string) A leaf script
          "leaf_ver" : n,                  (numeric) The version number for the leaf script
          "control_blocks" : [             (json array) The control blocks for this script
            "hex",                         (string) A hex-encoded control block for this script
            ...
          ]
        },
        ...
      ],
      "taproot_bip32_derivs" : [           (json array, optional)
        {                                  (json object)
          "pubkey" : "str",                (string) The x-only public key this path corresponds to
          "master_fingerprint" : "str",    (string) The fingerprint of the master key
          "path" : "str",                  (string) The path
          "leaf_hashes" : [                (json array) The hashes of the leaves this pubkey appears in
            "hex",                         (string) The hash of a leaf this pubkey appears in
            ...
          ]
        },
        ...
      ],
      "taproot_internal_key" : "hex",      (string, optional) The hex-encoded Taproot x-only internal key
      "taproot_merkle_root" : "hex",       (string, optional) The hex-encoded Taproot merkle root
      "musig2_participant_pubkeys" : [     (json array, optional)
        {                                  (json object)
          "aggregate_pubkey" : "hex",      (string) The compressed aggregate public key for which the participants create.
          "participant_pubkeys" : [        (json array)
            "hex",                         (string) The compressed public keys that are aggregated for aggregate_pubkey.
            ...
          ]
        },
        ...
      ],
      "musig2_pubnonces" : [               (json array, optional)
        {                                  (json object)
          "participant_pubkey" : "hex",    (string) The compressed public key of the participant that created this pubnonce.
          "aggregate_pubkey" : "hex",      (string) The compressed aggregate public key for which this pubnonce is for.
          "leaf_hash" : "hex",             (string, optional) The hash of the leaf script that contains the aggregate pubkey being signed for. Omitted when signing for the internal key.
          "pubnonce" : "hex"               (string) The public nonce itself.
        },
        ...
      ],
      "musig2_partial_sigs" : [            (json array, optional)
        {                                  (json object)
          "participant_pubkey" : "hex",    (string) The compressed public key of the participant that created this partial signature.
          "aggregate_pubkey" : "hex",      (string) The compressed aggregate public key for which this partial signature is for.
          "leaf_hash" : "hex",             (string, optional) The hash of the leaf script that contains the aggregate pubkey being signed for. Omitted when signing for the internal key.
          "partial_sig" : "hex"            (string) The partial signature itself.
        },
        ...
      ],
      "unknown" : {                        (json object, optional) The unknown input fields
        "key" : "hex",                     (string) (key-value pair) An unknown key-value pair
        ...
      },
      "proprietary" : [                    (json array, optional) The input proprietary map
        {                                  (json object)
          "identifier" : "hex",            (string) The hex string for the proprietary identifier
          "subtype" : n,                   (numeric) The number for the subtype
          "key" : "hex",                   (string) The hex for the key
          "value" : "hex"                  (string) The hex for the value
        },
        ...
      ]
    },
    ...
  ],
  "outputs" : [                            (json array)
    {                                      (json object)
      "redeem_script" : {                  (json object, optional)
        "asm" : "str",                     (string) Disassembly of the redeem script
        "hex" : "hex",                     (string) The raw redeem script bytes, hex-encoded
        "type" : "str"                     (string) The type, eg 'pubkeyhash'
      },
      "witness_script" : {                 (json object, optional)
        "asm" : "str",                     (string) Disassembly of the witness script
        "hex" : "hex",                     (string) The raw witness script bytes, hex-encoded
        "type" : "str"                     (string) The type, eg 'pubkeyhash'
      },
      "bip32_derivs" : [                   (json array, optional)
        {                                  (json object)
          "pubkey" : "str",                (string) The public key this path corresponds to
          "master_fingerprint" : "str",    (string) The fingerprint of the master key
          "path" : "str"                   (string) The path
        },
        ...
      ],
      "amount" : n,                        (numeric, optional) The amount (nValue) for this output
      "script" : {                         (json object, optional) The output script (scriptPubKey) for this output
        ...                                The layout is the same as the output of scriptPubKeys in decoderawtransaction.
      },
      "taproot_internal_key" : "hex",      (string, optional) The hex-encoded Taproot x-only internal key
      "taproot_tree" : [                   (json array, optional) The tuples that make up the Taproot tree, in depth first search order
        {                                  (json object, optional) A single leaf script in the taproot tree
          "depth" : n,                     (numeric) The depth of this element in the tree
          "leaf_ver" : n,                  (numeric) The version of this leaf
          "script" : "str"                 (string) The hex-encoded script itself
        },
        ...
      ],
      "taproot_bip32_derivs" : [           (json array, optional)
        {                                  (json object)
          "pubkey" : "str",                (string) The x-only public key this path corresponds to
          "master_fingerprint" : "str",    (string) The fingerprint of the master key
          "path" : "str",                  (string) The path
          "leaf_hashes" : [                (json array) The hashes of the leaves this pubkey appears in
            "hex",                         (string) The hash of a leaf this pubkey appears in
            ...
          ]
        },
        ...
      ],
      "musig2_participant_pubkeys" : [     (json array, optional)
        {                                  (json object)
          "aggregate_pubkey" : "hex",      (string) The compressed aggregate public key for which the participants create.
          "participant_pubkeys" : [        (json array)
            "hex",                         (string) The compressed public keys that are aggregated for aggregate_pubkey.
            ...
          ]
        },
        ...
      ],
      "unknown" : {                        (json object, optional) The unknown output fields
        "key" : "hex",                     (string) (key-value pair) An unknown key-value pair
        ...
      },
      "proprietary" : [                    (json array, optional) The output proprietary map
        {                                  (json object)
          "identifier" : "hex",            (string) The hex string for the proprietary identifier
          "subtype" : n,                   (numeric) The number for the subtype
          "key" : "hex",                   (string) The hex for the key
          "value" : "hex"                  (string) The hex for the value
        },
        ...
      ]
    },
    ...
  ],
  "fee" : n                                (numeric, optional) The transaction fee paid if all UTXOs slots in the PSBT have been filled.
}

Examples:
> bitcoin-cli decodepsbt "psbt"
```

### decoderawtransaction

```
decoderawtransaction "hexstring" ( iswitness )

Return a JSON object representing the serialized, hex-encoded transaction.

Arguments:
1. hexstring    (string, required) The transaction hex string
2. iswitness    (boolean, optional, default=depends on heuristic tests) Whether the transaction hex is a serialized witness transaction.
                If iswitness is not present, heuristic tests will be used in decoding.
                If true, only witness deserialization will be tried.
                If false, only non-witness deserialization will be tried.
                This boolean should reflect whether the transaction has inputs
                (e.g. fully valid, or on-chain transactions), if known by the caller.

Result:
{                             (json object)
  "txid" : "hex",             (string) The transaction id
  "hash" : "hex",             (string) The transaction hash (differs from txid for witness transactions)
  "size" : n,                 (numeric) The serialized transaction size
  "vsize" : n,                (numeric) The virtual transaction size (differs from size for witness transactions)
  "weight" : n,               (numeric) The transaction's weight (between vsize*4-3 and vsize*4)
  "version" : n,              (numeric) The version
  "locktime" : xxx,           (numeric) The lock time
  "vin" : [                   (json array)
    {                         (json object)
      "coinbase" : "hex",     (string, optional) The coinbase value (only if coinbase transaction)
      "txid" : "hex",         (string, optional) The transaction id (if not coinbase transaction)
      "vout" : n,             (numeric, optional) The output number (if not coinbase transaction)
      "scriptSig" : {         (json object, optional) The script (if not coinbase transaction)
        "asm" : "str",        (string) Disassembly of the signature script
        "hex" : "hex"         (string) The raw signature script bytes, hex-encoded
      },
      "txinwitness" : [       (json array, optional)
        "hex",                (string) hex-encoded witness data (if any)
        ...
      ],
      "sequence" : n          (numeric) The script sequence number
    },
    ...
  ],
  "vout" : [                  (json array)
    {                         (json object)
      "value" : n,            (numeric) The value in BTC
      "n" : n,                (numeric) index
      "scriptPubKey" : {      (json object)
        "asm" : "str",        (string) Disassembly of the output script
        "desc" : "str",       (string) Inferred descriptor for the output
        "hex" : "hex",        (string) The raw output script bytes, hex-encoded
        "address" : "str",    (string, optional) The Bitcoin address (only if a well-defined address exists)
        "type" : "str"        (string) The type (one of: nonstandard, anchor, pubkey, pubkeyhash, scripthash, multisig, nulldata, witness_v0_scripthash, witness_v0_keyhash, witness_v1_taproot, witness_unknown)
      }
    },
    ...
  ]
}

Examples:
> bitcoin-cli decoderawtransaction "hexstring"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "decoderawtransaction", "params": ["hexstring"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### decodescript

```
decodescript "hexstring"

Decode a hex-encoded script.

Arguments:
1. hexstring    (string, required) the hex-encoded script

Result:
{                             (json object)
  "asm" : "str",              (string) Disassembly of the script
  "desc" : "str",             (string) Inferred descriptor for the script
  "type" : "str",             (string) The output type (e.g. nonstandard, anchor, pubkey, pubkeyhash, scripthash, multisig, nulldata, witness_v0_scripthash, witness_v0_keyhash, witness_v1_taproot, witness_unknown)
  "address" : "str",          (string, optional) The Bitcoin address (only if a well-defined address exists)
  "p2sh" : "str",             (string, optional) address of P2SH script wrapping this redeem script (not returned for types that should not be wrapped)
  "segwit" : {                (json object, optional) Result of a witness output script wrapping this redeem script (not returned for types that should not be wrapped)
    "asm" : "str",            (string) Disassembly of the output script
    "hex" : "hex",            (string) The raw output script bytes, hex-encoded
    "type" : "str",           (string) The type of the output script (e.g. witness_v0_keyhash or witness_v0_scripthash)
    "address" : "str",        (string, optional) The Bitcoin address (only if a well-defined address exists)
    "desc" : "str",           (string) Inferred descriptor for the script
    "p2sh-segwit" : "str"     (string) address of the P2SH script wrapping this witness redeem script
  }
}

Examples:
> bitcoin-cli decodescript "hexstring"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "decodescript", "params": ["hexstring"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### descriptorprocesspsbt

```
descriptorprocesspsbt "psbt" ["",{"desc":"str","range":n or [n,n]},...] ( "sighashtype" bip32derivs finalize )

Update all segwit inputs in a PSBT with information from output descriptors, the UTXO set or the mempool. 
Then, sign the inputs we are able to with information from the output descriptors.

Arguments:
1. psbt                          (string, required) The transaction base64 string
2. descriptors                   (json array, required) An array of either strings or objects
     [
       "",                       (string) An output descriptor
       {                         (json object) An object with an output descriptor and extra information
         "desc": "str",          (string, required) An output descriptor
         "range": n or [n,n],    (numeric or array, optional, default=1000) Up to what index HD chains should be explored (either end or [begin,end])
       },
       ...
     ]
3. sighashtype                   (string, optional, default="DEFAULT for Taproot, ALL otherwise") The signature hash type to sign with if not specified by the PSBT. Must be one of
                                 "DEFAULT"
                                 "ALL"
                                 "NONE"
                                 "SINGLE"
                                 "ALL|ANYONECANPAY"
                                 "NONE|ANYONECANPAY"
                                 "SINGLE|ANYONECANPAY"
4. bip32derivs                   (boolean, optional, default=true) Include BIP 32 derivation paths for public keys if we know them
5. finalize                      (boolean, optional, default=true) Also finalize inputs if possible

Result:
{                             (json object)
  "psbt" : "str",             (string) The base64-encoded partially signed transaction
  "complete" : true|false,    (boolean) If the transaction has a complete set of signatures
  "hex" : "hex"               (string, optional) The hex-encoded network transaction if complete
}

Examples:
> bitcoin-cli descriptorprocesspsbt "psbt" "[\"descriptor1\", \"descriptor2\"]"
> bitcoin-cli descriptorprocesspsbt "psbt" "[{\"desc\":\"mydescriptor\", \"range\":21}]"
```

### finalizepsbt

```
finalizepsbt "psbt" ( extract )

Finalize the inputs of a PSBT. If the transaction is fully signed, it will produce a
network serialized transaction which can be broadcast with sendrawtransaction. Otherwise a PSBT will be
created which has the final_scriptSig and final_scriptwitness fields filled for inputs that are complete.
Implements the Finalizer and Extractor roles.

Arguments:
1. psbt       (string, required) A base64 string of a PSBT
2. extract    (boolean, optional, default=true) If true and the transaction is complete,
              extract and return the complete transaction in normal network serialization instead of the PSBT.

Result:
{                             (json object)
  "psbt" : "str",             (string, optional) The base64-encoded partially signed transaction if not extracted
  "hex" : "hex",              (string, optional) The hex-encoded network transaction if extracted
  "complete" : true|false     (boolean) If the transaction has a complete set of signatures
}

Examples:
> bitcoin-cli finalizepsbt "psbt"
```

### fundrawtransaction

```
fundrawtransaction "hexstring" ( options iswitness )

If the transaction has no inputs, they will be automatically selected to meet its out value.
It will add at most one change output to the outputs.
No existing outputs will be modified unless "subtractFeeFromOutputs" is specified.
Note that inputs which were signed may need to be resigned after completion since in/outputs have been added.
The inputs added will not be signed, use signrawtransactionwithkey
or signrawtransactionwithwallet for that.
All existing inputs must either have their previous output transaction be in the wallet
or be in the UTXO set. Solving data must be provided for non-wallet inputs.
Note that all inputs selected must be of standard form and P2SH scripts must be
in the wallet using importdescriptors (to calculate fees).
You can see whether this is the case by checking the "solvable" field in the listunspent output.
Note that if specifying an exact fee rate, the resulting transaction may have a higher fee rate
if the transaction has unconfirmed inputs. This is because the wallet will attempt to make the
entire package have the given fee rate, not the resulting transaction.

Arguments:
1. hexstring    (string, required) The hex string of the raw transaction
2. options      (json object, optional) Options object that can be used to pass named arguments, listed below.
3. iswitness    (boolean, optional, default=depends on heuristic tests) Whether the transaction hex is a serialized witness transaction.
                If iswitness is not present, heuristic tests will be used in decoding.
                If true, only witness deserialization will be tried.
                If false, only non-witness deserialization will be tried.
                This boolean should reflect whether the transaction has inputs
                (e.g. fully valid, or on-chain transactions), if known by the caller.

Named Arguments:
add_inputs                 (boolean, optional, default=true) For a transaction with existing inputs, automatically include more if they are not enough.
include_unsafe             (boolean, optional, default=false) Include inputs that are not safe to spend (unconfirmed transactions from outside keys and unconfirmed replacement transactions).
                           Warning: the resulting transaction may become invalid if one of the unsafe inputs disappears.
                           If that happens, you will need to fund the transaction with different inputs and republish it.
minconf                    (numeric, optional, default=0) If add_inputs is specified, require inputs with at least this many confirmations.
maxconf                    (numeric, optional) If add_inputs is specified, require inputs with at most this many confirmations.
changeAddress              (string, optional, default=automatic) The bitcoin address to receive the change
changePosition             (numeric, optional, default=random) The index of the change output
change_type                (string, optional, default=set by -changetype) The output type to use. Only valid if changeAddress is not specified. Options are "legacy", "p2sh-segwit", "bech32", "bech32m".
includeWatching            (boolean, optional, default=false) (DEPRECATED) No longer used
lockUnspents               (boolean, optional, default=false) Lock selected unspent outputs
fee_rate                   (numeric or string, optional, default=not set, fall back to wallet fee estimation) Specify a fee rate in sat/vB.
feeRate                    (numeric or string, optional, default=not set, fall back to wallet fee estimation) Specify a fee rate in BTC/kvB.
subtractFeeFromOutputs     (json array, optional, default=[]) The integers.
                           The fee will be equally deducted from the amount of each specified output.
                           Those recipients will receive less bitcoins than you enter in their corresponding amount field.
                           If no outputs are specified here, the sender pays the fee.
     [
       vout_index,         (numeric) The zero-based output index, before a change output is added.
       ...
     ]
input_weights              (json array, optional) Inputs and their corresponding weights
     [
       {                   (json object)
         "txid": "hex",    (string, required) The transaction id
         "vout": n,        (numeric, required) The output index
         "weight": n,      (numeric, required) The maximum weight for this input, including the weight of the outpoint and sequence number. Note that serialized signature sizes are not guaranteed to be consistent, so the maximum DER signatures size of 73 bytes should be used when considering ECDSA signatures.Remember to convert serialized sizes to weight units when necessary.
       },
       ...
     ]
max_tx_weight              (numeric, optional, default=400000) The maximum acceptable transaction weight.
                           Transaction building will fail if this can not be satisfied.
conf_target                (numeric, optional, default=wallet -txconfirmtarget) Confirmation target in blocks
estimate_mode              (string, optional, default="unset") The fee estimate mode, must be one of (case insensitive):
                           unset, economical, conservative 
                           unset means no mode set (economical mode is used if the transaction is replaceable;
                           otherwise, conservative mode is used). 
                           economical mode potentially returns a lower fee rate estimate.
                           conservative potentially returns a higher fee rate estimate.
                           
replaceable                (boolean, optional, default=wallet default) Marks this transaction as BIP125-replaceable.
                           Allows this transaction to be replaced by a transaction with higher fees
solving_data               (json object, optional) Keys and scripts needed for producing a final transaction with a dummy signature.
                           Used for fee estimation during coin selection.
     {
       "pubkeys": [        (json array, optional, default=[]) Public keys involved in this transaction.
         "pubkey",         (string) A public key
         ...
       ],
       "scripts": [        (json array, optional, default=[]) Scripts involved in this transaction.
         "script",         (string) A script
         ...
       ],
       "descriptors": [    (json array, optional, default=[]) Descriptors that provide solving data for this transaction.
         "descriptor",     (string) A descriptor
         ...
       ],
     }

Result:
{                     (json object)
  "hex" : "hex",      (string) The resulting raw transaction (hex-encoded string)
  "fee" : n,          (numeric) Fee in BTC the resulting transaction pays
  "changepos" : n     (numeric) The position of the added change output, or -1
}

Examples:

Create a transaction with no inputs
> bitcoin-cli createrawtransaction "[]" "{\"myaddress\":0.01}"

Add sufficient unsigned inputs to meet the output value
> bitcoin-cli fundrawtransaction "rawtransactionhex"

Sign the transaction
> bitcoin-cli signrawtransactionwithwallet "fundedtransactionhex"

Send the transaction
> bitcoin-cli sendrawtransaction "signedtransactionhex"
```

### getprivatebroadcastinfo

```
getprivatebroadcastinfo

Returns information about transactions tracked for private broadcast.
Transactions that have reached the send-attempt limit remain in the result with attempts_remaining=0.
This method is only available when running with -privatebroadcast enabled.

Result:
{                                  (json object)
  "transactions" : [               (json array)
    {                              (json object)
      "txid" : "hex",              (string) The transaction hash in hex
      "wtxid" : "hex",             (string) The transaction witness hash in hex
      "hex" : "hex",               (string) The serialized, hex-encoded transaction data
      "time_added" : xxx,          (numeric) The time this transaction was added to the private broadcast queue (seconds since epoch)
      "attempts_remaining" : n,    (numeric) The number of additional private broadcast send attempts allowed for this transaction
      "peers" : [                  (json array) Per-peer send and acknowledgment information for this transaction
        {                          (json object)
          "address" : "str",       (string) The address of the peer to which the transaction was sent
          "sent" : xxx,            (numeric) The time this transaction was picked for sending to this peer via private broadcast (seconds since epoch)
          "received" : xxx         (numeric, optional) The time this peer acknowledged reception of the transaction (seconds since epoch)
        },
        ...
      ]
    },
    ...
  ]
}

Examples:
> bitcoin-cli getprivatebroadcastinfo 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getprivatebroadcastinfo", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getrawtransaction

```
getrawtransaction "txid" ( verbosity "blockhash" )

By default, this call only returns a transaction if it is in the mempool. If -txindex is enabled
and no blockhash argument is passed, it will return the transaction if it is in the mempool or any block.
If a blockhash argument is passed, it will return the transaction if
the specified block is available and the transaction is in that block.

Hint: Use gettransaction for wallet transactions.

If verbosity is 0 or omitted, returns the serialized transaction as a hex-encoded string.
If verbosity is 1, returns a JSON Object with information about the transaction.
If verbosity is 2, returns a JSON Object with information about the transaction, including fee and prevout information.

Arguments:
1. txid         (string, required) The transaction id
2. verbosity    (numeric, optional, default=0) 0 for hex-encoded data, 1 for a JSON object, and 2 for JSON object with fee and prevout
3. blockhash    (string, optional) The block in which to look for the transaction

Result (if verbosity is not set or set to 0):
"str"    (string) The serialized transaction as a hex-encoded string for 'txid'

Result (if verbosity is set to 1):
{                                    (json object)
  "in_active_chain" : true|false,    (boolean, optional) Whether specified block is in the active chain or not (only present with explicit "blockhash" argument)
  "blockhash" : "hex",               (string, optional) the block hash
  "vsize_adjusted" : n,              (numeric, optional) Sigop-adjusted virtual size in bytes, present for mempool transactions.
  "confirmations" : n,               (numeric, optional) The confirmations
  "blocktime" : xxx,                 (numeric, optional) The block time expressed in UNIX epoch time
  "time" : n,                        (numeric, optional) Same as "blocktime"
  "hex" : "hex",                     (string) The serialized, hex-encoded data for 'txid'
  "txid" : "hex",                    (string) The transaction id (same as provided)
  "hash" : "hex",                    (string) The transaction hash (differs from txid for witness transactions)
  "size" : n,                        (numeric) The serialized transaction size
  "vsize" : n,                       (numeric) The virtual transaction size (differs from size for witness transactions)
  "weight" : n,                      (numeric) The transaction's weight (between vsize*4-3 and vsize*4)
  "version" : n,                     (numeric) The version
  "locktime" : xxx,                  (numeric) The lock time
  "vin" : [                          (json array)
    {                                (json object)
      "coinbase" : "hex",            (string, optional) The coinbase value (only if coinbase transaction)
      "txid" : "hex",                (string, optional) The transaction id (if not coinbase transaction)
      "vout" : n,                    (numeric, optional) The output number (if not coinbase transaction)
      "scriptSig" : {                (json object, optional) The script (if not coinbase transaction)
        "asm" : "str",               (string) Disassembly of the signature script
        "hex" : "hex"                (string) The raw signature script bytes, hex-encoded
      },
      "txinwitness" : [              (json array, optional)
        "hex",                       (string) hex-encoded witness data (if any)
        ...
      ],
      "sequence" : n                 (numeric) The script sequence number
    },
    ...
  ],
  "vout" : [                         (json array)
    {                                (json object)
      "value" : n,                   (numeric) The value in BTC
      "n" : n,                       (numeric) index
      "scriptPubKey" : {             (json object)
        "asm" : "str",               (string) Disassembly of the output script
        "desc" : "str",              (string) Inferred descriptor for the output
        "hex" : "hex",               (string) The raw output script bytes, hex-encoded
        "address" : "str",           (string, optional) The Bitcoin address (only if a well-defined address exists)
        "type" : "str"               (string) The type (one of: nonstandard, anchor, pubkey, pubkeyhash, scripthash, multisig, nulldata, witness_v0_scripthash, witness_v0_keyhash, witness_v1_taproot, witness_unknown)
      }
    },
    ...
  ]
}

Result (for verbosity = 2):
{                                    (json object)
  ...,                               Same output as verbosity = 1
  "fee" : n,                         (numeric, optional) transaction fee in BTC, omitted if block undo data is not available
  "vin" : [                          (json array)
    {                                (json object) utxo being spent
      ...,                           Same vin fields as verbosity = 1
      "prevout" : {                  (json object, optional) The previous output, omitted if block undo data is not available
        "generated" : true|false,    (boolean) Coinbase or not
        "height" : n,                (numeric) The height of the prevout
        "value" : n,                 (numeric) The value in BTC
        "scriptPubKey" : {           (json object)
          "asm" : "str",             (string) Disassembly of the output script
          "desc" : "str",            (string) Inferred descriptor for the output
          "hex" : "hex",             (string) The raw output script bytes, hex-encoded
          "address" : "str",         (string, optional) The Bitcoin address (only if a well-defined address exists)
          "type" : "str"             (string) The type (one of: nonstandard, anchor, pubkey, pubkeyhash, scripthash, multisig, nulldata, witness_v0_scripthash, witness_v0_keyhash, witness_v1_taproot, witness_unknown)
        }
      }
    },
    ...
  ]
}

Examples:
> bitcoin-cli getrawtransaction "mytxid"
> bitcoin-cli getrawtransaction "mytxid" 1
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getrawtransaction", "params": ["mytxid", 1]}' -H 'content-type: application/json' http://127.0.0.1:8332/
> bitcoin-cli getrawtransaction "mytxid" 0 "myblockhash"
> bitcoin-cli getrawtransaction "mytxid" 1 "myblockhash"
> bitcoin-cli getrawtransaction "mytxid" 2 "myblockhash"
```

### joinpsbts

```
joinpsbts ["psbt",...]

Joins multiple distinct version 0 PSBTs with different inputs and outputs into one version 0 PSBT with inputs and outputs from all of the PSBTs
No input in any of the PSBTs can be in more than one of the PSBTs.

Arguments:
1. txs            (json array, required) The base64 strings of partially signed transactions
     [
       "psbt",    (string, required) A base64 string of a PSBT
       ...
     ]

Result:
"str"    (string) The base64-encoded partially signed transaction

Examples:
> bitcoin-cli joinpsbts "psbt"
```

### sendrawtransaction

```
sendrawtransaction "hexstring" ( maxfeerate maxburnamount )

Submit a raw transaction (serialized, hex-encoded) to the network.

If -privatebroadcast is disabled, then the transaction will be put into the
local mempool of the node and will be sent unconditionally to all currently
connected peers, so using sendrawtransaction for manual rebroadcast will degrade
privacy by leaking the transaction's origin, as nodes will normally not
rebroadcast non-wallet transactions already in their mempool.

If -privatebroadcast is enabled, then the transaction will be sent only via
dedicated, short-lived connections to Tor or I2P peers or IPv4/IPv6 peers
via the Tor network. This conceals the transaction's origin. The transaction
will only enter the local mempool when it is received back from the network.
The private broadcast queue is bounded: when it is full, this RPC fails and
the transaction is not scheduled, until an existing one completes or is
aborted. Use getprivatebroadcastinfo to inspect the queue and abortprivatebroadcast to abort.

A specific exception, RPC_TRANSACTION_ALREADY_IN_UTXO_SET, may throw if the transaction cannot be added to the mempool.

Related RPCs: createrawtransaction, signrawtransactionwithkey

Arguments:
1. hexstring        (string, required) The hex string of the raw transaction
2. maxfeerate       (numeric or string, optional, default="0.10") Reject transactions whose fee rate is higher than the specified value, expressed in BTC/kvB.
                    Fee rates larger than 1BTC/kvB are rejected.
                    Set to 0 to accept any fee rate.
3. maxburnamount    (numeric or string, optional, default="0.00") Reject transactions with provably unspendable outputs (e.g. 'datacarrier' outputs that use the OP_RETURN opcode) greater than the specified value, expressed in BTC.
                    If burning funds through unspendable outputs is desired, increase this value.
                    This check is based on heuristics and does not guarantee spendability of outputs.
                    

Result:
"hex"    (string) The transaction hash in hex

Examples:

Create a transaction
> bitcoin-cli createrawtransaction "[{\"txid\" : \"mytxid\",\"vout\":0}]" "{\"myaddress\":0.01}"
Sign the transaction, and get back the hex
> bitcoin-cli signrawtransactionwithwallet "myhex"

Send the transaction (signed hex)
> bitcoin-cli sendrawtransaction "signedhex"

As a JSON-RPC call
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "sendrawtransaction", "params": ["signedhex"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### signrawtransactionwithkey

```
signrawtransactionwithkey "hexstring" ["privatekey",...] ( [{"txid":"hex","vout":n,"scriptPubKey":"hex","redeemScript":"hex","witnessScript":"hex","amount":amount},...] "sighashtype" )

Sign inputs for raw transaction (serialized, hex-encoded).
The second argument is an array of base58-encoded private
keys that will be the only keys used to sign the transaction.
The third optional argument (may be null) is an array of previous transaction outputs that
this transaction depends on but may not yet be in the block chain.

Arguments:
1. hexstring                        (string, required) The transaction hex string
2. privkeys                         (json array, required) The base58-encoded private keys for signing
     [
       "privatekey",                (string) private key in base58-encoding
       ...
     ]
3. prevtxs                          (json array, optional) The previous dependent transaction outputs
     [
       {                            (json object)
         "txid": "hex",             (string, required) The transaction id
         "vout": n,                 (numeric, required) The output number
         "scriptPubKey": "hex",     (string, required) output script
         "redeemScript": "hex",     (string, optional) (required for P2SH) redeem script
         "witnessScript": "hex",    (string, optional) (required for P2WSH or P2SH-P2WSH) witness script
         "amount": amount,          (numeric or string, optional) (required for Segwit inputs) the amount spent
       },
       ...
     ]
4. sighashtype                      (string, optional, default="DEFAULT for Taproot, ALL otherwise") The signature hash type. Must be one of:
                                    "DEFAULT"
                                    "ALL"
                                    "NONE"
                                    "SINGLE"
                                    "ALL|ANYONECANPAY"
                                    "NONE|ANYONECANPAY"
                                    "SINGLE|ANYONECANPAY"
                                    

Result:
{                             (json object)
  "hex" : "hex",              (string) The hex-encoded raw transaction with signature(s)
  "complete" : true|false,    (boolean) If the transaction has a complete set of signatures
  "errors" : [                (json array, optional) Script verification errors (if there are any)
    {                         (json object)
      "txid" : "hex",         (string) The hash of the referenced, previous transaction
      "vout" : n,             (numeric) The index of the output to spent and used as input
      "witness" : [           (json array)
        "hex",                (string)
        ...
      ],
      "scriptSig" : "hex",    (string) The hex-encoded signature script
      "sequence" : n,         (numeric) Script sequence number
      "error" : "str"         (string) Verification or signing error related to the input
    },
    ...
  ]
}

Examples:
> bitcoin-cli signrawtransactionwithkey "myhex" "[\"key1\",\"key2\"]"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "signrawtransactionwithkey", "params": ["myhex", "[\"key1\",\"key2\"]"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### submitpackage

```
submitpackage ["rawtx",...] ( maxfeerate maxburnamount )

Submit a package of raw transactions (serialized, hex-encoded) to local node.
The package will be validated according to consensus and mempool policy rules. If any transaction passes, it will be accepted to mempool.
This RPC is experimental and the interface may be unstable. Refer to doc/policy/packages.md for documentation on package policies.
Warning: successful submission does not mean the transactions will propagate throughout the network.

Arguments:
1. package          (json array, required) An array of raw transactions.
                    The package must consist of a transaction with (some, all, or none of) its unconfirmed parents. A single transaction is permitted.
                    None of the parents may depend on each other. Parents that are already in mempool do not need to be present in the package.
                    The package must be topologically sorted, with the child being the last element in the array if there are multiple elements.
     [
       "rawtx",     (string)
       ...
     ]
2. maxfeerate       (numeric or string, optional, default="0.10") Reject transactions whose fee rate is higher than the specified value, expressed in BTC/kvB.
                    Fee rates larger than 1BTC/kvB are rejected.
                    Set to 0 to accept any fee rate.
3. maxburnamount    (numeric or string, optional, default="0.00") Reject transactions with provably unspendable outputs (e.g. 'datacarrier' outputs that use the OP_RETURN opcode) greater than the specified value, expressed in BTC.
                    If burning funds through unspendable outputs is desired, increase this value.
                    This check is based on heuristics and does not guarantee spendability of outputs.
                    

Result:
{                                   (json object)
  "package_msg" : "str",            (string) The transaction package result message. "success" indicates all transactions were accepted into or are already in the mempool.
  "tx-results" : {                  (json object) The transaction results keyed by wtxid. An entry is returned for every submitted wtxid.
    "wtxid" : {                     (json object) transaction wtxid
      "txid" : "hex",               (string) The transaction hash in hex
      "other-wtxid" : "hex",        (string, optional) The wtxid of a different transaction with the same txid but different witness found in the mempool. This means the submitted transaction was ignored.
      "vsize_adjusted" : n,         (numeric, optional) Maximum of sigop-adjusted size (-bytespersigop) and virtual transaction size as defined in BIP 141.
      "vsize" : n,                  (numeric, optional) (DEPRECATED) Was previously erroneously described as the BIP 141 vsize, but is actually sigops-adjusted vsize.
                                    Use vsize_bip141 to actually get that behavior or switch to the explicit vsize_adjusted for retained behavior.
      "vsize_bip141" : n,           (numeric, optional) Virtual transaction size as defined in BIP 141.
      "fees" : {                    (json object, optional) Transaction fees
        "base" : n,                 (numeric) transaction fee in BTC
        "effective-feerate" : n,    (numeric, optional) if the transaction was not already in the mempool, the effective feerate in BTC per KvB. For example, the package feerate and/or feerate with modified fees from prioritisetransaction.
        "effective-includes" : [    (json array, optional) if effective-feerate is provided, the wtxids of the transactions whose fees and vsizes are included in effective-feerate.
          "hex",                    (string) transaction wtxid in hex
          ...
        ]
      },
      "error" : "str"               (string, optional) Error string if rejected from mempool, or "package-not-validated" when the package aborts before any per-tx processing.
    },
    ...
  },
  "replaced-transactions" : [       (json array, optional) List of txids of replaced transactions
    "hex",                          (string) The transaction id
    ...
  ]
}

Examples:
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "submitpackage", "params": [["raw-parent-tx-1", "raw-parent-tx-2", "raw-child-tx"]]}' -H 'content-type: application/json' http://127.0.0.1:8332/
> bitcoin-cli submitpackage '["raw-tx-without-unconfirmed-parents"]'
```

### testmempoolaccept

```
testmempoolaccept ["rawtx",...] ( maxfeerate )

Returns result of mempool acceptance tests indicating if raw transaction(s) (serialized, hex-encoded) would be accepted by mempool.

If multiple transactions are passed in, parents must come before children and package policies apply: the transactions cannot conflict with any mempool transactions or each other.

If one transaction fails, other transactions may not be fully validated (the 'allowed' key will be blank).

The maximum number of transactions allowed is 25.

This checks if transactions violate the consensus or policy rules.

See sendrawtransaction call.

Arguments:
1. rawtxs          (json array, required) An array of hex strings of raw transactions.
     [
       "rawtx",    (string)
       ...
     ]
2. maxfeerate      (numeric or string, optional, default="0.10") Reject transactions whose fee rate is higher than the specified value, expressed in BTC/kvB.
                   Fee rates larger than 1BTC/kvB are rejected.
                   Set to 0 to accept any fee rate.

Result:
[                                 (json array) The result of the mempool acceptance test for each raw transaction in the input array.
                                  Returns results for each transaction in the same order they were passed in.
                                  Transactions that cannot be fully validated due to failures in other transactions will not contain an 'allowed' result.
                                  
  {                               (json object)
    "txid" : "hex",               (string) The transaction hash in hex
    "wtxid" : "hex",              (string) The transaction witness hash in hex
    "package-error" : "str",      (string, optional) Package validation error, if any (only possible if rawtxs had more than 1 transaction).
    "allowed" : true|false,       (boolean, optional) Whether this tx would be accepted to the mempool and pass client-specified maxfeerate. If not present, the tx was not fully validated due to a failure in another tx in the list.
    "vsize_adjusted" : n,         (numeric, optional) Maximum of sigop-adjusted size (-bytespersigop) and virtual transaction size as defined in BIP 141 (only present when 'allowed' is true).
    "vsize" : n,                  (numeric, optional) (DEPRECATED) Was previously erroneously described as the BIP 141 vsize, but is actually sigops-adjusted vsize.
                                  Use vsize_bip141 to actually get that behavior or switch to the explicit vsize_adjusted for retained behavior.
    "vsize_bip141" : n,           (numeric, optional) Virtual transaction size as defined in BIP 141.
                                  This is different from actual serialized size for witness transactions as witness data is discounted (only present when 'allowed' is true).
    "fees" : {                    (json object, optional) Transaction fees (only present if 'allowed' is true)
      "base" : n,                 (numeric) transaction fee in BTC
      "effective-feerate" : n,    (numeric) the effective feerate in BTC per KvB. May differ from the base feerate if, for example, there are modified fees from prioritisetransaction or a package feerate was used.
      "effective-includes" : [    (json array) transactions whose fees and vsizes are included in effective-feerate.
        "hex",                    (string) transaction wtxid in hex
        ...
      ]
    },
    "reject-reason" : "str",      (string, optional) Rejection reason (only present when 'allowed' is false)
    "reject-details" : "str"      (string, optional) Rejection details (only present when 'allowed' is false and rejection details exist)
  },
  ...
]

Examples:

Create a transaction
> bitcoin-cli createrawtransaction "[{\"txid\" : \"mytxid\",\"vout\":0}]" "{\"myaddress\":0.01}"
Sign the transaction, and get back the hex
> bitcoin-cli signrawtransactionwithwallet "myhex"

Test acceptance of the transaction (signed hex)
> bitcoin-cli testmempoolaccept '["signedhex"]'

As a JSON-RPC call
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "testmempoolaccept", "params": [["signedhex"]]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### utxoupdatepsbt

```
utxoupdatepsbt "psbt" ( ["",{"desc":"str","range":n or [n,n]},...] )

Updates all segwit inputs and outputs in a PSBT with data from output descriptors, the UTXO set, txindex, or the mempool.

Arguments:
1. psbt                          (string, required) A base64 string of a PSBT
2. descriptors                   (json array, optional) An array of either strings or objects
     [
       "",                       (string) An output descriptor
       {                         (json object) An object with an output descriptor and extra information
         "desc": "str",          (string, required) An output descriptor
         "range": n or [n,n],    (numeric or array, optional, default=1000) Up to what index HD chains should be explored (either end or [begin,end])
       },
       ...
     ]

Result:
"str"    (string) The base64-encoded partially signed transaction with inputs updated

Examples:
> bitcoin-cli utxoupdatepsbt "psbt"
```


## Signer

### enumeratesigners

```
enumeratesigners

Returns a list of external signers from -signer. Signers with duplicate master key fingerprints are skipped.

Result:
{                               (json object)
  "signers" : [                 (json array)
    {                           (json object)
      "fingerprint" : "hex",    (string) Master key fingerprint
      "name" : "str"            (string) Device name, the model returned by the signer
    },
    ...
  ]
}

Examples:
> bitcoin-cli enumeratesigners 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "enumeratesigners", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```


## Util

### createmultisig

```
createmultisig nrequired ["key",...] ( "address_type" )

Creates a multi-signature address with n signatures of m keys required.
It returns a json object with the address and redeemScript.

Arguments:
1. nrequired       (numeric, required) The number of required signatures out of the m keys.
2. keys            (json array, required) The hex-encoded public keys.
     [
       "key",      (string) The hex-encoded public key
       ...
     ]
3. address_type    (string, optional, default="legacy") The address type to use. Options are "legacy", "p2sh-segwit", and "bech32".

Result:
{                            (json object)
  "address" : "str",         (string) The value of the new multisig address.
  "redeemScript" : "hex",    (string) The string value of the hex-encoded redemption script.
  "descriptor" : "str",      (string) The descriptor for this multisig
  "warnings" : [             (json array, optional) Any warnings resulting from the creation of this multisig
    "str",                   (string)
    ...
  ]
}

Examples:

Create a multisig address from 2 public keys
> bitcoin-cli createmultisig 2 "[\"03789ed0bb717d88f7d321a368d905e7430207ebbd82bd342cf11ae157a7ace5fd\",\"03dbc6764b8884a92e871274b87583e6d5c2a58819473e17e107ef3f6aa5a61626\"]"

As a JSON-RPC call
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "createmultisig", "params": [2, ["03789ed0bb717d88f7d321a368d905e7430207ebbd82bd342cf11ae157a7ace5fd","03dbc6764b8884a92e871274b87583e6d5c2a58819473e17e107ef3f6aa5a61626"]]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### deriveaddresses

```
deriveaddresses "descriptor" ( range )

Derives one or more addresses corresponding to an output descriptor.
Examples of output descriptors are:
    pkh(<pubkey>)                                     P2PKH outputs for the given pubkey
    wpkh(<pubkey>)                                    Native segwit P2PKH outputs for the given pubkey
    sh(multi(<n>,<pubkey>,<pubkey>,...))              P2SH-multisig outputs for the given threshold and pubkeys
    raw(<hex script>)                                 Outputs whose output script equals the specified hex-encoded bytes
    tr(<pubkey>,multi_a(<n>,<pubkey>,<pubkey>,...))   P2TR-multisig outputs for the given threshold and pubkeys

In the above, <pubkey> either refers to a fixed public key in hexadecimal notation, or to an xpub/xprv optionally followed by one
or more path elements separated by "/", where "h" represents a hardened child key.
For more information on output descriptors, see the documentation in the doc/descriptors.md file.

Arguments:
1. descriptor    (string, required) The descriptor.
2. range         (numeric or array, optional) If a ranged descriptor is used, this specifies the end or the range (in [begin,end] notation) to derive.

Result (for single derivation descriptors):
[           (json array)
  "str",    (string) the derived addresses
  ...
]

Result (for multipath descriptors):
[             (json array) The derived addresses for each of the multipath expansions of the descriptor, in multipath specifier order
  [           (json array) The derived addresses for a multipath descriptor expansion
    "str",    (string) the derived address
    ...
  ],
  ...
]

Examples:
First three native segwit receive addresses
> bitcoin-cli deriveaddresses "wpkh([d34db33f/84h/0h/0h]xpub6DJ2dNUysrn5Vt36jH2KLBT2i1auw1tTSSomg8PhqNiUtx8QX2SvC9nrHu81fT41fvDUnhMjEzQgXnQjKEu3oaqMSzhSrHMxyyoEAmUHQbY/0/*)#cjjspncu" "[0,2]"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "deriveaddresses", "params": ["wpkh([d34db33f/84h/0h/0h]xpub6DJ2dNUysrn5Vt36jH2KLBT2i1auw1tTSSomg8PhqNiUtx8QX2SvC9nrHu81fT41fvDUnhMjEzQgXnQjKEu3oaqMSzhSrHMxyyoEAmUHQbY/0/*)#cjjspncu", "[0,2]"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### estimatesmartfee

```
estimatesmartfee conf_target ( "estimate_mode" {"fee_rate_estimator":"str","verbosity":n} )

Estimates the approximate fee per kilobyte needed for a transaction to begin
confirmation within conf_target blocks if possible and return the number of blocks
for which the estimate is valid. Uses virtual transaction size as defined
in BIP 141 (witness data is discounted).

Arguments:
1. conf_target                         (numeric, required) Confirmation target in blocks (1 - 1008)
2. estimate_mode                       (string, optional, default="economical") The fee estimate mode.
                                       unset, economical, conservative 
                                       unset means no mode set (default mode will be used). 
                                       economical mode potentially returns a lower fee rate estimate.
                                       conservative potentially returns a higher fee rate estimate.
                                       
3. options                             (json object, optional)
     {
       "fee_rate_estimator": "str",    (string, optional, default="none") Selects which fee rate estimator to use.
                                       "none" returns the lower of the block policy and mempool estimates. If the mempool
                                       estimate is unavailable, it returns that error instead of falling back to the block
                                       policy estimate; use "block_policy" in that case to get the block policy estimate.
                                       "block_policy" uses only the block policy fee rate estimator.
                                       "mempool_policy" uses only the mempool fee rate estimator.
                                       Unknown values are treated as "none".
       "verbosity": n,                 (numeric, optional, default=1) 1 returns feerate or errors. 2 also returns "mempool_health_statistics".
     }

Result:
{                                    (json object)
  "feerate" : n,                     (numeric, optional) estimate fee rate in BTC/kvB (only present if no errors were encountered)
  "estimator" : "str",               (string, optional) the fee estimator used to produce the result (only present for successful estimates when fee_rate_estimator is "none")
  "errors" : [                       (json array, optional) Errors encountered during processing (if there are any)
    "str",                           (string) error
    ...
  ],
  "blocks" : n,                      (numeric) the confirmation target in blocks for the returned fee rate estimate.
                                     For the block policy fee rate estimator, this is the target the estimate was found at, clamped to at
                                     least 2 and at most the estimator's maximum usable target. For the mempool fee rate
                                     estimator, it is always 2.
  "mempool_health_statistics" : [    (json array, optional) Health statistics for the most recently mined blocks tracked by the mempool fee rate estimator (only present when verbosity >= 2)
    {                                (json object)
      "block_height" : n,            (numeric) Block height
      "block_weight" : n,            (numeric) Total weight of non-coinbase transactions in the block
      "mempool_txs_weight" : n       (numeric) Total weight of transactions removed from the mempool for this block
    },
    ...
  ]
}

Examples:
> bitcoin-cli estimatesmartfee 6
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "estimatesmartfee", "params": [6]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getdescriptorinfo

```
getdescriptorinfo "descriptor"

Analyses a descriptor.

Arguments:
1. descriptor    (string, required) The descriptor.

Result:
{                                   (json object)
  "descriptor" : "str",             (string) The descriptor, without private keys. For a multipath descriptor, only the first will be returned.
  "multipath_expansion" : [         (json array, optional) All descriptors produced by expanding multipath derivation elements. Only if the provided descriptor specifies multipath derivation elements.
    "str",                          (string)
    ...
  ],
  "checksum" : "str",               (string) The checksum for the input descriptor
  "isrange" : true|false,           (boolean) Whether the descriptor is ranged
  "issolvable" : true|false,        (boolean) Whether the descriptor is solvable
  "hasprivatekeys" : true|false     (boolean) Whether the input descriptor contained at least one private key
}

Examples:
Analyse a descriptor
> bitcoin-cli getdescriptorinfo "wpkh([d34db33f/84h/0h/0h]0279be667ef9dcbbac55a06295Ce870b07029Bfcdb2dce28d959f2815b16f81798)"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getdescriptorinfo", "params": ["wpkh([d34db33f/84h/0h/0h]0279be667ef9dcbbac55a06295Ce870b07029Bfcdb2dce28d959f2815b16f81798)"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getindexinfo

```
getindexinfo ( "index_name" )

Returns the status of one or all available indices currently running in the node.

Arguments:
1. index_name    (string, optional) Filter results for an index with a specific name.

Result:
{                               (json object)
  "name" : {                    (json object) The name of the index
    "synced" : true|false,      (boolean) Whether the index is synced or not
    "best_block_height" : n     (numeric) The block height to which the index is synced
  },
  ...
}

Examples:
> bitcoin-cli getindexinfo 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getindexinfo", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
> bitcoin-cli getindexinfo txindex
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getindexinfo", "params": ["txindex"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### signmessagewithprivkey

```
signmessagewithprivkey "privkey" "message"

Sign a message with the private key of an address

Arguments:
1. privkey    (string, required) The private key to sign the message with.
2. message    (string, required) The message to create a signature of.

Result:
"str"    (string) The signature of the message encoded in base 64

Examples:

Create the signature
> bitcoin-cli signmessagewithprivkey "privkey" "my message"

Verify the signature
> bitcoin-cli verifymessage "1D1ZrZNe3JUo7ZycKEYQQiQAWd9y54F4XX" "signature" "my message"

As a JSON-RPC call
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "signmessagewithprivkey", "params": ["privkey", "my message"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### validateaddress

```
validateaddress "address"

Return information about the given bitcoin address.

Arguments:
1. address    (string, required) The bitcoin address to validate

Result:
{                               (json object)
  "isvalid" : true|false,       (boolean) If the address is valid or not
  "address" : "str",            (string, optional) The bitcoin address validated
  "scriptPubKey" : "hex",       (string, optional) The hex-encoded output script generated by the address
  "isscript" : true|false,      (boolean, optional) If the key is a script
  "iswitness" : true|false,     (boolean, optional) If the address is a witness address
  "witness_version" : n,        (numeric, optional) The version number of the witness program
  "witness_program" : "hex",    (string, optional) The hex value of the witness program
  "error" : "str",              (string, optional) Error message, if any
  "error_locations" : [         (json array, optional) Indices of likely error locations in address, if known (e.g. Bech32 errors)
    n,                          (numeric) index of a potential error
    ...
  ]
}

Examples:
> bitcoin-cli validateaddress "bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "validateaddress", "params": ["bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### verifymessage

```
verifymessage "address" "signature" "message"

Verify a signed message.

Arguments:
1. address      (string, required) The bitcoin address to use for the signature.
2. signature    (string, required) The signature provided by the signer in base 64 encoding (see signmessage).
3. message      (string, required) The message that was signed.

Result:
true|false    (boolean) If the signature is verified or not.

Examples:

Unlock the wallet for 30 seconds
> bitcoin-cli walletpassphrase "mypassphrase" 30

Create the signature
> bitcoin-cli signmessage "1D1ZrZNe3JUo7ZycKEYQQiQAWd9y54F4XX" "my message"

Verify the signature
> bitcoin-cli verifymessage "1D1ZrZNe3JUo7ZycKEYQQiQAWd9y54F4XX" "signature" "my message"

As a JSON-RPC call
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "verifymessage", "params": ["1D1ZrZNe3JUo7ZycKEYQQiQAWd9y54F4XX", "signature", "my message"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```


## Wallet

### abandontransaction

```
abandontransaction "txid"

Mark in-wallet transaction <txid> as abandoned
This will mark this transaction and all its in-wallet descendants as abandoned which will allow
for their inputs to be respent.  It can be used to replace "stuck" or evicted transactions.
It only works on transactions which are not included in a block and are not currently in the mempool.
It has no effect on transactions which are already abandoned.

Arguments:
1. txid    (string, required) The transaction id

Result:
null    (json null)

Examples:
> bitcoin-cli abandontransaction "1075db55d416d3ca199f55b6084e2115b9345e16c5cf302fc80e9d5fbf5d48d"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "abandontransaction", "params": ["1075db55d416d3ca199f55b6084e2115b9345e16c5cf302fc80e9d5fbf5d48d"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### abortrescan

```
abortrescan

Stops current wallet rescan triggered by an RPC call, e.g. by a rescanblockchain call.
Note: Use "getwalletinfo" to query the scanning progress.

Result:
true|false    (boolean) Whether the abort was successful

Examples:

Import a private key
> bitcoin-cli rescanblockchain 

Abort the running wallet rescan
> bitcoin-cli abortrescan 

As a JSON-RPC call
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "abortrescan", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### addhdkey

```
addhdkey ( "hdkey" )

Add a BIP 32 HD key to the wallet that can be used with 'createwalletdescriptor'

Arguments:
1. hdkey    (string, optional, default=Automatically generated new key) The BIP 32 extended private key to add. If none is provided, a randomly generated one will be added.

Result:
{                    (json object)
  "xpub" : "str"     (string) The xpub of the HD key that was added to the wallet
}

Examples:
> bitcoin-cli addhdkey xprv
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "addhdkey", "params": ["xprv"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### backupwallet

```
backupwallet "destination"

Safely copies the current wallet file to the specified destination, which can either be a directory or a path with a filename.

Arguments:
1. destination    (string, required) The destination directory or file

Result:
null    (json null)

Examples:
> bitcoin-cli backupwallet "backup.dat"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "backupwallet", "params": ["backup.dat"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### bumpfee

```
bumpfee "txid" ( options )

Bumps the fee of a transaction T, replacing it with a new transaction B.
A transaction with the given txid must be in the wallet.
The command will pay the additional fee by reducing change outputs or adding inputs when necessary.
It may add a new change output if one does not already exist.
All inputs in the original transaction will be included in the replacement transaction.
The command will fail if the wallet or mempool contains a transaction that spends one of T's outputs.
By default, the new fee will be calculated automatically using the estimatesmartfee RPC.
The user can specify a confirmation target for estimatesmartfee.
Alternatively, the user can specify a fee rate in sat/vB for the new transaction.
At a minimum, the new fee rate must be high enough to pay an additional new relay fee (incrementalfee
returned by getnetworkinfo) to enter the node's mempool.
* WARNING: before version 0.21, fee_rate was in BTC/kvB. As of 0.21, fee_rate is in sat/vB. *

Arguments:
1. txid       (string, required) The txid to be bumped
2. options    (json object, optional) Options object that can be used to pass named arguments, listed below.

Named Arguments:
conf_target                    (numeric, optional, default=wallet -txconfirmtarget) Confirmation target in blocks
                               
fee_rate                       (numeric or string, optional, default=not set, fall back to wallet fee estimation) 
                               Specify a fee rate in sat/vB instead of relying on the built-in fee estimator.
                               Must be at least 0.100 sat/vB higher than the current transaction fee rate.
                               WARNING: before version 0.21, fee_rate was in BTC/kvB. As of 0.21, fee_rate is in sat/vB.
                               
replaceable                    (boolean, optional, default=true) Whether the new transaction should be
                               marked bip-125 replaceable. If true, the sequence numbers in the transaction will
                               be set to 0xfffffffd. If false, any input sequence numbers in the
                               transaction will be set to 0xfffffffe
                               so the new transaction will not be explicitly bip-125 replaceable (though it may
                               still be replaceable in practice, for example if it has unconfirmed ancestors which
                               are replaceable).
                               
estimate_mode                  (string, optional, default="unset") The fee estimate mode, must be one of (case insensitive):
                               unset, economical, conservative 
                               unset means no mode set (economical mode is used if the transaction is replaceable;
                               otherwise, conservative mode is used). 
                               economical mode potentially returns a lower fee rate estimate.
                               conservative potentially returns a higher fee rate estimate.
                               
outputs                        (json array, optional, default=[]) The outputs specified as key-value pairs.
                               Each key may only appear once, i.e. there can only be one 'data' output, and no address may be duplicated.
                               At least one output of either type must be specified.
                               Cannot be provided if 'original_change_index' is specified.
     [
       {                       (json object)
         "address": amount,    (numeric or string, required) A key-value pair. The key (string) is the bitcoin address,
                               the value (float or string) is the amount in BTC
         ...
       },
       {                       (json object)
         "data": "hex",        (string, required) A key-value pair. The key must be "data", the value is hex-encoded data that becomes a part of an OP_RETURN output
       },
       ...
     ]
original_change_index          (numeric, optional, default=not set, detect change automatically) The 0-based index of the change output on the original transaction. The indicated output will be recycled into the new change output on the bumped transaction. The remainder after paying the recipients and fees will be sent to the output script of the original change output. The change output’s amount can increase if bumping the transaction adds new inputs, otherwise it will decrease. Cannot be used in combination with the 'outputs' option.

Result:
{                    (json object)
  "txid" : "hex",    (string) The id of the new transaction.
  "origfee" : n,     (numeric) The fee of the replaced transaction.
  "fee" : n,         (numeric) The fee of the new transaction.
  "errors" : [       (json array) Errors encountered during processing (may be empty).
    "str",           (string)
    ...
  ]
}

Examples:

Bump the fee, get the new transaction's txid
> bitcoin-cli bumpfee <txid>
```

### createwallet

```
createwallet "wallet_name" ( disable_private_keys blank "passphrase" avoid_reuse descriptors load_on_startup external_signer )

Creates and loads a new wallet.

Arguments:
1. wallet_name             (string, required) The name for the new wallet. If this is a path, the wallet will be created at the path location.
2. disable_private_keys    (boolean, optional, default=false) Disable the possibility of private keys (only watchonlys are possible in this mode).
3. blank                   (boolean, optional, default=false) Create a blank wallet. A blank wallet has no keys.
4. passphrase              (string, optional) Encrypt the wallet with this passphrase.
5. avoid_reuse             (boolean, optional, default=false) Keep track of coin reuse, and treat dirty and clean coins differently with privacy considerations in mind.
6. descriptors             (boolean, optional, default=true) If set, must be "true"
7. load_on_startup         (boolean, optional) Save wallet name to persistent settings and load on startup. True to add wallet to startup list, false to remove, null to leave unchanged.
8. external_signer         (boolean, optional, default=false) Use an external signer such as a hardware wallet. Requires -signer to be configured. Wallet creation will fail if keys cannot be fetched. Requires disable_private_keys and descriptors set to true.

Result:
{                    (json object)
  "name" : "str",    (string) The wallet name if created successfully. If the wallet was created using a full path, the wallet_name will be the full path.
  "warnings" : [     (json array, optional) Warning messages, if any, related to creating and loading the wallet.
    "str",           (string)
    ...
  ]
}

Examples:
> bitcoin-cli createwallet "testwallet"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "createwallet", "params": ["testwallet"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
> bitcoin-cli -named createwallet wallet_name=descriptors avoid_reuse=true load_on_startup=true
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "createwallet", "params": {"wallet_name":"descriptors","avoid_reuse":true,"load_on_startup":true}}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### createwalletdescriptor

```
createwalletdescriptor "type" ( {"internal":bool,"hdkey":"str",...} )

Creates the wallet's descriptor for the given address type. The address type must be one that the wallet does not already have a descriptor for.
Requires wallet passphrase to be set with walletpassphrase call if wallet is encrypted.

Arguments:
1. type       (string, required) The address type the descriptor will produce. Options are "legacy", "p2sh-segwit", "bech32", "bech32m".
2. options    (json object, optional) Options object that can be used to pass named arguments, listed below.

Named Arguments:
internal    (boolean, optional, default=Both external and internal will be generated unless this parameter is specified) Whether to only make one descriptor that is internal (if parameter is true) or external (if parameter is false)
hdkey       (string, optional, default=The HD key used by all other active descriptors) The HD key that the wallet knows the private key of, listed using 'gethdkeys', to use for this descriptor's key

Result:
{                (json object)
  "descs" : [    (json array) The public descriptors that were added to the wallet
    "str",       (string)
    ...
  ]
}

Examples:
> bitcoin-cli createwalletdescriptor bech32m
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "createwalletdescriptor", "params": ["bech32m"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### derivehdkey

```
derivehdkey "path" ( {"private":bool,"hdkey":"str",...} )

Derive extended public or private key from HD key in the wallet at a given path.
Derivation uses wallet private key material.

Requires wallet passphrase to be set with walletpassphrase call if wallet is encrypted.

Arguments:
1. path       (string, required) BIP 32 derivation path with at least one hardened step.
2. options    (json object, optional) Options object that can be used to pass named arguments, listed below.

Named Arguments:
private    (boolean, optional, default=false) Show private key
hdkey      (string, optional, default=Either the HD key of an unused(KEY) descriptor, or any other active descriptor.) The HD key that the wallet knows the private key of, listed using 'gethdkeys', to use for derivation

Result:
{                      (json object)
  "origin" : "str",    (string) Fingerprint and path for use in descriptors
  "xpub" : "str",      (string) The extended public key
  "xprv" : "str"       (string, optional) The extended private key if "private" is true
}

Examples:
> bitcoin-cli derivehdkey m/87h/0h/0h
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "derivehdkey", "params": ["m/87h/0h/0h"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
> bitcoin-cli -named derivehdkey path=m/87h/0h/0h private=true
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "derivehdkey", "params": {"path":"m/87h/0h/0h","private":"true"}}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### encryptwallet

```
encryptwallet "passphrase"

Encrypts the wallet with 'passphrase'. This is for first time encryption.
After this, any calls that interact with private keys such as sending or signing 
will require the passphrase to be set prior to making these calls.
Use the walletpassphrase call for this, and then walletlock call.
If the wallet is already encrypted, use the walletpassphrasechange call.
** IMPORTANT **
For security reasons, the encryption process will generate a new HD seed, resulting
in the creation of a fresh set of active descriptors. Therefore, it is crucial to
securely back up the newly generated wallet file using the backupwallet RPC.

Arguments:
1. passphrase    (string, required) The pass phrase to encrypt the wallet with. It must be at least 1 character, but should be long.

Result:
"str"    (string) A string with further instructions

Examples:

Encrypt your wallet
> bitcoin-cli encryptwallet "my pass phrase"

Now set the passphrase to use the wallet, such as for signing or sending bitcoin
> bitcoin-cli walletpassphrase "my pass phrase"

Now we can do something like sign
> bitcoin-cli signmessage "address" "test message"

Now lock the wallet again by removing the passphrase
> bitcoin-cli walletlock 

As a JSON-RPC call
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "encryptwallet", "params": ["my pass phrase"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### exportwatchonlywallet

```
exportwatchonlywallet "destination"

Creates a wallet file at the specified destination containing a watchonly version of the current wallet. This watchonly wallet contains the wallet's public descriptors, its transactions, and address book data. Descriptors that use hardened derivation will only have a limited number of derived keys included in the export due to hardened derivation requiring private keys. Descriptors with unhardened derivation do not have this limitation. The watchonly wallet can be imported into another node using 'restorewallet'.

Arguments:
1. destination    (string, required) The path to the filename the exported watchonly wallet will be saved to

Result:
{                             (json object)
  "exported_file" : "str"     (string) The full path that the file has been exported to
}

Examples:
> bitcoin-cli exportwatchonlywallet "/path/to/export.dat"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "exportwatchonlywallet", "params": ["/path/to/export.dat"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getaddressesbylabel

```
getaddressesbylabel "label"

Returns the list of addresses assigned the specified label.

Arguments:
1. label    (string, required) The label.

Result:
{                         (json object) json object with addresses as keys
  "address" : {           (json object) json object with information about address
    "purpose" : "str"     (string) Purpose of address ("send" for sending address, "receive" for receiving address)
  },
  ...
}

Examples:
> bitcoin-cli getaddressesbylabel "tabby"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getaddressesbylabel", "params": ["tabby"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getaddressinfo

```
getaddressinfo "address"

Return information about the given bitcoin address.
Some of the information will only be present if the address is in the active wallet.

Arguments:
1. address    (string, required) The bitcoin address for which to get information.

Result:
{                                   (json object)
  "address" : "str",                (string) The bitcoin address validated.
  "scriptPubKey" : "hex",           (string) The hex-encoded output script generated by the address.
  "ismine" : true|false,            (boolean) If the address is yours.
  "iswatchonly" : true|false,       (boolean) (DEPRECATED) Always false.
  "solvable" : true|false,          (boolean) If we know how to spend coins sent to this address, ignoring the possible lack of private keys.
  "desc" : "str",                   (string, optional) A descriptor for spending coins sent to this address (only when solvable).
  "parent_desc" : "str",            (string, optional) The descriptor used to derive this address if this is a descriptor wallet
  "isscript" : true|false,          (boolean, optional) If the key is a script.
  "ischange" : true|false,          (boolean) If the address was used for change output.
  "iswitness" : true|false,         (boolean) If the address is a witness address.
  "witness_version" : n,            (numeric, optional) The version number of the witness program.
  "witness_program" : "hex",        (string, optional) The hex value of the witness program.
  "script" : "str",                 (string, optional) The output script type. Only if isscript is true and the redeemscript is known. Possible
                                    types: nonstandard, pubkey, pubkeyhash, scripthash, multisig, nulldata, witness_v0_keyhash,
                                    witness_v0_scripthash, witness_unknown.
  "hex" : "hex",                    (string, optional) The redeemscript for the p2sh address.
  "pubkeys" : [                     (json array, optional) Array of pubkeys associated with the known redeemscript (only if script is multisig).
    "str",                          (string)
    ...
  ],
  "sigsrequired" : n,               (numeric, optional) The number of signatures required to spend multisig output (only if script is multisig).
  "pubkey" : "hex",                 (string, optional) The hex value of the raw public key for single-key addresses (possibly embedded in P2SH or P2WSH).
  "embedded" : {                    (json object, optional) Information about the address embedded in P2SH or P2WSH, if relevant and known.
    ...                             Includes all getaddressinfo output fields for the embedded address, excluding metadata (timestamp, hdkeypath, hdseedid)
                                    and relation to the wallet (ismine).
  },
  "iscompressed" : true|false,      (boolean, optional) If the pubkey is compressed.
  "timestamp" : xxx,                (numeric, optional) The creation time of the key, if available, expressed in UNIX epoch time.
  "hdkeypath" : "str",              (string, optional) The HD keypath, if the key is HD and available.
  "hdseedid" : "hex",               (string, optional) The Hash160 of the HD seed.
  "hdmasterfingerprint" : "hex",    (string, optional) The fingerprint of the master key.
  "labels" : [                      (json array) Array of labels associated with the address. Currently limited to one label but returned
                                    as an array to keep the API stable if multiple labels are enabled in the future.
    "str",                          (string) Label name (defaults to "").
    ...
  ]
}

Examples:
> bitcoin-cli getaddressinfo "bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getaddressinfo", "params": ["bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getbalance

```
getbalance ( "dummy" minconf include_watchonly avoid_reuse )

Returns the total available balance.
The available balance is what the wallet considers currently spendable, and is
thus affected by options which limit spendability such as -spendzeroconfchange.

Arguments:
1. dummy                (string, optional) Remains for backward compatibility. Must be excluded or set to "*".
2. minconf              (numeric, optional, default=0) Only include transactions confirmed at least this many times.
3. include_watchonly    (boolean, optional, default=false) No longer used
4. avoid_reuse          (boolean, optional, default=true) (only available if avoid_reuse wallet flag is set) Do not include balance in dirty outputs; addresses are considered dirty if they have previously been used in a transaction.

Result:
n    (numeric) The total amount in BTC received for this wallet.

Examples:

The total amount in the wallet with 0 or more confirmations
> bitcoin-cli getbalance 

The total amount in the wallet with at least 6 confirmations
> bitcoin-cli getbalance "*" 6

As a JSON-RPC call
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getbalance", "params": ["*", 6]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getbalances

```
getbalances

Returns an object with all balances in BTC.

Result:
{                               (json object)
  "mine" : {                    (json object) balances from outputs that the wallet can sign
    "trusted" : n,              (numeric) trusted balance (outputs created by the wallet or confirmed outputs)
    "untrusted_pending" : n,    (numeric) untrusted pending balance (outputs created by others that are in the mempool)
    "immature" : n,             (numeric) balance from immature coinbase outputs
    "nonmempool" : n,           (numeric) sum of coins that are spent by transactions not in the mempool (usually an over-estimate due to not accounting for change or spends that conflict with each other)
    "used" : n                  (numeric, optional) (only present if avoid_reuse is set) balance from coins sent to addresses that were previously spent from (potentially privacy violating)
  },
  "lastprocessedblock" : {      (json object) hash and height of the block this information was generated on
    "hash" : "hex",             (string) hash of the block this information was generated on
    "height" : n                (numeric) height of the block this information was generated on
  }
}

Examples:
> bitcoin-cli getbalances 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getbalances", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### gethdkeys

```
gethdkeys ( {"active_only":bool,"private":bool,...} )

List all BIP 32 HD keys in the wallet and which descriptors use them.

Arguments:
1. options    (json object, optional) Options object that can be used to pass named arguments, listed below.

Named Arguments:
active_only    (boolean, optional, default=false) Show the keys for only active descriptors
private        (boolean, optional, default=false) Show private keys

Result:
[                                  (json array)
  {                                (json object)
    "xpub" : "str",                (string) The extended public key
    "has_private" : true|false,    (boolean) Whether the wallet has the private key for this xpub
    "xprv" : "str",                (string, optional) The extended private key if "private" is true
    "descriptors" : [              (json array) Array of descriptor objects that use this HD key
      {                            (json object)
        "desc" : "str",            (string) Descriptor string public representation
        "active" : true|false      (boolean) Whether this descriptor is currently used to generate new addresses
      },
      ...
    ]
  },
  ...
]

Examples:
> bitcoin-cli gethdkeys 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "gethdkeys", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
> bitcoin-cli -named gethdkeys active_only=true private=true
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "gethdkeys", "params": {"active_only":"true","private":"true"}}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getnewaddress

```
getnewaddress ( "label" "address_type" )

Returns a new Bitcoin address for receiving payments.
If 'label' is specified, it is added to the address book 
so payments received with the address will be associated with 'label'.

Arguments:
1. label           (string, optional, default="") The label name for the address to be linked to. It can also be set to the empty string "" to represent the default label. The label does not need to exist, it will be created if there is no label by the given name.
2. address_type    (string, optional, default=set by -addresstype) The address type to use. Options are "legacy", "p2sh-segwit", "bech32", "bech32m".

Result:
"str"    (string) The new bitcoin address

Examples:
> bitcoin-cli getnewaddress 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getnewaddress", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getrawchangeaddress

```
getrawchangeaddress ( "address_type" )

Returns a new Bitcoin address, for receiving change.
This is for use with raw transactions, NOT normal use.

Arguments:
1. address_type    (string, optional, default=set by -changetype) The address type to use. Options are "legacy", "p2sh-segwit", "bech32", "bech32m".

Result:
"str"    (string) The address

Examples:
> bitcoin-cli getrawchangeaddress 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getrawchangeaddress", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getreceivedbyaddress

```
getreceivedbyaddress "address" ( minconf include_immature_coinbase )

Returns the total amount received by the given address in transactions with at least minconf confirmations.

Arguments:
1. address                      (string, required) The bitcoin address for transactions.
2. minconf                      (numeric, optional, default=1) Only include transactions confirmed at least this many times.
3. include_immature_coinbase    (boolean, optional, default=false) Include immature coinbase transactions.

Result:
n    (numeric) The total amount in BTC received at this address.

Examples:

The amount from transactions with at least 1 confirmation
> bitcoin-cli getreceivedbyaddress "bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl"

The amount including unconfirmed transactions, zero confirmations
> bitcoin-cli getreceivedbyaddress "bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl" 0

The amount with at least 6 confirmations
> bitcoin-cli getreceivedbyaddress "bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl" 6

The amount with at least 6 confirmations including immature coinbase outputs
> bitcoin-cli getreceivedbyaddress "bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl" 6 true

As a JSON-RPC call
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getreceivedbyaddress", "params": ["bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl", 6]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getreceivedbylabel

```
getreceivedbylabel "label" ( minconf include_immature_coinbase )

Returns the total amount received by addresses with <label> in transactions with at least [minconf] confirmations.

Arguments:
1. label                        (string, required) The selected label, may be the default label using "".
2. minconf                      (numeric, optional, default=1) Only include transactions confirmed at least this many times.
3. include_immature_coinbase    (boolean, optional, default=false) Include immature coinbase transactions.

Result:
n    (numeric) The total amount in BTC received for this label.

Examples:

Amount received by the default label with at least 1 confirmation
> bitcoin-cli getreceivedbylabel ""

Amount received at the tabby label including unconfirmed amounts with zero confirmations
> bitcoin-cli getreceivedbylabel "tabby" 0

The amount with at least 6 confirmations
> bitcoin-cli getreceivedbylabel "tabby" 6

The amount with at least 6 confirmations including immature coinbase outputs
> bitcoin-cli getreceivedbylabel "tabby" 6 true

As a JSON-RPC call
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getreceivedbylabel", "params": ["tabby", 6, true]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### gettransaction

```
gettransaction "txid" ( include_watchonly verbose )

Get detailed information about in-wallet transaction <txid>

Arguments:
1. txid                 (string, required) The transaction id
2. include_watchonly    (boolean, optional, default=false) (DEPRECATED) No longer used
3. verbose              (boolean, optional, default=false) Whether to include a `decoded` field containing the decoded transaction (equivalent to RPC decoderawtransaction)

Result:
{                                   (json object)
  "amount" : n,                     (numeric) The amount in BTC
  "fee" : n,                        (numeric, optional) The amount of the fee in BTC. This is negative and only available for the
                                    'send' category of transactions.
  "confirmations" : n,              (numeric) The number of confirmations for the transaction. Negative confirmations means the
                                    transaction conflicted that many blocks ago.
  "generated" : true|false,         (boolean, optional) Only present if the transaction's only input is a coinbase one.
  "trusted" : true|false,           (boolean, optional) Whether we consider the transaction to be trusted and safe to spend from.
                                    Only present when the transaction has 0 confirmations (or negative confirmations, if conflicted).
  "blockhash" : "hex",              (string, optional) The block hash containing the transaction.
  "blockheight" : n,                (numeric, optional) The block height containing the transaction.
  "blockindex" : n,                 (numeric, optional) The index of the transaction in the block that includes it.
  "blocktime" : xxx,                (numeric, optional) The block time expressed in UNIX epoch time.
  "txid" : "hex",                   (string) The transaction id.
  "wtxid" : "hex",                  (string) The hash of serialized transaction, including witness data.
  "alternate_wtxids" : [            (json array) The wtxids of transactions with different witness data but the same txid.
    "hex",                          (string) The witness transaction id.
    ...
  ],
  "walletconflicts" : [             (json array) Confirmed transactions that have been detected by the wallet to conflict with this transaction.
    "hex",                          (string) The transaction id.
    ...
  ],
  "replaced_by_txid" : "hex",       (string, optional) Only if 'category' is 'send'. The txid if this tx was replaced.
  "replaces_txid" : "hex",          (string, optional) Only if 'category' is 'send'. The txid if this tx replaces another.
  "mempoolconflicts" : [            (json array) Transactions in the mempool that directly conflict with either this transaction or an ancestor transaction
    "hex",                          (string) The transaction id.
    ...
  ],
  "to" : "str",                     (string, optional) If a comment to is associated with the transaction.
  "time" : xxx,                     (numeric) The transaction time expressed in UNIX epoch time.
  "timereceived" : xxx,             (numeric) The time received expressed in UNIX epoch time.
  "comment" : "str",                (string, optional) If a comment is associated with the transaction, only present if not empty.
  "bip125-replaceable" : "str",     (string, optional) ("yes|no|unknown") (DEPRECATED) Whether this transaction signals BIP125 replaceability or has an unconfirmed ancestor signaling BIP125 replaceability.
                                    May be unknown for unconfirmed transactions not in the mempool because their unconfirmed ancestors are unknown.
  "parent_descs" : [                (json array, optional) Only if 'category' is 'receive'. List of parent descriptors for the output script of this coin.
    "str",                          (string) The descriptor string.
    ...
  ],
  "details" : [                     (json array)
    {                               (json object)
      "address" : "str",            (string, optional) The bitcoin address involved in the transaction.
      "category" : "str",           (string) The transaction category.
                                    "send"                  Transactions sent.
                                    "receive"               Non-coinbase transactions received.
                                    "generate"              Coinbase transactions received with more than 100 confirmations.
                                    "immature"              Coinbase transactions received with 100 or fewer confirmations.
                                    "orphan"                Orphaned coinbase transactions received.
      "amount" : n,                 (numeric) The amount in BTC
      "label" : "str",              (string, optional) A comment for the address/transaction, if any
      "vout" : n,                   (numeric) the vout value
      "fee" : n,                    (numeric, optional) The amount of the fee in BTC. This is negative and only available for the 
                                    'send' category of transactions.
      "abandoned" : true|false,     (boolean) 'true' if the transaction has been abandoned (inputs are respendable).
      "parent_descs" : [            (json array, optional) Only if 'category' is 'receive'. List of parent descriptors for the output script of this coin.
        "str",                      (string) The descriptor string.
        ...
      ]
    },
    ...
  ],
  "hex" : "hex",                    (string) Raw data for transaction
  "decoded" : {                     (json object, optional) The decoded transaction (only present when `verbose` is passed)
    "txid" : "hex",                 (string) The transaction id
    "hash" : "hex",                 (string) The transaction hash (differs from txid for witness transactions)
    "size" : n,                     (numeric) The serialized transaction size
    "vsize" : n,                    (numeric) The virtual transaction size (differs from size for witness transactions)
    "weight" : n,                   (numeric) The transaction's weight (between vsize*4-3 and vsize*4)
    "version" : n,                  (numeric) The version
    "locktime" : xxx,               (numeric) The lock time
    "vin" : [                       (json array)
      {                             (json object)
        "coinbase" : "hex",         (string, optional) The coinbase value (only if coinbase transaction)
        "txid" : "hex",             (string, optional) The transaction id (if not coinbase transaction)
        "vout" : n,                 (numeric, optional) The output number (if not coinbase transaction)
        "scriptSig" : {             (json object, optional) The script (if not coinbase transaction)
          "asm" : "str",            (string) Disassembly of the signature script
          "hex" : "hex"             (string) The raw signature script bytes, hex-encoded
        },
        "txinwitness" : [           (json array, optional)
          "hex",                    (string) hex-encoded witness data (if any)
          ...
        ],
        "sequence" : n              (numeric) The script sequence number
      },
      ...
    ],
    "vout" : [                      (json array)
      {                             (json object)
        "value" : n,                (numeric) The value in BTC
        "n" : n,                    (numeric) index
        "scriptPubKey" : {          (json object)
          "asm" : "str",            (string) Disassembly of the output script
          "desc" : "str",           (string) Inferred descriptor for the output
          "hex" : "hex",            (string) The raw output script bytes, hex-encoded
          "address" : "str",        (string, optional) The Bitcoin address (only if a well-defined address exists)
          "type" : "str"            (string) The type (one of: nonstandard, anchor, pubkey, pubkeyhash, scripthash, multisig, nulldata, witness_v0_scripthash, witness_v0_keyhash, witness_v1_taproot, witness_unknown)
        },
        "ischange" : true|false     (boolean, optional) Output script is change (only present if true)
      },
      ...
    ]
  },
  "lastprocessedblock" : {          (json object) hash and height of the block this information was generated on
    "hash" : "hex",                 (string) hash of the block this information was generated on
    "height" : n                    (numeric) height of the block this information was generated on
  }
}

Examples:
> bitcoin-cli gettransaction "1075db55d416d3ca199f55b6084e2115b9345e16c5cf302fc80e9d5fbf5d48d"
> bitcoin-cli gettransaction "1075db55d416d3ca199f55b6084e2115b9345e16c5cf302fc80e9d5fbf5d48d" true
> bitcoin-cli gettransaction "1075db55d416d3ca199f55b6084e2115b9345e16c5cf302fc80e9d5fbf5d48d" false true
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "gettransaction", "params": ["1075db55d416d3ca199f55b6084e2115b9345e16c5cf302fc80e9d5fbf5d48d"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### getwalletinfo

```
getwalletinfo

Returns an object containing various wallet state info.

Result:
{                                         (json object)
  "walletname" : "str",                   (string) the wallet name
  "walletversion" : n,                    (numeric) (DEPRECATED) only related to unsupported legacy wallet, returns the latest version 169900 for backwards compatibility
  "format" : "str",                       (string) the database format (only sqlite)
  "txcount" : n,                          (numeric) the total number of transactions in the wallet
  "keypoolsize" : n,                      (numeric) how many new keys are pre-generated (only counts external keys)
  "keypoolsize_hd_internal" : n,          (numeric) how many new keys are pre-generated for internal use (used for change outputs; 0 if external keys are used for change)
  "unlocked_until" : xxx,                 (numeric, optional) the UNIX epoch time until which the wallet is unlocked for transfers, or 0 if the wallet is locked (only present for passphrase-encrypted wallets)
  "private_keys_enabled" : true|false,    (boolean) false if privatekeys are disabled for this wallet (enforced watch-only wallet)
  "avoid_reuse" : true|false,             (boolean) whether this wallet tracks clean/dirty coins in terms of reuse
  "scanning" : {                          (json object) current scanning details, or false if no scan is in progress
    "duration" : n,                       (numeric) elapsed seconds since scan start
    "progress" : n                        (numeric) scanning progress percentage [0.0, 1.0]
  },
  "descriptors" : true|false,             (boolean) whether this wallet uses descriptors for output script management
  "external_signer" : true|false,         (boolean) whether this wallet is configured to use an external signer such as a hardware wallet
  "blank" : true|false,                   (boolean) Whether this wallet intentionally does not contain any keys, scripts, or descriptors
  "birthtime" : xxx,                      (numeric, optional) The start time for blocks scanning. It could be modified by (re)importing any descriptor with an earlier timestamp.
  "flags" : [                             (json array) The flags currently set on the wallet
    "str",                                (string) The name of the flag
    ...
  ],
  "lastprocessedblock" : {                (json object) hash and height of the block this information was generated on
    "hash" : "hex",                       (string) hash of the block this information was generated on
    "height" : n                          (numeric) height of the block this information was generated on
  }
}

Examples:
> bitcoin-cli getwalletinfo 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getwalletinfo", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### importdescriptors

```
importdescriptors requests

Import descriptors. This will trigger a rescan of the blockchain based on the earliest timestamp of all descriptors being imported. Requires a new wallet backup.
When importing descriptors with multipath key expressions, if the multipath specifier contains exactly two elements, the descriptor produced from the second element will be imported as an internal descriptor.

Note: This call can take over an hour to complete if using an early timestamp; during that time, other rpc calls
may report that the imported keys, addresses or scripts exist but related transactions are still missing.
The rescan is significantly faster if block filters are available (using startup option "-blockfilterindex=1").

Arguments:
1. requests                                 (json array, required) Data to be imported
     [
       {                                    (json object)
         "desc": "str",                     (string, required) Descriptor to import.
         "active": bool,                    (boolean, optional, default=false) Set this descriptor to be the active descriptor for the corresponding output type/externality
         "range": n or [n,n],               (numeric or array, optional) If a ranged descriptor is used, this specifies the end or the range (in the form [begin,end]) to import
         "next_index": n,                   (numeric, optional) If a ranged descriptor is set to active, this specifies the next index to generate addresses from
         "timestamp": timestamp | "now",    (integer / string, required) Time from which to start rescanning the blockchain for this descriptor, in UNIX epoch time
                                            Use the string "now" to substitute the current synced blockchain time.
                                            "now" can be specified to bypass scanning, for outputs which are known to never have been used, and
                                            0 can be specified to scan the entire blockchain. Blocks up to 2 hours before the earliest timestamp
                                            of all descriptors being imported will be scanned as well as the mempool.
         "internal": bool,                  (boolean, optional, default=false) Whether matching outputs should be treated as not incoming payments (e.g. change)
         "label": "str",                    (string, optional, default="") Label to assign to the address, only allowed with internal=false. Disabled for ranged descriptors
       },
       ...
     ]

Result:
[                              (json array) Response is an array with the same size as the input that has the execution result
  {                            (json object)
    "success" : true|false,    (boolean)
    "warnings" : [             (json array, optional)
      "str",                   (string)
      ...
    ],
    "error" : {                (json object, optional)
      "code" : n,              (numeric) JSONRPC error code
      "message" : "str"        (string) JSONRPC error message
    }
  },
  ...
]

Examples:
> bitcoin-cli importdescriptors '[{ "desc": "<my descriptor>", "timestamp":1455191478, "internal": true }, { "desc": "<my descriptor 2>", "label": "example 2", "timestamp": 1455191480 }]'
> bitcoin-cli importdescriptors '[{ "desc": "<my descriptor>", "timestamp":1455191478, "active": true, "range": [0,100], "label": "<my bech32 wallet>" }]'
```

### importprunedfunds

```
importprunedfunds "rawtransaction" "txoutproof"

Imports funds without rescan. Corresponding address or script must previously be included in wallet. Aimed towards pruned wallets. The end-user is responsible to import additional transactions that subsequently spend the imported outputs or rescan after the point in the blockchain the transaction is included.

Arguments:
1. rawtransaction    (string, required) A raw transaction in hex funding an already-existing address in wallet
2. txoutproof        (string, required) The hex output from gettxoutproof that contains the transaction

Result:
null    (json null)
```

### keypoolrefill

```
keypoolrefill ( newsize )

Refills each descriptor keypool in the wallet up to the specified number of new keys.
By default, descriptor wallets have 4 active ranged descriptors ("legacy", "p2sh-segwit", "bech32", "bech32m"), each with 1000 entries.

Requires wallet passphrase to be set with walletpassphrase call if wallet is encrypted.

Arguments:
1. newsize    (numeric, optional, default=1000, or as set by -keypool) The new keypool size

Result:
null    (json null)

Examples:
> bitcoin-cli keypoolrefill 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "keypoolrefill", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### listaddressgroupings

```
listaddressgroupings

Lists groups of addresses which have had their common ownership
made public by common use as inputs or as the resulting change
in past transactions

Result:
[               (json array)
  [             (json array)
    [           (json array)
      "str",    (string) The bitcoin address
      n,        (numeric) The amount in BTC
      "str"     (string, optional) The label
    ],
    ...
  ],
  ...
]

Examples:
> bitcoin-cli listaddressgroupings 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "listaddressgroupings", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### listdescriptors

```
listdescriptors ( private )

List all descriptors present in a wallet.

Arguments:
1. private    (boolean, optional, default=false) Show private descriptors.

Result:
{                                 (json object)
  "wallet_name" : "str",          (string) Name of wallet this operation was performed on
  "descriptors" : [               (json array) Array of descriptor objects (sorted by descriptor string representation)
    {                             (json object)
      "desc" : "str",             (string) Descriptor string representation
      "timestamp" : n,            (numeric) The creation time of the descriptor
      "active" : true|false,      (boolean) Whether this descriptor is currently used to generate new addresses
      "internal" : true|false,    (boolean, optional) True if this descriptor is used to generate change addresses. False if this descriptor is used to generate receiving addresses; defined only for active descriptors
      "range" : [                 (json array, optional) Defined only for ranged descriptors
        n,                        (numeric) Range start inclusive
        n                         (numeric) Range end inclusive
      ],
      "next" : n,                 (numeric, optional) Same as next_index field. Kept for compatibility reason.
      "next_index" : n            (numeric, optional) The next index to generate addresses from; defined only for ranged descriptors
    },
    ...
  ]
}

Examples:
> bitcoin-cli listdescriptors 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "listdescriptors", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
> bitcoin-cli listdescriptors true
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "listdescriptors", "params": [true]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### listlabels

```
listlabels ( "purpose" )

Returns the list of all labels, or labels that are assigned to addresses with a specific purpose.

Arguments:
1. purpose    (string, optional) Address purpose to list labels for ('send','receive'). An empty string is the same as not providing this argument.

Result:
[           (json array)
  "str",    (string) Label name
  ...
]

Examples:

List all labels
> bitcoin-cli listlabels 

List labels that have receiving addresses
> bitcoin-cli listlabels receive

List labels that have sending addresses
> bitcoin-cli listlabels send

As a JSON-RPC call
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "listlabels", "params": ["receive"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### listlockunspent

```
listlockunspent

Returns list of temporarily unspendable outputs.
See the lockunspent call to lock and unlock transactions for spending.

Result:
[                      (json array)
  {                    (json object)
    "txid" : "hex",    (string) The transaction id locked
    "vout" : n         (numeric) The vout value
  },
  ...
]

Examples:

List the unspent transactions
> bitcoin-cli listunspent 

Lock an unspent transaction
> bitcoin-cli lockunspent false "[{\"txid\":\"a08e6907dbbd3d809776dbfc5d82e371b764ed838b5655e72f463568df1aadf0\",\"vout\":1}]"

List the locked transactions
> bitcoin-cli listlockunspent 

Unlock the transaction again
> bitcoin-cli lockunspent true "[{\"txid\":\"a08e6907dbbd3d809776dbfc5d82e371b764ed838b5655e72f463568df1aadf0\",\"vout\":1}]"

As a JSON-RPC call
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "listlockunspent", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### listreceivedbyaddress

```
listreceivedbyaddress ( minconf include_empty include_watchonly "address_filter" include_immature_coinbase )

List balances by receiving address.

Arguments:
1. minconf                      (numeric, optional, default=1) The minimum number of confirmations before payments are included.
2. include_empty                (boolean, optional, default=false) Whether to include addresses that haven't received any payments.
3. include_watchonly            (boolean, optional, default=false) (DEPRECATED) No longer used
4. address_filter               (string, optional) If present and non-empty, only return information on this address.
5. include_immature_coinbase    (boolean, optional, default=false) Include immature coinbase transactions.

Result:
[                           (json array)
  {                         (json object)
    "address" : "str",      (string) The receiving address
    "amount" : n,           (numeric) The total amount in BTC received by the address
    "confirmations" : n,    (numeric) The number of confirmations of the most recent transaction included
    "label" : "str",        (string) The label of the receiving address. The default label is ""
    "txids" : [             (json array)
      "hex",                (string) The ids of transactions received with the address
      ...
    ]
  },
  ...
]

Examples:
> bitcoin-cli listreceivedbyaddress 
> bitcoin-cli listreceivedbyaddress 6 true
> bitcoin-cli listreceivedbyaddress 6 true true "" true
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "listreceivedbyaddress", "params": [6, true, true]}' -H 'content-type: application/json' http://127.0.0.1:8332/
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "listreceivedbyaddress", "params": [6, true, true, "bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl", true]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### listreceivedbylabel

```
listreceivedbylabel ( minconf include_empty include_watchonly include_immature_coinbase )

List received transactions by label.

Arguments:
1. minconf                      (numeric, optional, default=1) The minimum number of confirmations before payments are included.
2. include_empty                (boolean, optional, default=false) Whether to include labels that haven't received any payments.
3. include_watchonly            (boolean, optional, default=false) (DEPRECATED) No longer used
4. include_immature_coinbase    (boolean, optional, default=false) Include immature coinbase transactions.

Result:
[                           (json array)
  {                         (json object)
    "amount" : n,           (numeric) The total amount received by addresses with this label
    "confirmations" : n,    (numeric) The number of confirmations of the most recent transaction included
    "label" : "str"         (string) The label of the receiving address. The default label is ""
  },
  ...
]

Examples:
> bitcoin-cli listreceivedbylabel 
> bitcoin-cli listreceivedbylabel 6 true
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "listreceivedbylabel", "params": [6, true, true, true]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### listsinceblock

```
listsinceblock ( "blockhash" target_confirmations include_watchonly include_removed include_change "label" )

Get all transactions in blocks since block [blockhash], or all transactions if omitted.
If "blockhash" is no longer a part of the main chain, transactions from the fork point onward are included.
Additionally, if include_removed is set, transactions affecting the wallet which were removed are returned in the "removed" array.

Arguments:
1. blockhash               (string, optional) If set, the block hash to list transactions since, otherwise list all transactions.
2. target_confirmations    (numeric, optional, default=1) Return the nth block hash from the main chain. e.g. 1 would mean the best block hash. Note: this is not used as a filter, but only affects [lastblock] in the return value
3. include_watchonly       (boolean, optional, default=false) (DEPRECATED) No longer used
4. include_removed         (boolean, optional, default=true) Show transactions that were removed due to a reorg in the "removed" array
                           (not guaranteed to work on pruned nodes)
5. include_change          (boolean, optional, default=false) Also add entries for change outputs.
                           
6. label                   (string, optional) Return only incoming transactions paying to addresses with the specified label.
                           

Result:
{                                      (json object)
  "transactions" : [                   (json array)
    {                                  (json object)
      "address" : "str",               (string, optional) The bitcoin address of the transaction (not returned if the output does not have an address, e.g. OP_RETURN null data).
      "category" : "str",              (string) The transaction category.
                                       "send"                  Transactions sent.
                                       "receive"               Non-coinbase transactions received.
                                       "generate"              Coinbase transactions received with more than 100 confirmations.
                                       "immature"              Coinbase transactions received with 100 or fewer confirmations.
                                       "orphan"                Orphaned coinbase transactions received.
      "amount" : n,                    (numeric) The amount in BTC. This is negative for the 'send' category, and is positive
                                       for all other categories
      "vout" : n,                      (numeric) the vout value
      "fee" : n,                       (numeric, optional) The amount of the fee in BTC. This is negative and only available for the
                                       'send' category of transactions.
      "confirmations" : n,             (numeric) The number of confirmations for the transaction. Negative confirmations means the
                                       transaction conflicted that many blocks ago.
      "generated" : true|false,        (boolean, optional) Only present if the transaction's only input is a coinbase one.
      "trusted" : true|false,          (boolean, optional) Whether we consider the transaction to be trusted and safe to spend from.
                                       Only present when the transaction has 0 confirmations (or negative confirmations, if conflicted).
      "blockhash" : "hex",             (string, optional) The block hash containing the transaction.
      "blockheight" : n,               (numeric, optional) The block height containing the transaction.
      "blockindex" : n,                (numeric, optional) The index of the transaction in the block that includes it.
      "blocktime" : xxx,               (numeric, optional) The block time expressed in UNIX epoch time.
      "txid" : "hex",                  (string) The transaction id.
      "wtxid" : "hex",                 (string) The hash of serialized transaction, including witness data.
      "alternate_wtxids" : [           (json array) The wtxids of transactions with different witness data but the same txid.
        "hex",                         (string) The witness transaction id.
        ...
      ],
      "walletconflicts" : [            (json array) Confirmed transactions that have been detected by the wallet to conflict with this transaction.
        "hex",                         (string) The transaction id.
        ...
      ],
      "replaced_by_txid" : "hex",      (string, optional) Only if 'category' is 'send'. The txid if this tx was replaced.
      "replaces_txid" : "hex",         (string, optional) Only if 'category' is 'send'. The txid if this tx replaces another.
      "mempoolconflicts" : [           (json array) Transactions in the mempool that directly conflict with either this transaction or an ancestor transaction
        "hex",                         (string) The transaction id.
        ...
      ],
      "to" : "str",                    (string, optional) If a comment to is associated with the transaction.
      "time" : xxx,                    (numeric) The transaction time expressed in UNIX epoch time.
      "timereceived" : xxx,            (numeric) The time received expressed in UNIX epoch time.
      "comment" : "str",               (string, optional) If a comment is associated with the transaction, only present if not empty.
      "bip125-replaceable" : "str",    (string, optional) ("yes|no|unknown") (DEPRECATED) Whether this transaction signals BIP125 replaceability or has an unconfirmed ancestor signaling BIP125 replaceability.
                                       May be unknown for unconfirmed transactions not in the mempool because their unconfirmed ancestors are unknown.
      "parent_descs" : [               (json array, optional) Only if 'category' is 'receive'. List of parent descriptors for the output script of this coin.
        "str",                         (string) The descriptor string.
        ...
      ],
      "abandoned" : true|false,        (boolean) 'true' if the transaction has been abandoned (inputs are respendable).
      "label" : "str"                  (string, optional) A comment for the address/transaction, if any
    },
    ...
  ],
  "removed" : [                        (json array, optional) <structure is the same as "transactions" above, only present if include_removed=true>
                                       Note: transactions that were re-added in the active chain will appear as-is in this array, and may thus have a positive confirmation count.
    ...
  ],
  "lastblock" : "hex"                  (string) The hash of the block (target_confirmations-1) from the best block on the main chain, or the genesis hash if the referenced block does not exist yet. This is typically used to feed back into listsinceblock the next time you call it. So you would generally use a target_confirmations of say 6, so you will be continually re-notified of transactions until they've reached 6 confirmations plus any new ones
}

Examples:
> bitcoin-cli listsinceblock 
> bitcoin-cli listsinceblock "000000000000000bacf66f7497b7dc45ef753ee9a7d38571037cdb1a57f663ad" 6
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "listsinceblock", "params": ["000000000000000bacf66f7497b7dc45ef753ee9a7d38571037cdb1a57f663ad", 6]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### listtransactions

```
listtransactions ( "label" count skip include_watchonly )

If a label name is provided, this will return only incoming transactions paying to addresses with the specified label.
Returns up to 'count' most recent transactions ordered from oldest to newest while skipping the first number of 
transactions specified in the 'skip' argument. A transaction can have multiple entries in this RPC response. 
For instance, a wallet transaction that pays three addresses — one wallet-owned and two external — will produce 
four entries. The payment to the wallet-owned address appears both as a send entry and as a receive entry. 
As a result, the RPC response will contain one entry in the receive category and three entries in the send category.

Arguments:
1. label                (string, optional) If set, should be a valid label name to return only incoming transactions
                        with the specified label, or "*" to disable filtering and return all transactions.
2. count                (numeric, optional, default=10) The number of transactions to return
3. skip                 (numeric, optional, default=0) The number of transactions to skip
4. include_watchonly    (boolean, optional, default=false) (DEPRECATED) No longer used

Result:
[                                    (json array)
  {                                  (json object)
    "address" : "str",               (string, optional) The bitcoin address of the transaction (not returned if the output does not have an address, e.g. OP_RETURN null data).
    "category" : "str",              (string) The transaction category.
                                     "send"                  Transactions sent.
                                     "receive"               Non-coinbase transactions received.
                                     "generate"              Coinbase transactions received with more than 100 confirmations.
                                     "immature"              Coinbase transactions received with 100 or fewer confirmations.
                                     "orphan"                Orphaned coinbase transactions received.
    "amount" : n,                    (numeric) The amount in BTC. This is negative for the 'send' category, and is positive
                                     for all other categories
    "label" : "str",                 (string, optional) A comment for the address/transaction, if any
    "vout" : n,                      (numeric) the vout value
    "fee" : n,                       (numeric, optional) The amount of the fee in BTC. This is negative and only available for the
                                     'send' category of transactions.
    "confirmations" : n,             (numeric) The number of confirmations for the transaction. Negative confirmations means the
                                     transaction conflicted that many blocks ago.
    "generated" : true|false,        (boolean, optional) Only present if the transaction's only input is a coinbase one.
    "trusted" : true|false,          (boolean, optional) Whether we consider the transaction to be trusted and safe to spend from.
                                     Only present when the transaction has 0 confirmations (or negative confirmations, if conflicted).
    "blockhash" : "hex",             (string, optional) The block hash containing the transaction.
    "blockheight" : n,               (numeric, optional) The block height containing the transaction.
    "blockindex" : n,                (numeric, optional) The index of the transaction in the block that includes it.
    "blocktime" : xxx,               (numeric, optional) The block time expressed in UNIX epoch time.
    "txid" : "hex",                  (string) The transaction id.
    "wtxid" : "hex",                 (string) The hash of serialized transaction, including witness data.
    "alternate_wtxids" : [           (json array) The wtxids of transactions with different witness data but the same txid.
      "hex",                         (string) The witness transaction id.
      ...
    ],
    "walletconflicts" : [            (json array) Confirmed transactions that have been detected by the wallet to conflict with this transaction.
      "hex",                         (string) The transaction id.
      ...
    ],
    "replaced_by_txid" : "hex",      (string, optional) Only if 'category' is 'send'. The txid if this tx was replaced.
    "replaces_txid" : "hex",         (string, optional) Only if 'category' is 'send'. The txid if this tx replaces another.
    "mempoolconflicts" : [           (json array) Transactions in the mempool that directly conflict with either this transaction or an ancestor transaction
      "hex",                         (string) The transaction id.
      ...
    ],
    "to" : "str",                    (string, optional) If a comment to is associated with the transaction.
    "time" : xxx,                    (numeric) The transaction time expressed in UNIX epoch time.
    "timereceived" : xxx,            (numeric) The time received expressed in UNIX epoch time.
    "comment" : "str",               (string, optional) If a comment is associated with the transaction, only present if not empty.
    "bip125-replaceable" : "str",    (string, optional) ("yes|no|unknown") (DEPRECATED) Whether this transaction signals BIP125 replaceability or has an unconfirmed ancestor signaling BIP125 replaceability.
                                     May be unknown for unconfirmed transactions not in the mempool because their unconfirmed ancestors are unknown.
    "parent_descs" : [               (json array, optional) Only if 'category' is 'receive'. List of parent descriptors for the output script of this coin.
      "str",                         (string) The descriptor string.
      ...
    ],
    "abandoned" : true|false         (boolean) 'true' if the transaction has been abandoned (inputs are respendable).
  },
  ...
]

Examples:

List the most recent 10 transactions in the systems
> bitcoin-cli listtransactions 

List transactions 100 to 120
> bitcoin-cli listtransactions "*" 20 100

As a JSON-RPC call
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "listtransactions", "params": ["*", 20, 100]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### listunspent

```
listunspent ( minconf maxconf ["address",...] include_unsafe query_options )

Returns array of unspent transaction outputs
with between minconf and maxconf (inclusive) confirmations.
Optionally filter to only include txouts paid to specified addresses.

Arguments:
1. minconf           (numeric, optional, default=1) The minimum confirmations to filter
2. maxconf           (numeric, optional, default=9999999) The maximum confirmations to filter
3. addresses         (json array, optional, default=[]) The bitcoin addresses to filter
     [
       "address",    (string) bitcoin address
       ...
     ]
4. include_unsafe    (boolean, optional, default=true) Include outputs that are not safe to spend
                     See description of "safe" attribute below.
5. query_options     (json object, optional) Options object that can be used to pass named arguments, listed below.

Named Arguments:
minimumAmount                (numeric or string, optional, default="0.00") Minimum value of each UTXO in BTC
maximumAmount                (numeric or string, optional, default=unlimited) Maximum value of each UTXO in BTC
maximumCount                 (numeric, optional, default=unlimited) Maximum number of UTXOs
minimumSumAmount             (numeric or string, optional, default=unlimited) Minimum sum value of all UTXOs in BTC
include_immature_coinbase    (boolean, optional, default=false) Include immature coinbase UTXOs

Result:
[                                (json array)
  {                              (json object)
    "txid" : "hex",              (string) the transaction id
    "vout" : n,                  (numeric) the vout value
    "address" : "str",           (string, optional) the bitcoin address
    "label" : "str",             (string, optional) The associated label, or "" for the default label
    "scriptPubKey" : "hex",      (string) the output script
    "amount" : n,                (numeric) the transaction output amount in BTC
    "confirmations" : n,         (numeric) The number of confirmations
    "ancestorcount" : n,         (numeric, optional) The number of in-mempool ancestor transactions, including this one (if transaction is in the mempool)
    "ancestorsize" : n,          (numeric, optional) The virtual transaction size of in-mempool ancestors, including this one (if transaction is in the mempool)
    "ancestorfees" : n,          (numeric, optional) The total fees of in-mempool ancestors (including this one) with fee deltas used for mining priority in sat (if transaction is in the mempool)
    "redeemScript" : "hex",      (string, optional) The redeem script if the output script is P2SH
    "witnessScript" : "str",     (string, optional) witness script if the output script is P2WSH or P2SH-P2WSH
    "spendable" : true|false,    (boolean) (DEPRECATED) Always true
    "solvable" : true|false,     (boolean) Whether we know how to spend this output, ignoring the lack of keys
    "reused" : true|false,       (boolean, optional) (only present if avoid_reuse is set) Whether this output is reused/dirty (sent to an address that was previously spent from)
    "desc" : "str",              (string, optional) (only when solvable) A descriptor for spending this output
    "parent_descs" : [           (json array) List of parent descriptors for the output script of this coin.
      "str",                     (string) The descriptor string.
      ...
    ],
    "safe" : true|false          (boolean) Whether this output is considered safe to spend. Unconfirmed transactions
                                 from outside keys and unconfirmed replacement transactions are considered unsafe
                                 and are not eligible for spending by fundrawtransaction and sendtoaddress.
  },
  ...
]

Examples:
> bitcoin-cli listunspent 
> bitcoin-cli listunspent 6 9999999 "[\"bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl\",\"bc1q02ad21edsxd23d32dfgqqsz4vv4nmtfzuklhy3\"]"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "listunspent", "params": [6, 9999999, ["bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl","bc1q02ad21edsxd23d32dfgqqsz4vv4nmtfzuklhy3"]]}' -H 'content-type: application/json' http://127.0.0.1:8332/
> bitcoin-cli listunspent 6 9999999 '[]' true '{ "minimumAmount": 0.005 }'
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "listunspent", "params": [6, 9999999, [] , true, { "minimumAmount": 0.005 } ]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### listwalletdir

```
listwalletdir

Returns a list of wallets in the wallet directory.

Result:
{                        (json object)
  "wallets" : [          (json array)
    {                    (json object)
      "name" : "str",    (string) The wallet name
      "warnings" : [     (json array) Warning messages related to loading the wallet (may be empty).
        "str",           (string)
        ...
      ]
    },
    ...
  ]
}

Examples:
> bitcoin-cli listwalletdir 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "listwalletdir", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### listwallets

```
listwallets

Returns a list of currently loaded wallets.
For full information on the wallet, use "getwalletinfo"

Result:
[           (json array)
  "str",    (string) the wallet name
  ...
]

Examples:
> bitcoin-cli listwallets 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "listwallets", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### loadwallet

```
loadwallet "filename" ( load_on_startup )

Loads a wallet from a wallet file or directory.
Note that all wallet command-line options used when starting bitcoind will be
applied to the new wallet.

Arguments:
1. filename           (string, required) The path to the directory of the wallet to be loaded, either absolute or relative to the "wallets" directory. The "wallets" directory is set by the -walletdir option and defaults to the "wallets" folder within the data directory.
2. load_on_startup    (boolean, optional) Save wallet name to persistent settings and load on startup. True to add wallet to startup list, false to remove, null to leave unchanged.

Result:
{                    (json object)
  "name" : "str",    (string) The wallet name if loaded successfully.
  "warnings" : [     (json array, optional) Warning messages, if any, related to loading the wallet.
    "str",           (string)
    ...
  ]
}

Examples:

Load wallet from the wallet dir:
> bitcoin-cli loadwallet "walletname"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "loadwallet", "params": ["walletname"]}' -H 'content-type: application/json' http://127.0.0.1:8332/

Load wallet using absolute path (Unix):
> bitcoin-cli loadwallet "/path/to/walletname/"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "loadwallet", "params": ["/path/to/walletname/"]}' -H 'content-type: application/json' http://127.0.0.1:8332/

Load wallet using absolute path (Windows):
> bitcoin-cli loadwallet "DriveLetter:\path\to\walletname\"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "loadwallet", "params": ["DriveLetter:\\path\\to\\walletname"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### lockunspent

```
lockunspent unlock ( [{"txid":"hex","vout":n},...] persistent )

Updates list of temporarily unspendable outputs.
Temporarily lock (unlock=false) or unlock (unlock=true) specified transaction outputs.
If no transaction outputs are specified when unlocking then all current locked transaction outputs are unlocked.
A locked transaction output will not be chosen by automatic coin selection, when spending bitcoins.
Manually selected coins are automatically unlocked.
Locks are stored in memory only, unless persistent=true, in which case they will be written to the
wallet database and loaded on node start. Unwritten (persistent=false) locks are always cleared
(by virtue of process exit) when a node stops or fails. Unlocking will clear both persistent and not.
Also see the listunspent call

Arguments:
1. unlock                  (boolean, required) Whether to unlock (true) or lock (false) the specified transactions
2. transactions            (json array, optional, default=[]) The transaction outputs and within each, the txid (string) vout (numeric).
     [
       {                   (json object)
         "txid": "hex",    (string, required) The transaction id
         "vout": n,        (numeric, required) The output number
       },
       ...
     ]
3. persistent              (boolean, optional, default=false) Whether to write/erase this lock in the wallet database, or keep the change in memory only. Ignored for unlocking.

Result:
true|false    (boolean) Whether the command was successful or not

Examples:

List the unspent transactions
> bitcoin-cli listunspent 

Lock an unspent transaction
> bitcoin-cli lockunspent false "[{\"txid\":\"a08e6907dbbd3d809776dbfc5d82e371b764ed838b5655e72f463568df1aadf0\",\"vout\":1}]"

List the locked transactions
> bitcoin-cli listlockunspent 

Unlock the transaction again
> bitcoin-cli lockunspent true "[{\"txid\":\"a08e6907dbbd3d809776dbfc5d82e371b764ed838b5655e72f463568df1aadf0\",\"vout\":1}]"

Lock the transaction persistently in the wallet database
> bitcoin-cli lockunspent false "[{\"txid\":\"a08e6907dbbd3d809776dbfc5d82e371b764ed838b5655e72f463568df1aadf0\",\"vout\":1}]" true

As a JSON-RPC call
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "lockunspent", "params": [false, "[{\"txid\":\"a08e6907dbbd3d809776dbfc5d82e371b764ed838b5655e72f463568df1aadf0\",\"vout\":1}]"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### migratewallet

```
migratewallet ( "wallet_name" "passphrase" load_wallet )

Migrate the wallet to a descriptor wallet.
A new wallet backup will need to be made.

The migration process will create a backup of the wallet before migrating. This backup
file will be named <wallet name>-<timestamp>.legacy.bak and can be found in the directory
for this wallet. In the event of an incorrect migration, the backup can be restored using restorewallet.
Encrypted wallets must have the passphrase provided as an argument to this call.

This RPC may take a long time to complete. Increasing the RPC client timeout is recommended.

Arguments:
1. wallet_name    (string, optional, default=the wallet name from the RPC endpoint) The name of the wallet to migrate. If provided both here and in the RPC endpoint, the two must be identical.
2. passphrase     (string, optional) The wallet passphrase
3. load_wallet    (boolean, optional, default=true) Load the wallet after migration.

Result:
{                              (json object)
  "wallet_name" : "str",       (string) The name of the primary migrated wallet
  "watchonly_name" : "str",    (string, optional) The name of the migrated wallet containing the watchonly scripts
  "solvables_name" : "str",    (string, optional) The name of the migrated wallet containing solvable but not watched scripts
  "backup_path" : "str"        (string) The location of the backup of the original wallet
}

Examples:
> bitcoin-cli migratewallet 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "migratewallet", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### psbtbumpfee

```
psbtbumpfee "txid" ( options )

Bumps the fee of a transaction T, replacing it with a new transaction B.
Returns a PSBT instead of creating and signing a new transaction.
A transaction with the given txid must be in the wallet.
The command will pay the additional fee by reducing change outputs or adding inputs when necessary.
It may add a new change output if one does not already exist.
All inputs in the original transaction will be included in the replacement transaction.
The command will fail if the wallet or mempool contains a transaction that spends one of T's outputs.
By default, the new fee will be calculated automatically using the estimatesmartfee RPC.
The user can specify a confirmation target for estimatesmartfee.
Alternatively, the user can specify a fee rate in sat/vB for the new transaction.
At a minimum, the new fee rate must be high enough to pay an additional new relay fee (incrementalfee
returned by getnetworkinfo) to enter the node's mempool.
* WARNING: before version 0.21, fee_rate was in BTC/kvB. As of 0.21, fee_rate is in sat/vB. *

Arguments:
1. txid       (string, required) The txid to be bumped
2. options    (json object, optional) Options object that can be used to pass named arguments, listed below.

Named Arguments:
conf_target                    (numeric, optional, default=wallet -txconfirmtarget) Confirmation target in blocks
                               
fee_rate                       (numeric or string, optional, default=not set, fall back to wallet fee estimation) 
                               Specify a fee rate in sat/vB instead of relying on the built-in fee estimator.
                               Must be at least 0.100 sat/vB higher than the current transaction fee rate.
                               WARNING: before version 0.21, fee_rate was in BTC/kvB. As of 0.21, fee_rate is in sat/vB.
                               
replaceable                    (boolean, optional, default=true) Whether the new transaction should be
                               marked bip-125 replaceable. If true, the sequence numbers in the transaction will
                               be set to 0xfffffffd. If false, any input sequence numbers in the
                               transaction will be set to 0xfffffffe
                               so the new transaction will not be explicitly bip-125 replaceable (though it may
                               still be replaceable in practice, for example if it has unconfirmed ancestors which
                               are replaceable).
                               
estimate_mode                  (string, optional, default="unset") The fee estimate mode, must be one of (case insensitive):
                               unset, economical, conservative 
                               unset means no mode set (economical mode is used if the transaction is replaceable;
                               otherwise, conservative mode is used). 
                               economical mode potentially returns a lower fee rate estimate.
                               conservative potentially returns a higher fee rate estimate.
                               
outputs                        (json array, optional, default=[]) The outputs specified as key-value pairs.
                               Each key may only appear once, i.e. there can only be one 'data' output, and no address may be duplicated.
                               At least one output of either type must be specified.
                               Cannot be provided if 'original_change_index' is specified.
     [
       {                       (json object)
         "address": amount,    (numeric or string, required) A key-value pair. The key (string) is the bitcoin address,
                               the value (float or string) is the amount in BTC
         ...
       },
       {                       (json object)
         "data": "hex",        (string, required) A key-value pair. The key must be "data", the value is hex-encoded data that becomes a part of an OP_RETURN output
       },
       ...
     ]
original_change_index          (numeric, optional, default=not set, detect change automatically) The 0-based index of the change output on the original transaction. The indicated output will be recycled into the new change output on the bumped transaction. The remainder after paying the recipients and fees will be sent to the output script of the original change output. The change output’s amount can increase if bumping the transaction adds new inputs, otherwise it will decrease. Cannot be used in combination with the 'outputs' option.
psbt_version                   (numeric, optional, default=2) The PSBT version number to use.

Result:
{                    (json object)
  "psbt" : "str",    (string) The base64-encoded unsigned PSBT of the new transaction.
  "origfee" : n,     (numeric) The fee of the replaced transaction.
  "fee" : n,         (numeric) The fee of the new transaction.
  "errors" : [       (json array) Errors encountered during processing (may be empty).
    "str",           (string)
    ...
  ]
}

Examples:

Bump the fee, get the new transaction's psbt
> bitcoin-cli psbtbumpfee <txid>
```

### removeprunedfunds

```
removeprunedfunds "txid"

(DEPRECATED) This feature will be removed in the next major release. Start bitcoind with the `-deprecatedrpc=removeprunedfunds` option in order to use this.
Deletes the specified transaction from the wallet. Meant for use with pruned wallets and as a companion to importprunedfunds. This will affect wallet balances.

Arguments:
1. txid    (string, required) The hex-encoded id of the transaction you are deleting

Result:
null    (json null)

Examples:
> bitcoin-cli removeprunedfunds "a8d0c0184dde994a09ec054286f1ce581bebf46446a512166eae7628734ea0a5"

As a JSON-RPC call
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "removeprunedfunds", "params": ["a8d0c0184dde994a09ec054286f1ce581bebf46446a512166eae7628734ea0a5"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### rescanblockchain

```
rescanblockchain ( start_height stop_height )

Rescan the local blockchain for wallet related transactions.
Note: Use "getwalletinfo" to query the scanning progress.
The rescan is significantly faster if block filters are available
(using startup option "-blockfilterindex=1").

Arguments:
1. start_height    (numeric, optional, default=0) block height where the rescan should start
2. stop_height     (numeric, optional) the last block height that should be scanned. If none is provided it will rescan up to the tip at return time of this call.

Result:
{                        (json object)
  "start_height" : n,    (numeric) The block height where the rescan started (the requested height or 0)
  "stop_height" : n      (numeric) The height of the last rescanned block. May be null in rare cases if there was a reorg and the call didn't scan any blocks because they were already scanned in the background.
}

Examples:
> bitcoin-cli rescanblockchain 100000 120000
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "rescanblockchain", "params": [100000, 120000]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### restorewallet

```
restorewallet "wallet_name" "backup_file" ( load_on_startup )

Restores and loads a wallet from backup.

The rescan is significantly faster if block filters are available
(using startup option "-blockfilterindex=1").

Arguments:
1. wallet_name        (string, required) The name that will be applied to the restored wallet
2. backup_file        (string, required) The backup file that will be used to restore the wallet.
3. load_on_startup    (boolean, optional) Save wallet name to persistent settings and load on startup. True to add wallet to startup list, false to remove, null to leave unchanged.

Result:
{                    (json object)
  "name" : "str",    (string) The wallet name if restored successfully.
  "warnings" : [     (json array, optional) Warning messages, if any, related to restoring and loading the wallet.
    "str",           (string)
    ...
  ]
}

Examples:
> bitcoin-cli restorewallet "testwallet" "home\backups\backup-file.bak"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "restorewallet", "params": ["testwallet", "home\\backups\\backup-file.bak"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
> bitcoin-cli -named restorewallet wallet_name=testwallet backup_file=home\backups\backup-file.bak load_on_startup=true
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "restorewallet", "params": {"wallet_name":"testwallet","backup_file":"home\\backups\\backup-file.bak","load_on_startup":true}}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### send

```
send [{"address":amount,...},{"data":"hex"},...] ( conf_target "estimate_mode" fee_rate options version )

Send a transaction.

Arguments:
1. outputs                     (json array, required) The outputs specified as key-value pairs.
                               Each key may only appear once, i.e. there can only be one 'data' output, and no address may be duplicated.
                               At least one output of either type must be specified.
                               For convenience, a dictionary, which holds the key-value pairs directly, is also accepted.
     [
       {                       (json object)
         "address": amount,    (numeric or string, required) A key-value pair. The key (string) is the bitcoin address,
                               the value (float or string) is the amount in BTC
         ...
       },
       {                       (json object)
         "data": "hex",        (string, required) A key-value pair. The key must be "data", the value is hex-encoded data that becomes a part of an OP_RETURN output
       },
       ...
     ]
2. conf_target                 (numeric, optional, default=wallet -txconfirmtarget) Confirmation target in blocks
3. estimate_mode               (string, optional, default="unset") The fee estimate mode, must be one of (case insensitive):
                               unset, economical, conservative 
                               unset means no mode set (economical mode is used if the transaction is replaceable;
                               otherwise, conservative mode is used). 
                               economical mode potentially returns a lower fee rate estimate.
                               conservative potentially returns a higher fee rate estimate.
                               
4. fee_rate                    (numeric or string, optional, default=not set, fall back to wallet fee estimation) Specify a fee rate in sat/vB.
5. options                     (json object, optional) Options object that can be used to pass named arguments, listed below.
6. version                     (numeric, optional, default=2) Transaction version

Named Arguments:
add_inputs                   (boolean, optional, default=false when "inputs" are specified, true otherwise) Automatically include coins from the wallet to cover the target amount.
                             
include_unsafe               (boolean, optional, default=false) Include inputs that are not safe to spend (unconfirmed transactions from outside keys and unconfirmed replacement transactions).
                             Warning: the resulting transaction may become invalid if one of the unsafe inputs disappears.
                             If that happens, you will need to fund the transaction with different inputs and republish it.
minconf                      (numeric, optional, default=0) If add_inputs is specified, require inputs with at least this many confirmations.
maxconf                      (numeric, optional) If add_inputs is specified, require inputs with at most this many confirmations.
add_to_wallet                (boolean, optional, default=true) When false, returns a serialized transaction which will not be added to the wallet or broadcast
change_address               (string, optional, default=automatic) The bitcoin address to receive the change
change_position              (numeric, optional, default=random) The index of the change output
change_type                  (string, optional, default=set by -changetype) The output type to use. Only valid if change_address is not specified. Options are "legacy", "p2sh-segwit", "bech32", "bech32m".
fee_rate                     (numeric or string, optional, default=not set, fall back to wallet fee estimation) Specify a fee rate in sat/vB.
include_watching             (boolean, optional, default="false") (DEPRECATED) No longer used
inputs                       (json array, optional, default=[]) Specify inputs instead of adding them automatically.
     [
       {                     (json object)
         "txid": "hex",      (string, required) The transaction id
         "vout": n,          (numeric, required) The output number
         "sequence": n,      (numeric, optional, default=depends on the value of the 'replaceable' and 'locktime' arguments) The sequence number
         "weight": n,        (numeric, optional, default=Calculated from wallet and solving data) The maximum weight for this input, including the weight of the outpoint and sequence number. Note that signature sizes are not guaranteed to be consistent, so the maximum DER signatures size of 73 bytes should be used when considering ECDSA signatures.Remember to convert serialized sizes to weight units when necessary.
       },
       ...
     ]
locktime                     (numeric, optional, default=locktime close to block height to prevent fee sniping) Raw locktime. Non-0 value also locktime-activates inputs
lock_unspents                (boolean, optional, default=false) Lock selected unspent outputs
psbt                         (boolean, optional, default=automatic) Always return a PSBT, implies add_to_wallet=false.
subtract_fee_from_outputs    (json array, optional, default=[]) Outputs to subtract the fee from, specified as integer indices.
                             The fee will be equally deducted from the amount of each specified output.
                             Those recipients will receive less bitcoins than you enter in their corresponding amount field.
                             If no outputs are specified here, the sender pays the fee.
     [
       vout_index,           (numeric) The zero-based output index, before a change output is added.
       ...
     ]
max_tx_weight                (numeric, optional, default=400000) The maximum acceptable transaction weight.
                             Transaction building will fail if this can not be satisfied.
conf_target                  (numeric, optional, default=wallet -txconfirmtarget) Confirmation target in blocks
estimate_mode                (string, optional, default="unset") The fee estimate mode, must be one of (case insensitive):
                             unset, economical, conservative 
                             unset means no mode set (economical mode is used if the transaction is replaceable;
                             otherwise, conservative mode is used). 
                             economical mode potentially returns a lower fee rate estimate.
                             conservative potentially returns a higher fee rate estimate.
                             
replaceable                  (boolean, optional, default=wallet default) Marks this transaction as BIP125-replaceable.
                             Allows this transaction to be replaced by a transaction with higher fees
solving_data                 (json object, optional) Keys and scripts needed for producing a final transaction with a dummy signature.
                             Used for fee estimation during coin selection.
     {
       "pubkeys": [          (json array, optional, default=[]) Public keys involved in this transaction.
         "pubkey",           (string) A public key
         ...
       ],
       "scripts": [          (json array, optional, default=[]) Scripts involved in this transaction.
         "script",           (string) A script
         ...
       ],
       "descriptors": [      (json array, optional, default=[]) Descriptors that provide solving data for this transaction.
         "descriptor",       (string) A descriptor
         ...
       ],
     }

Result:
{                             (json object)
  "complete" : true|false,    (boolean) If the transaction has a complete set of signatures
  "txid" : "hex",             (string, optional) The transaction id for the send. Only 1 transaction is created regardless of the number of addresses.
  "hex" : "hex",              (string, optional) If add_to_wallet is false, the hex-encoded raw transaction with signature(s)
  "psbt" : "str"              (string, optional) If more signatures are needed, or if add_to_wallet is false, the base64-encoded (partially) signed transaction
}

Examples:

Send 0.1 BTC with a confirmation target of 6 blocks in economical fee estimate mode
> bitcoin-cli send '{"bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl": 0.1}' 6 economical

Send 0.2 BTC with a fee rate of 1.1 sat/vB using positional arguments
> bitcoin-cli send '{"bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl": 0.2}' null "unset" 1.1

Send 0.2 BTC with a fee rate of 1 sat/vB using the options argument
> bitcoin-cli send '{"bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl": 0.2}' null "unset" null '{"fee_rate": 1}'

Send 0.3 BTC with a fee rate of 25 sat/vB using named arguments
> bitcoin-cli -named send outputs='{"bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl": 0.3}' fee_rate=25

Create a transaction that should confirm the next block, with a specific input, and return result without adding to wallet or broadcasting to the network
> bitcoin-cli send '{"bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl": 0.1}' 1 economical null '{"add_to_wallet": false, "inputs": [{"txid":"a08e6907dbbd3d809776dbfc5d82e371b764ed838b5655e72f463568df1aadf0", "vout":1}]}'
```

### sendall

```
sendall ["address",{"address":amount,...},...] ( conf_target "estimate_mode" fee_rate options )

Spend the value of all (or specific) confirmed UTXOs and unconfirmed change in the wallet to one or more recipients.
Unconfirmed inbound UTXOs and locked UTXOs will not be spent. Sendall will respect the avoid_reuse wallet flag.
If your wallet contains many small inputs, either because it received tiny payments or as a result of accumulating change, consider using `send_max` to exclude inputs that are worth less than the fees needed to spend them.

Arguments:
1. recipients                  (json array, required) The sendall destinations. Each address may only appear once.
                               Optionally some recipients can be specified with an amount to perform payments, but at least one address must appear without a specified amount.
                               
     [
       "address",              (string, required) A bitcoin address which receives an equal share of the unspecified amount.
       {                       (json object)
         "address": amount,    (numeric or string, required) A key-value pair. The key (string) is the bitcoin address, the value (float or string) is the amount in BTC
         ...
       },
       ...
     ]
2. conf_target                 (numeric, optional, default=wallet -txconfirmtarget) Confirmation target in blocks
3. estimate_mode               (string, optional, default="unset") The fee estimate mode, must be one of (case insensitive):
                               unset, economical, conservative 
                               unset means no mode set (economical mode is used if the transaction is replaceable;
                               otherwise, conservative mode is used). 
                               economical mode potentially returns a lower fee rate estimate.
                               conservative potentially returns a higher fee rate estimate.
                               
4. fee_rate                    (numeric or string, optional, default=not set, fall back to wallet fee estimation) Specify a fee rate in sat/vB.
5. options                     (json object, optional) Options object that can be used to pass named arguments, listed below.

Named Arguments:
add_to_wallet              (boolean, optional, default=true) When false, returns the serialized transaction without broadcasting or adding it to the wallet
fee_rate                   (numeric or string, optional, default=not set, fall back to wallet fee estimation) Specify a fee rate in sat/vB.
include_watching           (boolean, optional, default=false) (DEPRECATED) No longer used
inputs                     (json array, optional, default=[]) Use exactly the specified inputs to build the transaction. Specifying inputs is incompatible with the send_max, minconf, and maxconf options.
     [
       {                   (json object)
         "txid": "hex",    (string, required) The transaction id
         "vout": n,        (numeric, required) The output number
         "sequence": n,    (numeric, optional, default=depends on the value of the 'replaceable' and 'locktime' arguments) The sequence number
       },
       ...
     ]
locktime                   (numeric, optional, default=locktime close to block height to prevent fee sniping) Raw locktime. Non-0 value also locktime-activates inputs
lock_unspents              (boolean, optional, default=false) Lock selected unspent outputs
psbt                       (boolean, optional, default=automatic) Always return a PSBT, implies add_to_wallet=false.
send_max                   (boolean, optional, default=false) When true, only use UTXOs that can pay for their own fees to maximize the output amount. When 'false' (default), no UTXO is left behind. send_max is incompatible with providing specific inputs.
minconf                    (numeric, optional, default=0) Require inputs with at least this many confirmations.
maxconf                    (numeric, optional) Require inputs with at most this many confirmations.
version                    (numeric, optional, default=2) Transaction version
conf_target                (numeric, optional, default=wallet -txconfirmtarget) Confirmation target in blocks
estimate_mode              (string, optional, default="unset") The fee estimate mode, must be one of (case insensitive):
                           unset, economical, conservative 
                           unset means no mode set (economical mode is used if the transaction is replaceable;
                           otherwise, conservative mode is used). 
                           economical mode potentially returns a lower fee rate estimate.
                           conservative potentially returns a higher fee rate estimate.
                           
replaceable                (boolean, optional, default=wallet default) Marks this transaction as BIP125-replaceable.
                           Allows this transaction to be replaced by a transaction with higher fees
solving_data               (json object, optional) Keys and scripts needed for producing a final transaction with a dummy signature.
                           Used for fee estimation during coin selection.
     {
       "pubkeys": [        (json array, optional, default=[]) Public keys involved in this transaction.
         "pubkey",         (string) A public key
         ...
       ],
       "scripts": [        (json array, optional, default=[]) Scripts involved in this transaction.
         "script",         (string) A script
         ...
       ],
       "descriptors": [    (json array, optional, default=[]) Descriptors that provide solving data for this transaction.
         "descriptor",     (string) A descriptor
         ...
       ],
     }

Result:
{                             (json object)
  "complete" : true|false,    (boolean) If the transaction has a complete set of signatures
  "txid" : "hex",             (string, optional) The transaction id for the send. Only 1 transaction is created regardless of the number of addresses.
  "hex" : "hex",              (string, optional) If add_to_wallet is false, the hex-encoded raw transaction with signature(s)
  "psbt" : "str"              (string, optional) If more signatures are needed, or if add_to_wallet is false, the base64-encoded (partially) signed transaction
}

Examples:

Spend all UTXOs from the wallet with a fee rate of 1 sat/vB using named arguments
> bitcoin-cli -named sendall recipients='["bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl"]' fee_rate=1

Spend all UTXOs with a fee rate of 1.1 sat/vB using positional arguments
> bitcoin-cli sendall '["bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl"]' null "unset" 1.1

Spend all UTXOs split into equal amounts to two addresses with a fee rate of 1.5 sat/vB using the options argument
> bitcoin-cli sendall '["bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl", "bc1q02ad21edsxd23d32dfgqqsz4vv4nmtfzuklhy3"]' null "unset" null '{"fee_rate": 1.5}'

Leave dust UTXOs in wallet, spend only UTXOs with positive effective value with a fee rate of 10 sat/vB using the options argument
> bitcoin-cli sendall '["bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl"]' null "unset" null '{"fee_rate": 10, "send_max": true}'

Spend all UTXOs with a fee rate of 1.3 sat/vB using named arguments and sending a 0.25 BTC to another recipient
> bitcoin-cli -named sendall recipients='[{"bc1q02ad21edsxd23d32dfgqqsz4vv4nmtfzuklhy3": 0.25}, "bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl"]' fee_rate=1.3
```

### sendmany

```
sendmany ( "" ) {"address":amount,...} ( minconf "comment" ["address",...] replaceable conf_target "estimate_mode" fee_rate verbose )

Send multiple times. Amounts are double-precision floating point numbers.
Requires wallet passphrase to be set with walletpassphrase call if wallet is encrypted.

Arguments:
1. dummy                     (string, optional, default="\"\"") Must be set to "" for backwards compatibility.
2. amounts                   (json object, required) The addresses and amounts
     {
       "address": amount,    (numeric or string, required) The bitcoin address is the key, the numeric amount (can be string) in BTC is the value
       ...
     }
3. minconf                   (numeric, optional) Ignored dummy value
4. comment                   (string, optional) A comment
5. subtractfeefrom           (json array, optional) The addresses.
                             The fee will be equally deducted from the amount of each selected address.
                             Those recipients will receive less bitcoins than you enter in their corresponding amount field.
                             If no addresses are specified here, the sender pays the fee.
     [
       "address",            (string) Subtract fee from this address
       ...
     ]
6. replaceable               (boolean, optional, default=wallet default) Signal that this transaction can be replaced by a transaction (BIP 125)
7. conf_target               (numeric, optional, default=wallet -txconfirmtarget) Confirmation target in blocks
8. estimate_mode             (string, optional, default="unset") The fee estimate mode, must be one of (case insensitive):
                             unset, economical, conservative 
                             unset means no mode set (economical mode is used if the transaction is replaceable;
                             otherwise, conservative mode is used). 
                             economical mode potentially returns a lower fee rate estimate.
                             conservative potentially returns a higher fee rate estimate.
                             
9. fee_rate                  (numeric or string, optional, default=not set, fall back to wallet fee estimation) Specify a fee rate in sat/vB.
10. verbose                  (boolean, optional, default=false) If true, return extra information about the transaction.

Result (if verbose is not set or set to false):
"hex"    (string) The transaction id for the send. Only 1 transaction is created regardless of
         the number of addresses.

Result (if verbose is set to true):
{                          (json object)
  "txid" : "hex",          (string) The transaction id for the send. Only 1 transaction is created regardless of
                           the number of addresses.
  "fee_reason" : "str"     (string) The reason the wallet selected this fee rate (e.g. fee rate estimator, mempool minimum, fallback, or minimum required).
}

Examples:

Send two amounts to two different addresses:
> bitcoin-cli sendmany "" "{\"bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl\":0.01,\"bc1q02ad21edsxd23d32dfgqqsz4vv4nmtfzuklhy3\":0.02}"

Send two amounts to two different addresses setting the confirmation and comment:
> bitcoin-cli sendmany "" "{\"bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl\":0.01,\"bc1q02ad21edsxd23d32dfgqqsz4vv4nmtfzuklhy3\":0.02}" 6 "testing"

Send two amounts to two different addresses, subtract fee from amount:
> bitcoin-cli sendmany "" "{\"bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl\":0.01,\"bc1q02ad21edsxd23d32dfgqqsz4vv4nmtfzuklhy3\":0.02}" 1 "" "[\"bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl\",\"bc1q02ad21edsxd23d32dfgqqsz4vv4nmtfzuklhy3\"]"

As a JSON-RPC call
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "sendmany", "params": ["", {"bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl":0.01,"bc1q02ad21edsxd23d32dfgqqsz4vv4nmtfzuklhy3":0.02}, 6, "testing"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### sendtoaddress

```
sendtoaddress "address" amount ( "comment" "comment_to" subtractfeefromamount replaceable conf_target "estimate_mode" avoid_reuse fee_rate verbose )

Send an amount to a given address.
Requires wallet passphrase to be set with walletpassphrase call if wallet is encrypted.

Arguments:
1. address                  (string, required) The bitcoin address to send to.
2. amount                   (numeric or string, required) The amount in BTC to send. eg 0.1
3. comment                  (string, optional) A comment used to store what the transaction is for.
                            This is not part of the transaction, just kept in your wallet.
4. comment_to               (string, optional) A comment to store the name of the person or organization
                            to which you're sending the transaction. This is not part of the 
                            transaction, just kept in your wallet.
5. subtractfeefromamount    (boolean, optional, default=false) The fee will be deducted from the amount being sent.
                            The recipient will receive less bitcoins than you enter in the amount field.
6. replaceable              (boolean, optional, default=wallet default) Signal that this transaction can be replaced by a transaction (BIP 125)
7. conf_target              (numeric, optional, default=wallet -txconfirmtarget) Confirmation target in blocks
8. estimate_mode            (string, optional, default="unset") The fee estimate mode, must be one of (case insensitive):
                            unset, economical, conservative 
                            unset means no mode set (economical mode is used if the transaction is replaceable;
                            otherwise, conservative mode is used). 
                            economical mode potentially returns a lower fee rate estimate.
                            conservative potentially returns a higher fee rate estimate.
                            
9. avoid_reuse              (boolean, optional, default=true) (only available if avoid_reuse wallet flag is set) Avoid spending from dirty addresses; addresses are considered
                            dirty if they have previously been used in a transaction. If true, this also activates avoidpartialspends, grouping outputs by their addresses.
10. fee_rate                (numeric or string, optional, default=not set, fall back to wallet fee estimation) Specify a fee rate in sat/vB.
11. verbose                 (boolean, optional, default=false) If true, return extra information about the transaction.

Result (if verbose is not set or set to false):
"hex"    (string) The transaction id.

Result (if verbose is set to true):
{                          (json object)
  "txid" : "hex",          (string) The transaction id.
  "fee_reason" : "str"     (string) The reason the wallet selected this fee rate (e.g. fee rate estimator, mempool minimum, fallback, or minimum required).
}

Examples:

Send 0.1 BTC
> bitcoin-cli sendtoaddress "bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl" 0.1

Send 0.1 BTC with a confirmation target of 6 blocks in economical fee estimate mode using positional arguments
> bitcoin-cli sendtoaddress "bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl" 0.1 "donation" "sean's outpost" false true 6 economical

Send 0.1 BTC with a fee rate of 1.1 sat/vB, subtract fee from amount, BIP125-replaceable, using positional arguments
> bitcoin-cli sendtoaddress "bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl" 0.1 "drinks" "room77" true true null "unset" null 1.1

Send 0.2 BTC with a confirmation target of 6 blocks in economical fee estimate mode using named arguments
> bitcoin-cli -named sendtoaddress address="bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl" amount=0.2 conf_target=6 estimate_mode="economical"

Send 0.5 BTC with a fee rate of 25 sat/vB using named arguments
> bitcoin-cli -named sendtoaddress address="bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl" amount=0.5 fee_rate=25
> bitcoin-cli -named sendtoaddress address="bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl" amount=0.5 fee_rate=25 subtractfeefromamount=false replaceable=true avoid_reuse=true comment="2 pizzas" comment_to="jeremy" verbose=true
```

### setlabel

```
setlabel "address" "label"

Sets the label associated with the given address.

Arguments:
1. address    (string, required) The bitcoin address to be associated with a label.
2. label      (string, required) The label to assign to the address.

Result:
null    (json null)

Examples:
> bitcoin-cli setlabel "bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl" "tabby"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "setlabel", "params": ["bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl", "tabby"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### setwalletflag

```
setwalletflag "flag" ( value )

Change the state of the given wallet flag for a wallet.

Arguments:
1. flag     (string, required) The name of the flag to change. Current available flags: avoid_reuse
2. value    (boolean, optional, default=true) The new state.

Result:
{                               (json object)
  "flag_name" : "str",          (string) The name of the flag that was modified
  "flag_state" : true|false,    (boolean) The new state of the flag
  "warnings" : "str"            (string, optional) Any warnings associated with the change
}

Examples:
> bitcoin-cli setwalletflag avoid_reuse
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "setwalletflag", "params": ["avoid_reuse"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### signmessage

```
signmessage "address" "message"

Sign a message with the private key of an address
Requires wallet passphrase to be set with walletpassphrase call if wallet is encrypted.

Arguments:
1. address    (string, required) The bitcoin address to use for the private key.
2. message    (string, required) The message to create a signature of.

Result:
"str"    (string) The signature of the message encoded in base 64

Examples:

Unlock the wallet for 30 seconds
> bitcoin-cli walletpassphrase "mypassphrase" 30

Create the signature
> bitcoin-cli signmessage "1D1ZrZNe3JUo7ZycKEYQQiQAWd9y54F4XX" "my message"

Verify the signature
> bitcoin-cli verifymessage "1D1ZrZNe3JUo7ZycKEYQQiQAWd9y54F4XX" "signature" "my message"

As a JSON-RPC call
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "signmessage", "params": ["1D1ZrZNe3JUo7ZycKEYQQiQAWd9y54F4XX", "my message"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### signrawtransactionwithwallet

```
signrawtransactionwithwallet "hexstring" ( [{"txid":"hex","vout":n,"scriptPubKey":"hex","redeemScript":"hex","witnessScript":"hex","amount":amount},...] "sighashtype" )

Sign inputs for raw transaction (serialized, hex-encoded).
The second optional argument (may be null) is an array of previous transaction outputs that
this transaction depends on but may not yet be in the block chain.
Requires wallet passphrase to be set with walletpassphrase call if wallet is encrypted.

Arguments:
1. hexstring                        (string, required) The transaction hex string
2. prevtxs                          (json array, optional) The previous dependent transaction outputs
     [
       {                            (json object)
         "txid": "hex",             (string, required) The transaction id
         "vout": n,                 (numeric, required) The output number
         "scriptPubKey": "hex",     (string, required) The output script
         "redeemScript": "hex",     (string, optional) (required for P2SH) redeem script
         "witnessScript": "hex",    (string, optional) (required for P2WSH or P2SH-P2WSH) witness script
         "amount": amount,          (numeric or string, optional) (required for Segwit inputs) the amount spent
       },
       ...
     ]
3. sighashtype                      (string, optional, default="DEFAULT for Taproot, ALL otherwise") The signature hash type. Must be one of
                                    "DEFAULT"
                                    "ALL"
                                    "NONE"
                                    "SINGLE"
                                    "ALL|ANYONECANPAY"
                                    "NONE|ANYONECANPAY"
                                    "SINGLE|ANYONECANPAY"

Result:
{                             (json object)
  "hex" : "hex",              (string) The hex-encoded raw transaction with signature(s)
  "complete" : true|false,    (boolean) If the transaction has a complete set of signatures
  "errors" : [                (json array, optional) Script verification errors (if there are any)
    {                         (json object)
      "txid" : "hex",         (string) The hash of the referenced, previous transaction
      "vout" : n,             (numeric) The index of the output to spent and used as input
      "witness" : [           (json array)
        "hex",                (string)
        ...
      ],
      "scriptSig" : "hex",    (string) The hex-encoded signature script
      "sequence" : n,         (numeric) Script sequence number
      "error" : "str"         (string) Verification or signing error related to the input
    },
    ...
  ]
}

Examples:
> bitcoin-cli signrawtransactionwithwallet "myhex"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "signrawtransactionwithwallet", "params": ["myhex"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### simulaterawtransaction

```
simulaterawtransaction ["rawtx",...] ( {"include_watchonly":bool,...} )

Calculate the balance change resulting in the signing and broadcasting of the given transaction(s).

Arguments:
1. rawtxs          (json array, required) An array of hex strings of raw transactions.
                   
     [
       "rawtx",    (string)
       ...
     ]
2. options         (json object, optional) Options object that can be used to pass named arguments, listed below.

Named Arguments:
include_watchonly    (boolean, optional, default=false) (DEPRECATED) No longer used

Result:
{                          (json object)
  "balance_change" : n     (numeric) The wallet balance change (negative means decrease).
}

Examples:
> bitcoin-cli simulaterawtransaction ["myhex"]
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "simulaterawtransaction", "params": [["myhex"]]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### unloadwallet

```
unloadwallet ( "wallet_name" load_on_startup )

Unloads the wallet referenced by the request endpoint or the wallet_name argument.
If both are specified, they must be identical.

Arguments:
1. wallet_name        (string, optional, default=the wallet name from the RPC endpoint) The name of the wallet to unload. If provided both here and in the RPC endpoint, the two must be identical.
2. load_on_startup    (boolean, optional) Save wallet name to persistent settings and load on startup. True to add wallet to startup list, false to remove, null to leave unchanged.

Result:
{                   (json object)
  "warnings" : [    (json array, optional) Warning messages, if any, related to unloading the wallet.
    "str",          (string)
    ...
  ]
}

Examples:
> bitcoin-cli unloadwallet wallet_name
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "unloadwallet", "params": ["wallet_name"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### walletcreatefundedpsbt

```
walletcreatefundedpsbt ( [{"txid":"hex","vout":n,"sequence":n,"weight":n},...] ) [{"address":amount,...},{"data":"hex"},...] ( locktime options bip32derivs version psbt_version )

Creates and funds a transaction in the Partially Signed Transaction format.
Implements the Creator and Updater roles.
All existing inputs must either have their previous output transaction be in the wallet
or be in the UTXO set. Solving data must be provided for non-wallet inputs.

Arguments:
1. inputs                      (json array, optional) Leave empty to add inputs automatically. See add_inputs option.
     [
       {                       (json object)
         "txid": "hex",        (string, required) The transaction id
         "vout": n,            (numeric, required) The output number
         "sequence": n,        (numeric, optional, default=depends on the value of the 'locktime' and 'options.replaceable' arguments) The sequence number
         "weight": n,          (numeric, optional, default=Calculated from wallet and solving data) The maximum weight for this input, including the weight of the outpoint and sequence number. Note that signature sizes are not guaranteed to be consistent, so the maximum DER signatures size of 73 bytes should be used when considering ECDSA signatures.Remember to convert serialized sizes to weight units when necessary.
       },
       ...
     ]
2. outputs                     (json array, required) The outputs specified as key-value pairs.
                               Each key may only appear once, i.e. there can only be one 'data' output, and no address may be duplicated.
                               At least one output of either type must be specified.
                               For compatibility reasons, a dictionary, which holds the key-value pairs directly, is also
                               accepted as second parameter.
     [
       {                       (json object)
         "address": amount,    (numeric or string, required) A key-value pair. The key (string) is the bitcoin address,
                               the value (float or string) is the amount in BTC
         ...
       },
       {                       (json object)
         "data": "hex",        (string, required) A key-value pair. The key must be "data", the value is hex-encoded data that becomes a part of an OP_RETURN output
       },
       ...
     ]
3. locktime                    (numeric, optional, default=0) Raw locktime. Non-0 value also locktime-activates inputs
4. options                     (json object, optional) Options object that can be used to pass named arguments, listed below.
5. bip32derivs                 (boolean, optional, default=true) Include BIP 32 derivation paths for public keys if we know them
6. version                     (numeric, optional, default=2) Transaction version
7. psbt_version                (numeric, optional, default=2) The PSBT version number to use.

Named Arguments:
add_inputs                 (boolean, optional, default=false when "inputs" are specified, true otherwise) Automatically include coins from the wallet to cover the target amount.
                           
include_unsafe             (boolean, optional, default=false) Include inputs that are not safe to spend (unconfirmed transactions from outside keys and unconfirmed replacement transactions).
                           Warning: the resulting transaction may become invalid if one of the unsafe inputs disappears.
                           If that happens, you will need to fund the transaction with different inputs and republish it.
minconf                    (numeric, optional, default=0) If add_inputs is specified, require inputs with at least this many confirmations.
maxconf                    (numeric, optional) If add_inputs is specified, require inputs with at most this many confirmations.
changeAddress              (string, optional, default=automatic) The bitcoin address to receive the change
changePosition             (numeric, optional, default=random) The index of the change output
change_type                (string, optional, default=set by -changetype) The output type to use. Only valid if changeAddress is not specified. Options are "legacy", "p2sh-segwit", "bech32", "bech32m".
includeWatching            (boolean, optional, default=false) (DEPRECATED) No longer used
lockUnspents               (boolean, optional, default=false) Lock selected unspent outputs
fee_rate                   (numeric or string, optional, default=not set, fall back to wallet fee estimation) Specify a fee rate in sat/vB.
feeRate                    (numeric or string, optional, default=not set, fall back to wallet fee estimation) Specify a fee rate in BTC/kvB.
subtractFeeFromOutputs     (json array, optional, default=[]) The outputs to subtract the fee from.
                           The fee will be equally deducted from the amount of each specified output.
                           Those recipients will receive less bitcoins than you enter in their corresponding amount field.
                           If no outputs are specified here, the sender pays the fee.
     [
       vout_index,         (numeric) The zero-based output index, before a change output is added.
       ...
     ]
max_tx_weight              (numeric, optional, default=400000) The maximum acceptable transaction weight.
                           Transaction building will fail if this can not be satisfied.
conf_target                (numeric, optional, default=wallet -txconfirmtarget) Confirmation target in blocks
estimate_mode              (string, optional, default="unset") The fee estimate mode, must be one of (case insensitive):
                           unset, economical, conservative 
                           unset means no mode set (economical mode is used if the transaction is replaceable;
                           otherwise, conservative mode is used). 
                           economical mode potentially returns a lower fee rate estimate.
                           conservative potentially returns a higher fee rate estimate.
                           
replaceable                (boolean, optional, default=wallet default) Marks this transaction as BIP125-replaceable.
                           Allows this transaction to be replaced by a transaction with higher fees
solving_data               (json object, optional) Keys and scripts needed for producing a final transaction with a dummy signature.
                           Used for fee estimation during coin selection.
     {
       "pubkeys": [        (json array, optional, default=[]) Public keys involved in this transaction.
         "pubkey",         (string) A public key
         ...
       ],
       "scripts": [        (json array, optional, default=[]) Scripts involved in this transaction.
         "script",         (string) A script
         ...
       ],
       "descriptors": [    (json array, optional, default=[]) Descriptors that provide solving data for this transaction.
         "descriptor",     (string) A descriptor
         ...
       ],
     }

Result:
{                     (json object)
  "psbt" : "str",     (string) The resulting raw transaction (base64-encoded string)
  "fee" : n,          (numeric) Fee in BTC the resulting transaction pays
  "changepos" : n     (numeric) The position of the added change output, or -1
}

Examples:

Create a PSBT with automatically picked inputs that sends 0.5 BTC to an address and has a fee rate of 2 sat/vB:
> bitcoin-cli walletcreatefundedpsbt "[]" "[{\"bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl\":0.5}]" 0 "{\"add_inputs\":true,\"fee_rate\":2}"

Create the same PSBT as the above one instead using named arguments:
> bitcoin-cli -named walletcreatefundedpsbt outputs="[{\"bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl\":0.5}]" add_inputs=true fee_rate=2
```

### walletdisplayaddress

```
walletdisplayaddress "address"

Display address on an external signer for verification.

Arguments:
1. address    (string, required) bitcoin address to display

Result:
{                       (json object)
  "address" : "str"     (string) The address as confirmed by the signer
}
```

### walletlock

```
walletlock

Removes the wallet encryption key from memory, locking the wallet.
After calling this method, you will need to call walletpassphrase again
before being able to call any methods which require the wallet to be unlocked.

Result:
null    (json null)

Examples:

Set the passphrase for 2 minutes to perform a transaction
> bitcoin-cli walletpassphrase "my pass phrase" 120

Perform a send (requires passphrase set)
> bitcoin-cli sendtoaddress "bc1q09vm5lfy0j5reeulh4x5752q25uqqvz34hufdl" 1.0

Clear the passphrase since we are done before 2 minutes is up
> bitcoin-cli walletlock 

As a JSON-RPC call
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "walletlock", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### walletpassphrase

```
walletpassphrase "passphrase" timeout

Stores the wallet decryption key in memory for 'timeout' seconds.
This is needed prior to performing transactions related to private keys such as sending bitcoins

Note:
Issuing the walletpassphrase command while the wallet is already unlocked will set a new unlock
time that overrides the old one.

Arguments:
1. passphrase    (string, required) The wallet passphrase
2. timeout       (numeric, required) The time to keep the decryption key in seconds; capped at 100000000 (~3 years).

Result:
null    (json null)

Examples:

Unlock the wallet for 60 seconds
> bitcoin-cli walletpassphrase "my pass phrase" 60

Lock the wallet again (before 60 seconds)
> bitcoin-cli walletlock 

As a JSON-RPC call
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "walletpassphrase", "params": ["my pass phrase", 60]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### walletpassphrasechange

```
walletpassphrasechange "oldpassphrase" "newpassphrase"

Changes the wallet passphrase from 'oldpassphrase' to 'newpassphrase'.

Arguments:
1. oldpassphrase    (string, required) The current passphrase
2. newpassphrase    (string, required) The new passphrase

Result:
null    (json null)

Examples:
> bitcoin-cli walletpassphrasechange "old one" "new one"
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "walletpassphrasechange", "params": ["old one", "new one"]}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

### walletprocesspsbt

```
walletprocesspsbt "psbt" ( sign "sighashtype" bip32derivs finalize )

Update a PSBT with input information from our wallet and then sign inputs
that we can sign for.
Requires wallet passphrase to be set with walletpassphrase call if wallet is encrypted.

Arguments:
1. psbt           (string, required) The transaction base64 string
2. sign           (boolean, optional, default=true) Also sign the transaction when updating (requires wallet to be unlocked)
3. sighashtype    (string, optional, default="DEFAULT for Taproot, ALL otherwise") The signature hash type to sign with if not specified by the PSBT. Must be one of
                  "DEFAULT"
                  "ALL"
                  "NONE"
                  "SINGLE"
                  "ALL|ANYONECANPAY"
                  "NONE|ANYONECANPAY"
                  "SINGLE|ANYONECANPAY"
4. bip32derivs    (boolean, optional, default=true) Include BIP 32 derivation paths for public keys if we know them
5. finalize       (boolean, optional, default=true) Also finalize inputs if possible

Result:
{                             (json object)
  "psbt" : "str",             (string) The base64-encoded partially signed transaction
  "complete" : true|false,    (boolean) If the transaction has a complete set of signatures
  "hex" : "hex"               (string, optional) The hex-encoded network transaction if complete
}

Examples:
> bitcoin-cli walletprocesspsbt "psbt"
```


## Zmq

### getzmqnotifications

```
getzmqnotifications

Returns information about the active ZeroMQ notifications.

Result:
[                         (json array)
  {                       (json object)
    "type" : "str",       (string) Type of notification
    "address" : "str",    (string) Address of the publisher
    "hwm" : n             (numeric) Outbound message high water mark
  },
  ...
]

Examples:
> bitcoin-cli getzmqnotifications 
> curl --user myusername --data-binary '{"jsonrpc": "2.0", "id": "curltest", "method": "getzmqnotifications", "params": []}' -H 'content-type: application/json' http://127.0.0.1:8332/
```

