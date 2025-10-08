
# Reinforcemnt Learning Based Cross--DEX Arbitrage Agent



### ReturnX __ Arbitrum Sepolia X Morph Testnet X Avail

- During starting and ending of each training phase ,all hyperparameters and training result is stored on-chain contract.

- Arbitrum Sepolia deployed contract "https://sepolia.arbiscan.io/address/0xae6713ee724a68f2954E4996F08aeF60d15eC91e"
  
- Morph testnet deployed contract "https://explorer-testnet.morphl2.io/address/0x14D80eb8a71A7e0FB9357D905D558b752280960A"

- Op-Avail Sepolia Testnet deployed address "0xa326DF8e4132980E69d60199FF79872FCA0C2F5F"

- Op-Avail Sepolia Blockscout verified contract "https://op-avail-sepolia-explorer.alt.technology/address/0xa326DF8e4132980E69d60199FF79872FCA0C2F5F?tab=contract"




### Prerequisites

- Make sure you have `anaconda` installed for managing Python packages and `PyCharm` as IDE.
 
- Model is under development and has not yet trained.

 
### Overview  


- I have used **Twin Delayed Deep Deterministic Policy Gradient** (TD3 DDPG) with **PyTorch**
  
- Updating Arbitrage Bot is pain. This project is a proof-of-concept that favours arbitrage opportunities in among the dexes.
- I have used **Web3.py** and **UniswapV3** for demonstration.
 



## Installation

- Run these commands on Terminal

```bash
git clone git@github.com:hardik-kansal/RL-Arbitrage-Cross-DEX.git
cd RL-Arbitrage-Cross-DEX
cd chainENV 
yarn install
```

- Get `COINMARKETCAP API-KEY` from `https://coinmarketcap.com/api/`  
  
- Get `ALCHEMY API-KEY` from `https://www.alchemy.com/`


- Run the following command to start hardhat mainnet fork locally.
  
```bash
 yarn hardhat node --fork https://eth-mainnet.g.alchemy.com/v2/[ALCHEMY API-KEY]
```



- Copy any account and private-Key and paste under `ACCOUNT` in `Agent/config.ini`

- You can add any no of tokens (currently from **UniswapV3** only) in the format `ETH=[decimal][chain-address]`

- Get `Morph` or `Arbitrum Sepolia` testnet API-key and copy it to `train.py` .





## Training

- Go to `train.py` and change following hyperparamters

##### Agent

```
epsilon=0.99  
num_episodes=10000
gamma=0.99
alpha=0.001
beta=0.002
fc1_dim=256
fc2_dim=256
memory_size=50
batch_size=50
tau=1
update_period=40
warmup=10
name="model1"
```



##### Reward

```
profitThreshold=100  | **min profit**
lpTerminalReward=200 | **low or negative profit**
wpTerminalReward=-1000 | **no token exist in pool**
ngTerminalReward=-100 | **less gas used**
stepLimit=10 | **no of steps or swap in a episode **
```

- To start training, run `train.py`




## Reward 

- To change reward for the agent go to `Agent/chainENV.py` and change `step` function

  
#### Constraints
- Infinite-gas
- Moving Average Gas predicted > Moving Average gas Used
- Max step or No of swaps in a single tx - 10
- Profit > profitThreshold
- state-space :  [TokenHoldings of Agent (USD),Pool reserves,Market price,InitialAmount (fixed each episode),gasUsed]
- action-space : [PoolIndex,Gaspredicted]
