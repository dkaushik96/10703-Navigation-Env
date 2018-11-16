"""Collection of NEL environments for OpenAI gym."""

from __future__ import absolute_import, division, print_function

try:
  from gym.envs.registration import register
  modules_loaded = True
except:
  modules_loaded = False

from .agent import Agent
from .direction import RelativeDirection
from .item import *
from .simulator import *
from .visualizer import MapVisualizer

def make_config():
  # specify the item types
  items = []
  items.append(Item("diamond",    [0.0, 1.0, 0.0], [0.0, 1.0, 0.0], [0, 1, 0, 0], [0, 1, 0, 0], False,
            intensity_fn=IntensityFunction.CONSTANT, intensity_fn_args=[-5.3],
            interaction_fns=[
              [InteractionFunction.PIECEWISE_BOX, 10.0, 200.0, 0.0, -6.0],      # parameters for interaction between item 0 and item 0
              [InteractionFunction.PIECEWISE_BOX, 200.0, 0.0, -6.0, -6.0],      # parameters for interaction between item 0 and item 1
              [InteractionFunction.PIECEWISE_BOX, 10.0, 200.0, 2.0, -100.0],    # parameters for interaction between item 0 and item 2
              [InteractionFunction.ZERO]                                        # parameters for interaction between item 0 and item 3
            ]))
  items.append(Item("tongs",     [1.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0, 0, 0, 0], [0, 0, 0, 0], False,
            intensity_fn=IntensityFunction.CONSTANT, intensity_fn_args=[-5.0],
            interaction_fns=[
              [InteractionFunction.PIECEWISE_BOX, 200.0, 0.0, -6.0, -6.0],      # parameters for interaction between item 1 and item 0
              [InteractionFunction.ZERO],                                       # parameters for interaction between item 1 and item 1
              [InteractionFunction.PIECEWISE_BOX, 200.0, 0.0, -100.0, -100.0],  # parameters for interaction between item 1 and item 2
              [InteractionFunction.ZERO]                                        # parameters for interaction between item 1 and item 3
            ]))
  items.append(Item("jellybean", [0.0, 0.0, 1.0], [0.0, 0.0, 1.0], [0, 0, 0, 0], [0, 0, 0, 0], False,
            intensity_fn=IntensityFunction.CONSTANT, intensity_fn_args=[-5.3],
            interaction_fns=[
              [InteractionFunction.PIECEWISE_BOX, 10.0, 200.0, 2.0, -100.0],    # parameters for interaction between item 2 and item 0
              [InteractionFunction.PIECEWISE_BOX, 200.0, 0.0, -100.0, -100.0],  # parameters for interaction between item 2 and item 1
              [InteractionFunction.PIECEWISE_BOX, 10.0, 200.0, 0.0, -6.0],      # parameters for interaction between item 2 and item 2
              [InteractionFunction.ZERO]                                        # parameters for interaction between item 2 and item 3
            ]))
  items.append(Item("wall",      [0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [0, 0, 0, 1], [0, 0, 0, 0], True,
            intensity_fn=IntensityFunction.CONSTANT, intensity_fn_args=[0.0],
            interaction_fns=[
              [InteractionFunction.ZERO],                                       # parameters for interaction between item 3 and item 0
              [InteractionFunction.ZERO],                                       # parameters for interaction between item 3 and item 1
              [InteractionFunction.ZERO],                                       # parameters for interaction between item 3 and item 2
              [InteractionFunction.CROSS, 10.0, 15.0, 20.0, -200.0, -20.0, 1.0] # parameters for interaction between item 3 and item 3
            ]))
  # construct the simulator configuration
  return SimulatorConfig(max_steps_per_movement=1, vision_range=5, gt_vision_range=10,
    allowed_movement_directions=[RelativeDirection.FORWARD],
    allowed_turn_directions=[RelativeDirection.LEFT, RelativeDirection.RIGHT],
    patch_size=32, gibbs_num_iter=10, items=items, agent_color=[0.0, 0.0, 1.0],
    collision_policy=MovementConflictPolicy.FIRST_COME_FIRST_SERVED,
    decay_param=0.4, diffusion_param=0.14, deleted_item_lifetime=2000)

if modules_loaded:
  # Construct the simulator configuration.
  sim_config = make_config()

  # Create a reward function.
  def reward_fn(prev_items, items):
      collected_items = items - prev_items
      n_diamonds = collected_items[0]
      n_jellybeans = collected_items[2]
      return 20 * n_jellybeans + 100 * n_diamonds

  register(
      id='NEL-v0',
      entry_point='nel.environment:NELEnv',
      kwargs={
        'sim_config': sim_config,
        'reward_fn': reward_fn,
        'render': False})

  register(
      id='NEL-render-v0',
      entry_point='nel.environment:NELEnv',
      kwargs={
        'sim_config': sim_config,
        'reward_fn': reward_fn,
        'render': True})
