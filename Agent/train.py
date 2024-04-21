from chainENV import ENV
from agent1 import Agent
import numpy as np
from utils import plot_learning_curve
import math
from web3 import Web3
from configparser import ConfigParser


# REWARDS
profitThreshold=100
lpTerminalReward=200
wpTerminalReward=-500
ngTerminalReward=-300
stepLimit=10


# MODEL PARAMS
epsilon=0.99
num_episodes=10
gamma=0.99
alpha=0.001
beta=0.002
fc1_dim=128
fc2_dim=256
memory_size=50
batch_size=50
tau=1
update_period=40
warmup=10
name="model1"

env=ENV(profitThreshold,lpTerminalReward,wpTerminalReward,ngTerminalReward,stepLimit)

config = ConfigParser()
config.read("config.ini")
recipient=config['Account-testnet']['address']
privateKey=config['Account-testnet']['key']
arbAddr=config['TESTNET']['arbaddress']
arbABI=config['TESTNET']['abi']

# ADD TESTNET CHAIN RPC URL HERE

w3 = Web3(Web3.HTTPProvider("testnet-chain RPC-url where model params to be stored"))
arbContract=w3.eth.contract(address=arbAddr,abi=arbABI)

# Functions where Arbitrum Sepolia X Morph X OP Avail Sepolia Testnet are called.

def store_var():
        arbContract = w3.eth.contract(address=arbAddr, abi=arbABI)
        store_var= arbContract.functions.storeInitialVariablesPart1(name,str(epsilon),num_episodes,str(gamma),str(alpha),str(beta),fc1_dim,fc2_dim,memory_size,batch_size).build_transaction({
            "from": recipient,
            "nonce": w3.eth.get_transaction_count(recipient)
        })
        signed_tx = w3.eth.account.sign_transaction(store_var, private_key=privateKey)
        w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        store_var= arbContract.functions.storeInitialVariablesPart2(name,tau,update_period,warmup).build_transaction({
            "from": recipient,
            "nonce": w3.eth.get_transaction_count(recipient)
        })
        signed_tx = w3.eth.account.sign_transaction(store_var, private_key=privateKey)
        w3.eth.send_raw_transaction(signed_tx.rawTransaction)


def store_perf(name,episode_lengths,profit_eachEpisode):
    arbContract = w3.eth.contract(address=arbAddr, abi=arbABI)
    store_var = arbContract.functions.storeModelPerformance(name,episode_lengths,profit_eachEpisode).build_transaction({
        "from": recipient,
        "nonce": w3.eth.get_transaction_count(recipient)
    })
    signed_tx = w3.eth.account.sign_transaction(store_var, private_key=privateKey)
    w3.eth.send_raw_transaction(signed_tx.rawTransaction)


def train(env,agent,epsilon,num_episodes):

    store_var()
    pools_dim=env.pools_dim
    episode_lengths=[]
    profit_eachEpisode=[]
    for i in range(0,num_episodes):
        print()
        print(f"#########  Episode No-{i}")
        state=env.reset()
        # print(f"Initial State--{state}")
        step_size=0
        while True:
            actions = agent.choose_action(state)
            r = np.random.rand()
            # print(r)
            if r < epsilon:
                print("Exploration")
                next_action = np.random.choice(np.arange(pools_dim))
            else:
                print("Greedy")
                next_action = np.argmax(actions[0][:pools_dim])
            gas=actions[0][agent.action_dims - 1]
            if math.isnan(gas):
                gas=-1
            action = [next_action, int(gas)]
            print(f"ActionPerformed--- {action}")
            _state,reward,done=env.step(action)
            agent.store_transition(state,actions,reward,_state,done)
            agent.learn()
            if(done):
                profit_eachEpisode.append(env.profit)
                break

            step_size+=1
        episode_lengths.append(step_size)
        if(i%50==0):
            epsilon = epsilon-0.03



    return episode_lengths,profit_eachEpisode


state_dims=env.state_dim
action_dims=env.pools_dim+1

agent=Agent(epsilon, gamma, alpha, beta, state_dims, action_dims, fc1_dim, fc2_dim,
                 memory_size, batch_size, tau, update_period, warmup, name)

episode_lengths,profit_eachEpisode = train(env, agent, epsilon, num_episodes)

# Storing Model performance in contract
store_perf(name,episode_lengths,profit_eachEpisode)

plot_learning_curve(episode_lengths,profit_eachEpisode,"LearningPlot1",False)



