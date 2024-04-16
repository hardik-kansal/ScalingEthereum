import os
import torch as T
import torch.optim as optim
import torch.nn as nn
import torch.nn.functional as F


class Critic(nn.Module):
    def __init__(self, lr, state_dims, action_dims, fc1_dims=400, fc2_dims=300, name='Critic', ckpt_dir='tmp/'):
        super(Critic, self).__init__()
        self.lr = lr
        self.state_dims = state_dims
        self.action_dims = action_dims
        self.fc1_dims = fc1_dims
        self.fc2_dims = fc2_dims
        self.name = name
        self.ckpt_dir = ckpt_dir
        self.ckpt_path = os.path.join(self.ckpt_dir, self.name)

        # NN layers
        # 28,100
        self.fc1 = nn.Linear(self.state_dims + self.action_dims, self.fc1_dims)
        self.fc2 = nn.Linear(self.fc1_dims, self.fc2_dims)
        self.fc3 = nn.Linear(self.fc2_dims, 1)

        # Optimization objects
        self.optimizer = optim.Adam(self.parameters(), lr=self.lr)
        self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu')
        self.to(self.device)

    def forward(self, state, action):
        state_action = T.cat((state, action), dim=1).float()
        x = F.relu(self.fc1(state_action))
        x = F.relu(self.fc2(x))
        q = self.fc3(x)
        return q

    def save_checkpoint(self):
        print('... saving checkpoint ...')
        T.save(self.state_dict(), self.ckpt_path)

    def load_checkpoint(self, gpu_to_cpu=False):
        print('... loading checkpoint ...')
        if gpu_to_cpu:
            self.load_state_dict(T.load(self.ckpt_path, map_location=lambda storage, loc: storage))
        else:
            self.load_state_dict(T.load(self.ckpt_path))


class Actor(nn.Module):
    def __init__(self, lr, state_dims, action_dims, fc1_dims=400, fc2_dims=300, name='Actor', ckpt_dir='tmp/'):
        super(Actor, self).__init__()
        self.lr = lr
        self.state_dims = state_dims
        self.action_dims = action_dims
        self.fc1_dims = fc1_dims
        self.fc2_dims = fc2_dims
        self.name = name
        self.ckpt_dir = ckpt_dir
        self.ckpt_path = os.path.join(self.ckpt_dir, self.name)

        # NN layers
        self.fc1 = nn.Linear(self.state_dims, self.fc1_dims)
        self.fc2 = nn.Linear(self.fc1_dims, self.fc2_dims)
        self.a1=nn.Linear(self.fc2_dims,256)
        self.a2=nn.Linear(256,128)
        self.fc3 = nn.Linear(128, self.action_dims-1)
        self.fc4=nn.Linear(128,1)

        # Optimization objects
        self.optimizer = optim.Adam(self.parameters(), lr=self.lr)
        self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu')
        self.to(self.device)

    def forward(self, state):
        x = F.relu(self.fc1(state))
        y = F.relu(self.fc2(x))
        y=F.relu((self.a1(y)))
        y=F.relu(self.a2(y))
        x = F.relu(self.fc3(y))
        gasPredicted = F.relu(self.fc4(y))
        mu = F.softmax(x, dim=1)
        output = T.cat((mu, gasPredicted), dim=1)
        return output

    def save_checkpoint(self):
        print('... saving checkpoint ...')
        T.save(self.state_dict(), self.ckpt_path)

    def load_checkpoint(self, gpu_to_cpu=False):
        print('... loading checkpoint ...')
        if gpu_to_cpu:
            self.load_state_dict(T.load(self.ckpt_path, map_location=lambda storage, loc: storage))
        else:
            self.load_state_dict(T.load(self.ckpt_path))