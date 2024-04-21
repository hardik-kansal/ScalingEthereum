
# Reinforcemnt Learning Based Cross--DEX Arbitrage Agent


### Prerequisites

- Make sure you have `anaconda` installed for managing Python packages and `PyCharm` as IDE.
 
- Model is under development and has not yet trained.

 
### Overview  


- I have used **Twin Delayed Deep Deterministic Policy Gradient** (TD3 DDPG) with **PyTorch**
  
- Updating Arbitrage Bot is pain in the ass. This project is a proof-of-concept that favours arbitrage opportunities in ethereum network. Rl can easily be extended to cross-dex once model is trained.
- I have used **UniswapV3** as example.
 



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
