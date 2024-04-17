from web3 import Web3
from configparser import ConfigParser
import random
import numpy as np
import requests
import apikey
from math import comb


config = ConfigParser()
config.read("config.ini")


# Market Prices of Tokens
headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': apikey.apiKey,
}
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'


routerAddr=config['UNISWAP']['address']
routerABI=config['UNISWAP']['abi']
wethAddr=config['WETH9']['address']
wethABI=config['WETH9']['abi']
factoryAddr=config['FACTORY']['address']
factoryABI=config['FACTORY']['abi']
reservesAddr=config['RESERVES']['address']
reservesABI=config['RESERVES']['abi']
recipient=config['Account']['address']
privateKey=config['Account']['key']


w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
swapContract=w3.eth.contract(address=routerAddr,abi=routerABI)
factory=w3.eth.contract(address=factoryAddr,abi=factoryABI)







class ENV:
    def __init__(self,profitThreshold,lpTerminalReward,wpTerminalReward,ngTerminalReward,stepLimit):
        self.pools_dim=self.getNoOfPools()
        self.array,self.count,self.decimals=self.getToken()
        self.action_dim=2
        self.state_dim=self.getStateDim()
        self.state_space=np.zeros(self.state_dim)
        self.action_space=np.zeros(self.action_dim)
        self.pool_addr=self.getPoolAddr()
        self.agentTokens=np.zeros(self.count)
        self.marketPrice=self.getMarketPrice()
        self.profitThreshold=profitThreshold
        self.lpTerminalReward=lpTerminalReward
        self.wpTerminalReward=wpTerminalReward
        self.ngTerminalReward=ngTerminalReward
        self.iGasLimit=int(random.uniform(140000,150000))
        self.maGas=self.estimateGas()
        self.predictedGas=self.maGas
        self.noOfsteps=0
        self.stepLimit=stepLimit
        self.profit=0
        self.noOfEpisodes=0
        self.initialAmount=0


    def calculateProfit(self):
        tokenIndex=self.getTokenSwapIndex()
        maGas=w3.to_wei(self.maGas,'ether')
        return self.initialAmount-self.state_space[tokenIndex]-(maGas*self.marketPrice[0])/(10**18)


    def step(self,actions):
        self.noOfsteps+=1
        poolIndex=actions[0]
        gasPredicted=actions[1]
        if(gasPredicted==-1):
            print("#########   Terminal Result--Infinite Gas")
            self.profit=self.ngTerminalReward
            return self.state_space,self.ngTerminalReward,True

        token0,token1,done,token1Index=self.getTokenID(poolIndex)

        if(done):
             print(f"#########   Terminal Result--  Wrong Pool {self.noOfsteps}")
             self.profit=self.wpTerminalReward
             return self.state_space,self.wpTerminalReward+self.noOfsteps*100,True


        token0Index=self.getTokenSwapIndex()
        print(self.state_space[:self.count])
        amountIn=self.state_space[token0Index]*(10**int(self.decimals[token0Index]))/self.marketPrice[token1Index]
        gasUsed=self.swap(token0,token1,int(amountIn),3000)
        gasUsed=w3.from_wei(gasUsed,'ether')
        self.maGas=self.maGas+int(1/self.noOfsteps)*(gasUsed-self.maGas)
        self.predictedGas=self.predictedGas+int(1/self.noOfsteps)*(gasPredicted-self.predictedGas)
        token1Amount = w3.eth.contract(address=token1, abi=wethABI).caller().balanceOf(recipient)
        token1Amount=token1Amount/(10**int(self.decimals[token1Index]))


        if(self.predictedGas<self.maGas):
            print("#########   Terminal Result--Not enough gas")
            self.profit=self.ngTerminalReward
            return self.state_space,self.ngTerminalReward+self.noOfsteps*100,True
        self.updateStateSpace(token1Amount,token1Index)
        profit=self.calculateProfit()
        self.profit=profit


        if(profit<self.profitThreshold or self.noOfsteps>=self.stepLimit):
            print("#########   Terminal Result--  Low Profit")
            return self.state_space,self.lpTerminalReward,True
        else:
            print(f"#########   Terminal State -- PROFIT {profit}")
            return self.state_space,profit,False


    def updateStateSpace(self,token1Amount,token1Index):
        reserves=self.reserves()
        state_space=self.state_space
        state_space[self.getTokenSwapIndex()]=0
        state_space[token1Index]=token1Amount*self.marketPrice[token1Index]
        c=0
        b=self.count+self.pools_dim*2
        for i in range(self.count,b):
            state_space[i]=reserves[c]
            c+=1
        state_space[self.state_dim-2]=self.maGas
        self.state_space=state_space


    def reset(self):
        self.noOfsteps=0
        self.noOfEpisodes+=1
        if(self.noOfEpisodes%50==0):
            self.marketPrice = self.getMarketPrice()

        state_space=np.zeros(self.state_dim)
        reserves=self.reserves()
        state_space[0]=self.get_weth()*self.marketPrice[0]
        self.initialAmount=state_space[0]
        c=0
        b=self.count+self.pools_dim*2
        market=self.marketPrice
        for i in range(self.count,b):
            state_space[i]=reserves[c]
            c+=1
        c=0
        for i in range(b,self.state_dim-2):
            state_space[i]=market[c]
            c+=1
        self.iGasLimit=int(random.uniform(140000,150000))

        state_space[self.state_dim-2]=self.estimateGas()
        state_space[self.state_dim-1]=self.initialAmount

        self.state_space=state_space
        return state_space


    def get_weth(self,a=0.01, b=0.02):
        value = random.uniform(a, b)
        wethContract = w3.eth.contract(address=wethAddr, abi=wethABI)
        get_weth = wethContract.functions.deposit().build_transaction({
            "from": recipient,
            "nonce": w3.eth.get_transaction_count(recipient),
            "value": w3.to_wei(value, 'ether')
        })
        signed_tx = w3.eth.account.sign_transaction(get_weth, private_key=privateKey)
        w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return  value


    def getMarketPrice(self):
        symbol = []
        for i in config['TOKENS']:
            symbol.append(i.upper())
        symbols_formatted = ','.join(symbol)
        parameters = {
            'symbol': symbols_formatted,
            'convert': 'USD'
        }
        json = requests.get(url, headers=headers, params=parameters).json()
        json = json['data']
        c = 0
        array = []
        for i in json:
            array.append(json[symbol[c]]['quote']['USD']['price'])
        return array


    def getNoOfPools(self):
        k = (config['TOKENS'].keys())
        count = 0
        for i in k:
            count += 1
        return comb(count, 2)


    def getStateDim(self):
       p = self.pools_dim*2
       return self.count*2 + p + 2


    def getToken(self):
        array = []
        array1=[]
        k = (config['TOKENS'].keys())
        c = config['TOKENS']
        count = 0
        for i in k:
            array.append(c[i][2:])
            array1.append(c[i][:2])
            count += 1
        return array, count,array1


    def getReserves(self,token0, token1,poolAddr):

        token0 = w3.eth.contract(address=token0, abi=wethABI).caller().balanceOf(poolAddr)
        token1 = w3.eth.contract(address=token1, abi=wethABI).caller().balanceOf(poolAddr)
        return token0, token1


    def reserves(self):
        count=self.count
        array=self.array
        array1=[]
        c=0
        for i in range(0, count):
            for j in range(i + 1, count):
                token0,token1=self.getReserves(array[i], array[j],self.pool_addr[c])
                c+=1
                array1.append(token0*self.marketPrice[i]*(10**(-int(self.decimals[i]))))
                array1.append(token1*self.marketPrice[j]*(10**(-int(self.decimals[j]))))
        return array1


    def getPoolAddr(self):
        array = self.array
        array1=[]
        for i in range(0, self.count):
            for j in range(i + 1, self.count):
                poolAddr = factory.caller().getPool(array[i], array[j], 3000)
                array1.append(poolAddr)
        return array1
   
   
    def swap(self, token0, token1, amountIn, fee=3000):
        tx = w3.eth.contract(address=token0, abi=wethABI).functions.approve(routerAddr, amountIn).build_transaction({
            "from": recipient,
            "nonce": w3.eth.get_transaction_count(recipient)
        })
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=privateKey)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        deadline=int(w3.eth.get_block('latest').timestamp)+60*20
        swapTx = swapContract.functions.exactInputSingle(
            (token0, token1, fee, recipient,deadline, amountIn, 0, 0)).build_transaction({
            "from": recipient,
            "nonce": w3.eth.get_transaction_count(recipient)
        })
        signed_tx = w3.eth.account.sign_transaction(swapTx, private_key=privateKey)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt.gasUsed


    def getTokenID(self,poolIndex):
        tokenIndex=self.getTokenSwapIndex()
        # print("tokenIndex---",tokenIndex)
        p=0
        for i in range(0,tokenIndex):
            p+=self.count-i-1
        # print("p value--" ,p)
        if(poolIndex<p+self.count-1-tokenIndex and poolIndex>=p):
            token0 = self.array[tokenIndex]
            token1Index = tokenIndex + poolIndex - p + 1
            token1 = self.array[token1Index]
            return token0, token1, False, token1Index
        return "", "", True, 0


    def getTokenSwapIndex(self):
        tokenIndex=np.argmax(self.state_space[:self.count])
        return tokenIndex


    def estimateGas(self):
        gasPrice=w3.from_wei(w3.eth.gas_price,'ether')
        return (gasPrice*self.iGasLimit)




