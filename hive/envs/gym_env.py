import gym
import numpy as np
from hive.envs.base import BaseEnv
from hive.envs.env_spec import EnvSpec


class GymEnv(BaseEnv):
    """
    Class for loading gym environments.
    """

    def __init__(self, env_name, num_players=1, **kwargs):
        """
        Args:
            env_name (str): Name of the environment (NOTE: make sure it is available
                in gym.envs.registry.all())
            num_players (int): Number of players for the environment.
            kwargs: Any arguments you want to pass to :py:meth:`create_env` or
                :py:meth:`create_env_spec` can be passed as keyword arguments to this
                constructor.
        """
        self.create_env(env_name, **kwargs)
        super().__init__(self.create_env_spec(env_name, **kwargs), num_players)

    def create_env(self, env_name, **kwargs):
        """Function used to create the environment. Subclasses can override this method
        if they are using a gym style environment that needs special logic.

        Args:
            env_name (str): Name of the environment
        """
        env = gym.make(env_name)
        if kwargs.get("mujoco_wrapper", False):
            env = gym.wrappers.RecordEpisodeStatistics(env)
            env = gym.wrappers.ClipAction(env)
            env = gym.wrappers.NormalizeObservation(env)
            env = gym.wrappers.TransformObservation(
                env, lambda obs: np.clip(obs, -10, 10)
            )
            env = gym.wrappers.NormalizeReward(env)
            env = gym.wrappers.TransformReward(
                env, lambda reward: np.clip(reward, -10, 10)
            )

        elif kwargs.get("atari_wrapper", False):
            env = gym.wrappers.NoopResetEnv(env, noop_max=30)
            env = gym.wrappers.EpisodicLifeEnv(env)
            if "FIRE" in env.unwrapped.get_action_meanings():
                env = gym.wrappers.FireResetEnv(env)
        self._env = env

    def create_env_spec(self, env_name, **kwargs):
        """Function used to create the specification. Subclasses can override this method
        if they are using a gym style environment that needs special logic.

        Args:
            env_name (str): Name of the environment
        """
        if isinstance(self._env.observation_space, gym.spaces.Tuple):
            observation_spaces = self._env.observation_space.spaces
        else:
            observation_spaces = [self._env.observation_space]
        if isinstance(self._env.action_space, gym.spaces.Tuple):
            action_spaces = self._env.action_space.spaces
        else:
            action_spaces = [self._env.action_space]

        return EnvSpec(
            env_name=env_name,
            observation_space=observation_spaces,
            action_space=action_spaces,
        )

    def reset(self):
        observation = self._env.reset()
        return observation, self._turn

    def step(self, action):
        observation, reward, done, info = self._env.step(action)
        self._turn = (self._turn + 1) % self._num_players
        return observation, reward, done, self._turn, info

    def render(self, mode="rgb_array"):
        return self._env.render(mode=mode)

    def seed(self, seed=None):
        self._env.seed(seed=seed)

    def close(self):
        self._env.close()
