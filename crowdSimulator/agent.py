from mesa import Agent
import random
import math


class CrowdAgent(Agent):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

        self.steps = 0
        self.velocity = 1
        self.destination = Destination((0, 0), 'no', (0, 0, 0))
        self.personal_space_radius = 2
        self.visited_positions = []
        self.memory_limit = 4
        self.has_moved = False
        self.reached_destination = False

    def is_finished(self, x, y):
        if abs(x - self.destination.pos[0]) + abs(y - self.destination.pos[1]) < 1:
            self.reached_destination = True

            if self.destination.preset == 'exit':
                self.model.schedule.remove(self)
                self.model.grid.remove_agent(self)
            return True
        return False

    def step(self):
        if not self.is_finished(self.pos[0], self.pos[1]):
            self.move_towards_goal_or_avoid_intruder(self.destination.pos)
            self.has_moved = True
        else:
            self.has_moved = False

    @staticmethod
    def calculate_distance(pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

    def normalize_distance(self, distance):
        return max(0, min(1, (self.personal_space_radius - distance) / self.personal_space_radius))

    def move_towards_goal_or_avoid_intruder(self, goal_pos):
        intruders = []
        for agent in self.model.schedule.agents:
            if agent.unique_id != self.unique_id:
                distance = self.calculate_distance(self.pos, agent.pos)
                if distance <= self.personal_space_radius:
                    intruders.append(agent)

        if not intruders:
            dx = goal_pos[0] - self.pos[0]
            dy = goal_pos[1] - self.pos[1]
            if abs(dx) > abs(dy):
                new_pos = (self.pos[0] + (1 if dx > 0 else -1), self.pos[1])
            else:
                new_pos = (self.pos[0], self.pos[1] + (1 if dy > 0 else -1))

            if (0 <= new_pos[0] < self.model.grid.width and
                    0 <= new_pos[1] < self.model.grid.height):
                if self.model.grid.is_cell_empty(new_pos):
                    self.model.grid.move_agent(self, new_pos)
                    self.update_visited_positions(new_pos)
            return

        directions = {
            "up": (self.pos[0], self.pos[1] + 1),
            "down": (self.pos[0], self.pos[1] - 1),
            "left": (self.pos[0] - 1, self.pos[1]),
            "right": (self.pos[0] + 1, self.pos[1])
        }

        forces = {}

        for direction, pos in directions.items():
            if 0 <= pos[0] < self.model.grid.width and 0 <= pos[1] < self.model.grid.height:
                total_force = 0
                for intruder in intruders:
                    distance = self.calculate_distance(pos, intruder.pos)
                    normalized_distance = self.normalize_distance(distance)
                    if normalized_distance > 0:
                        force = 1 / normalized_distance
                        total_force += force
                if pos in self.visited_positions:
                    total_force += 100
                forces[direction] = total_force
                if pos == self.destination.pos:
                    forces[direction] = -1

        if forces:
            sorted_directions = sorted(forces, key=forces.get)

            for direction in sorted_directions:
                best_pos = directions[direction]

                if (0 <= best_pos[0] < self.model.grid.width and
                        0 <= best_pos[1] < self.model.grid.height):
                    if self.model.grid.is_cell_empty(best_pos):
                        self.model.grid.move_agent(self, best_pos)
                        self.update_visited_positions(best_pos)
                        break

    def update_visited_positions(self, new_pos):
        self.visited_positions.append(new_pos)
        self.model.visited_counts[new_pos] = self.model.visited_counts.get(new_pos, 0) + 1
        if len(self.visited_positions) > self.memory_limit:
            self.visited_positions.pop(0)


class Obstacle(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos

    def step(self):
        pass


class Destination:
    def __init__(self, pos, preset, color):
        self.color = color
        self.preset = preset
        self.pos = pos


