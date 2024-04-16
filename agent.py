import numpy as np

rng = np.random.default_rng(42)
ACTIONS = [-1,0,1]

class Agent():
    def __init__(self, paddle_y_max: int, ball_row_max: int, ball_column_max: int, action_size: int) -> None:
        self.paddle_y_max = paddle_y_max
        self.ball_row_max = ball_row_max
        self.ball_column_max = ball_column_max
        self.ball_dir_x_max = 3
        self.ball_dir_y_max = 2
        self.action_size = action_size
        self.gamma = 0.75
        self.learning_rate = 0.5
        self.epsilon = 0.3
        self.q_table = np.zeros((self.paddle_y_max + 2, self.ball_row_max + 1, self.ball_column_max + 1, self.ball_dir_x_max + 1, self.ball_dir_y_max + 1, self.action_size))

    
    def initialize_q_table(self):
        self.q_table = np.zeros((self.paddle_y_max + 2, self.ball_row_max + 1, self.ball_column_max + 1, self.ball_dir_x_max + 1, self.ball_dir_y_max + 1, self.action_size))

    def update_q_table(self, state, action, reward, newstate):
        delta = (
            reward
            + self.gamma * np.max(self.q_table[newstate, :])
            - self.q_table[state , action]
        )
        self.q_table[state, action] = self.q_table[state, action] + self.learning_rate * delta
    
    def choose_action(self, state, q_table) -> int:
        """
        Choose an action based on the epsilon-greedy algorithm.

        Args:
            state (ndarray): The current state of the game.
            q_table (ndarray): The Q-table containing the action-value estimates.

        Returns:
            int: The chosen action.
        """
        exploration_rate = rng.uniform(0, 1)

        if exploration_rate < self.epsilon:
            action = rng.choice(ACTIONS)
        else:
            action = np.argmax(q_table[state])

        return action
