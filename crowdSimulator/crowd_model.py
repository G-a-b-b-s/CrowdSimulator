import mesa
import json
from agent import *


class CrowdModel(mesa.Model):

    def __init__(self, config_file_path, scenario):
        super().__init__()

        with open(config_file_path, 'r') as f:
            params = json.load(f)

        self.params = params
        self.num_agents = params.get("num_agents", 10)
        self.num_destinations = params.get("num_objectives", 3)
        self.grid_width = params.get("grid_width", 20)
        self.grid_height = params.get("grid_height", 20)
        self.randomize_obstacles = params.get("randomize_obstacles", False)
        self.randomize_objectives = params.get("randomize_objectives", False)
        self.obstacles = []
        self.destinations = []
        self.scenario = scenario

        self.grid = mesa.space.SingleGrid(self.grid_width, self.grid_height, False)
        self.schedule = mesa.time.SimultaneousActivation(self)
        self.visited_counts = {}
        self.collision_count = {}
        self.collision_history = []
        self.intruders_history = {"intimate": [], "personal": [], "social": []}

        self.setup_obstacles()
        self.generate_unique_destinations()
        self.generate_agents()

    def load_obstacles(self, obstacle_data):
        obstacles = []
        for i, data in enumerate(obstacle_data):
            pos = tuple(data["position"])
            obstacle = Obstacle(i, self, pos)
            obstacles.append(obstacle)
        return obstacles

    def load_destinations(self, destination_data):
        destinations = []
        for i, data in enumerate(destination_data):
            pos = tuple(data["position"])
            preset = data["preset"]
            color = tuple(data["color"])
            destination = Destination(pos, preset, color)
            destinations.append(destination)
        return destinations

    def generate_agents(self):
        for i in range(self.num_agents):
            a = CrowdAgent(len(self.schedule.agents), self, self.scenario)
            self.schedule.add(a)

            while True:
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
                if self.grid.is_cell_empty((x, y)):
                    self.grid.place_agent(a, (x, y))
                    a.pos = x, y
                    break
        self.assign_destinations()

    def setup_obstacles(self):
        if self.randomize_obstacles:
            num_obstacles = len(self.obstacles) or 10
            for _ in range(num_obstacles):
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
                if self.grid.is_cell_empty((x, y)):
                    obstacle = Obstacle(len(self.agents), self, (x, y))
                    self.obstacles.append(obstacle)
        else:
            self.obstacles = self.load_obstacles(self.params.get("obstacles", []))

        self.generate_obstacles()

    def generate_obstacles(self):
        for obstacle in self.obstacles:
            x, y = obstacle.pos
            if self.grid.is_cell_empty((x, y)):
                self.grid.move_agent(obstacle, (x, y))

    def generate_unique_destinations(self):
        if self.randomize_objectives:
            for _ in range(self.num_destinations):
                dest_x = self.random.randrange(self.grid.width)
                dest_y = self.random.randrange(self.grid.height)
                destination = Destination((dest_x, dest_y), 'exit', (0, 0, 128))
                self.destinations.append(destination)
        else:
            self.destinations = self.load_destinations(self.params.get("objectives", []))

    def assign_destinations(self):
        for agent in self.schedule.agents:
            destination = self.random.choice(self.destinations)
            agent.destination = destination

    def spawn_agent(self):
        if len(self.schedule.agents) < self.num_agents + 10:
            destination = self.random.choice(self.destinations)

            new_agent_id = len(self.schedule.agents)
            new_agent = CrowdAgent(new_agent_id, self, self.scenario)
            self.schedule.add(new_agent)

            dest_x, dest_y = destination.pos

            offsets = [
                (-1, -1), (-1, 0), (-1, 1),
                (0, -1), (0, 1),
                (1, -1), (1, 0), (1, 1)
            ]

            self.random.shuffle(offsets)

            for offset in offsets:
                x = dest_x + offset[0]
                y = dest_y + offset[1]

                if (0 <= x < self.grid.width) and (0 <= y < self.grid.height):
                    if self.grid.is_cell_empty((x, y)):
                        self.grid.place_agent(new_agent, (x, y))
                        new_agent.pos = (x, y)
                        break

            new_agent.destination = self.random.choice(self.destinations)

    def count_intruders(self):
        zones = {
            "intimate": 2,
            "personal": 5,
            "social": 8
        }

        zone_counts = {zone: 0 for zone in zones}

        for agent in self.schedule.agents:
            for other_agent in self.schedule.agents:
                if agent != other_agent:
                    distance = ((agent.pos[0] - other_agent.pos[0]) ** 2 +
                                (agent.pos[1] - other_agent.pos[1]) ** 2) ** 0.5
                    for zone, radius in zones.items():
                        if distance <= radius:
                            zone_counts[zone] += 1
                            break

        for zone in zones:
            self.intruders_history[zone].append(zone_counts[zone])

    def step(self):
        self.schedule.step()

        total_collisions = sum(self.collision_count.values())
        self.collision_history.append(total_collisions)
