## SNAKE - AI
### Reinforcement learning for the game of snake

#### Rewards:
* Eat food:     +10
* Game over:    -10
* Else:          0

#### Actions:
* [1, 0, 0] -> straight
* [0, 1, 0] -> right turn
* [0, 0, 1] -> left turn


#### Game state description

##### State (11 values):
```
[
## Danger position
danger straight, danger right, danger left,

## Snake direction
direction left, direction right,
direction up, direction down,

## Food position
food left, food right,
food up, food down
] 
```

#### Model
Feed forward neural network
* input features [11] (state)
* hidden layer
* output [3] action

#### Loss function
`Bellman equation`  
Simplified:
Q = model.predict(state_0)  
Q_new = Reward + y*max(Q(state_1))


`Mean squared error`  
loss = (Q_new - Q)^2
