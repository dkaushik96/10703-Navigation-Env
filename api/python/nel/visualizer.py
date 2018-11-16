from __future__ import absolute_import, division, print_function

from math import ceil, floor, pi
from .direction import Direction

try:
	import numpy as np
	import matplotlib
	import matplotlib.pyplot as plt
	from matplotlib.collections import LineCollection, PatchCollection
	from matplotlib.patches import Circle, Rectangle, RegularPolygon
	modules_loaded = True
except ImportError:
	modules_loaded = False

__all__ = ['MapVisualizerError', 'MapVisualizer']

AGENT_RADIUS = 0.5
ITEM_RADIUS = 0.4
MAXIMUM_SCENT = 0.9

_FIGURE_COUNTER = 1

class MapVisualizerError(Exception):
  pass

def agent_position(direction):
	if direction == Direction.UP:
		return (0, -0.1), 0
	elif direction == Direction.DOWN:
		return (0, 0.1), pi
	elif direction == Direction.LEFT:
		return (0.1, 0), pi/2
	elif direction == Direction.RIGHT:
		return (-0.1, 0), 3*pi/2

class MapVisualizer(object):
	def __init__(self, sim, sim_config, bottom_left, top_right, show_agent_perspective=True):
		global _FIGURE_COUNTER
		if not modules_loaded:
			raise ImportError("numpy and matplotlib are required to use MapVisualizer.")
		plt.ion()
		self._sim = sim
		self._config = sim_config
		self._xlim = [bottom_left[0], top_right[0]]
		self._ylim = [bottom_left[1], top_right[1]]
		self._fignum = 'MapVisualizer Figure ' + str(_FIGURE_COUNTER)
		_FIGURE_COUNTER += 1
		if show_agent_perspective:
			self._fig, axes = plt.subplots(nrows=1, ncols=2, num=self._fignum)
			self._ax = axes[0]
			self._ax_agent = axes[1]
			self._fig.set_size_inches((18, 9))
		else:
			self._fig, self._ax = plt.subplots(num=self._fignum)
			self._ax_agent = None
			self._fig.set_size_inches((9, 9))
		self._fig.tight_layout()

	def __del__(self):
		plt.close(self._fig)

	def set_viewbox(self, bottom_left, top_right):
		self._xlim = [bottom_left[0], top_right[0]]
		self._ylim = [bottom_left[1], top_right[1]]

	def draw(self):
		if not plt.fignum_exists(self._fignum):
			raise MapVisualizerError('The figure is closed')
		map = self._sim._map((int(floor(self._xlim[0])), int(floor(self._ylim[0]))), (int(ceil(self._xlim[1])), int(ceil(self._ylim[1]))))
		n = self._config.patch_size
		self._ax.clear()
		self._ax.set_xlim(self._xlim)
		self._ax.set_ylim(self._ylim)
		for patch in map:
			(patch_position, fixed, scent, vision, gt_vision, items, agents) = patch
			color = (0, 0, 0, 0.3) if fixed else (0, 0, 0, 0.1)

			vertical_lines = np.empty((n + 1, 2, 2))
			vertical_lines[:,0,0] = patch_position[0]*n + np.arange(n + 1) - 0.5
			vertical_lines[:,0,1] = patch_position[1]*n - 0.5
			vertical_lines[:,1,0] = patch_position[0]*n + np.arange(n + 1) - 0.5
			vertical_lines[:,1,1] = patch_position[1]*n + n - 0.5
			vertical_line_col = LineCollection(vertical_lines, colors=color, linewidths=0.4, linestyle='solid')
			self._ax.add_collection(vertical_line_col)

			horizontal_lines = np.empty((n + 1, 2, 2))
			horizontal_lines[:,0,0] = patch_position[0]*n - 0.5
			horizontal_lines[:,0,1] = patch_position[1]*n + np.arange(n + 1) - 0.5
			horizontal_lines[:,1,0] = patch_position[0]*n + n - 0.5
			horizontal_lines[:,1,1] = patch_position[1]*n + np.arange(n + 1) - 0.5
			horizontal_line_col = LineCollection(horizontal_lines, colors=color, linewidths=0.4, linestyle='solid')
			self._ax.add_collection(horizontal_line_col)

			patches = []
			for agent in agents:
				(agent_pos, angle) = agent_position(Direction(agent[2]))
				patches.append(RegularPolygon((agent[0] + agent_pos[0], agent[1] + agent_pos[1]), 3,
						radius=AGENT_RADIUS, orientation=angle, facecolor=self._config.agent_color,
						edgecolor=(0,0,0), linestyle='solid', linewidth=0.4))
			for item in items:
				(type, position) = item
				if (self._config.items[type].blocks_movement):
					patches.append(Rectangle((position[0] - 0.5, position[1] - 0.5), 1.0, 1.0,
							facecolor=self._config.items[type].color, edgecolor=(0,0,0), linestyle='solid', linewidth = 0.4))
				else:
					patches.append(Circle(position, ITEM_RADIUS, facecolor=self._config.items[type].color,
							edgecolor=(0,0,0), linestyle='solid', linewidth=0.4))

			# convert 'scent' to a numpy array and transform into a subtractive color space (so zero is white)
			scent_img = np.clip(np.log(scent**0.4 + 1) / MAXIMUM_SCENT, 0.0, 1.0)
			scent_img = 1.0 - 0.5 * np.dot(scent_img, np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]]))
			self._ax.imshow(np.rot90(scent_img),
					extent=(patch_position[0]*n - 0.5, patch_position[0]*n + n - 0.5,
							patch_position[1]*n - 0.5, patch_position[1]*n + n - 0.5))

			self._ax.add_collection(PatchCollection(patches, match_original=True))

		# draw the agent's perspective
		if self._ax_agent != None and (0 in self._sim.agents):
			agent = self._sim.agents[0]
			R = self._config.vision_range
			self._ax_agent.clear()
			self._ax_agent.set_xlim([-R - 0.5, R + 0.5])
			self._ax_agent.set_ylim([-R - 0.5, R + 0.5])

			vertical_lines = np.empty((2*R, 2, 2))
			vertical_lines[:,0,0] = np.arange(2*R) - R + 0.5
			vertical_lines[:,0,1] = -R - 0.5
			vertical_lines[:,1,0] = np.arange(2*R) - R + 0.5
			vertical_lines[:,1,1] = R + 0.5
			vertical_line_col = LineCollection(vertical_lines, colors=(0, 0, 0, 0.3), linewidths=0.4, linestyle='solid')
			self._ax_agent.add_collection(vertical_line_col)

			horizontal_lines = np.empty((2*R, 2, 2))
			horizontal_lines[:,0,0] = -R - 0.5
			horizontal_lines[:,0,1] = np.arange(2*R) - R + 0.5
			horizontal_lines[:,1,0] = R + 0.5
			horizontal_lines[:,1,1] = np.arange(2*R) - R + 0.5
			horizontal_line_col = LineCollection(horizontal_lines, colors=(0, 0, 0, 0.3), linewidths=0.4, linestyle='solid')
			self._ax_agent.add_collection(horizontal_line_col)

			# convert 'vision' to a numpy array and transform into a subtractive color space (so zero is white)
			vision_img = agent.vision()
			vision_img = 1.0 - 0.5 * np.dot(vision_img, np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]]))
			self._ax_agent.imshow(np.rot90(vision_img),
					extent=(-R - 0.5, R + 0.5, -R - 0.5, R + 0.5))

			patches = []
			(agent_pos, angle) = agent_position(Direction.UP)
			patches.append(RegularPolygon(agent_pos, 3, radius=AGENT_RADIUS, orientation=angle,
					facecolor=self._config.agent_color, edgecolor=(0,0,0), linestyle='solid', linewidth=0.4))

			self._ax_agent.add_collection(PatchCollection(patches, match_original=True))

		self._pause(1.0e-16)
		plt.draw()
		self._xlim = self._ax.get_xlim()
		self._ylim = self._ax.get_ylim()

	def _pause(self, interval):
		backend = plt.rcParams['backend']
		if backend in matplotlib.rcsetup.interactive_bk:
			figManager = matplotlib._pylab_helpers.Gcf.get_active()
			if figManager is not None:
				canvas = figManager.canvas
				if canvas.figure.stale:
					canvas.draw()
				canvas.start_event_loop(interval)
				return
