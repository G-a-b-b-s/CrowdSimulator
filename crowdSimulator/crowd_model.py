import mesa
from agent import CrowdAgent, Destination


class CrowdModel(mesa.Model):

    def __init__(self, ag, ds, width=20, height=20):
        super().__init__()
        self.num_agents = ag
        self.num_destinations = ds
        self.grid = mesa.space.SingleGrid(width, height, False)
        self.schedule = mesa.time.SimultaneousActivation(self)
        self.destinations = set()
        self.visited_counts = {}

        self.generate_unique_destinations()

        for i in range(self.num_agents):
            a = CrowdAgent(i, self)
            self.schedule.add(a)

            while True:
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
                if self.grid.is_cell_empty((x, y)):
                    self.grid.place_agent(a, (x, y))
                    a.pos = x, y
                    break
        self.assign_destinations()

    def generate_unique_destinations(self):

        for _ in range(self.num_destinations):
            dest_x = self.random.randrange(self.grid.width - 1)
            dest_y = self.random.randrange(self.grid.height - 1)
            destination = (dest_x, dest_y)
            color = (0, 0, 128)
            objective = Destination(destination, 'exit', color)
            self.destinations.add(objective)

    def assign_destinations(self):
        for agent in self.agents:
            destination = self.random.choice(list(self.destinations))
            agent.destination = destination

    def spawn_agent(self):
        if len(self.schedule.agents) < self.num_agents + 10:
            destination = self.random.choice(list(self.destinations))

            new_agent_id = len(self.schedule.agents)
            new_agent = CrowdAgent(new_agent_id, self)
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

            new_agent.destination = self.random.choice(list(self.destinations))

    def step(self):
        self.schedule.step()



