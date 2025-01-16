import os

import pygame
import random
from param_choice import ParamsChoice
from crowd_model import CrowdModel
from statistics import *
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io

class SimulationVisualization:

    def __init__(self):
        self.model = None
        self.grid_size = 20
        self.cell_size = 500 // self.grid_size
        self.agent_colors = {}
        self.plots = []
        self.current_plot_index = 0

        pygame.init()
        self.screen = pygame.display.set_mode((500, 500))
        pygame.display.set_caption("Crowd Simulation")
        self.clock = pygame.time.Clock()

    def draw_grid(self):
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                rect = pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)

    def draw_agents(self):
        for agent in self.model.schedule.agents:
            color = (95, 158, 160)
            pygame.draw.circle(self.screen, color, (agent.pos[0] * self.cell_size + self.cell_size // 2,
                                                    agent.pos[1] * self.cell_size + self.cell_size // 2),
                               self.cell_size // 3)

            for pos in agent.visited_positions:
                trail_surface = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                trail_color = (*color, 30)
                pygame.draw.circle(trail_surface, trail_color,
                                   (self.cell_size // 2, self.cell_size // 2), self.cell_size // 3)
                self.screen.blit(trail_surface, (pos[0] * self.cell_size, pos[1] * self.cell_size))

    def draw_objectives(self):
        for obj in self.model.destinations:
            color = obj.color
            pygame.draw.rect(self.screen, color, (obj.pos[0] * self.cell_size, obj.pos[1] * self.cell_size,
                                                  self.cell_size, self.cell_size))

    def draw_obstacles(self):
        for obj in self.model.obstacles:
            color = (128, 128, 128)
            pygame.draw.rect(self.screen, color, (obj.pos[0] * self.cell_size, obj.pos[1] * self.cell_size,
                                                  self.cell_size, self.cell_size))

    def draw_button(self, text, rect, color):
        pygame.draw.rect(self.screen, color, rect)
        font = pygame.font.Font(None, 36)
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)

    def menu(self):
        running = True

        logo_rect = pygame.Rect(100, 50, 300, 100)
        logo_path = 'assets/title.png'
        logo_image = pygame.image.load(logo_path)
        logo_image = pygame.transform.scale(logo_image, (logo_rect.width, logo_rect.height))

        while running:
            self.screen.fill((230, 230, 230))
            self.screen.blit(logo_image, (logo_rect.x, logo_rect.y))

            walk_button_rect = pygame.Rect(150, 200, 200, 50)
            evac_button_rect = pygame.Rect(150, 300, 200, 50)

            self.draw_button("Walking", walk_button_rect, (128, 238, 128))
            self.draw_button("Evacuation", evac_button_rect, (240, 128, 128))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if walk_button_rect.collidepoint(event.pos):
                        return "Walking"
                    if evac_button_rect.collidepoint(event.pos):
                        return "Evacuation"

            pygame.display.flip()
            self.clock.tick(60)

    def run(self):
        scenario = self.menu()
        self.run_scenario(scenario)

    def run_scenario(self, scenario):
        running = True

        params = ParamsChoice()
        directory = f"presets/{params.menu()}"
        self.model = CrowdModel(directory, scenario)
        self.screen = pygame.display.set_mode((500, 500))
        pygame.display.flip()

        for agent in self.model.schedule.agents:
            self.agent_colors[agent.unique_id] = (0,150,255)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.screen.fill((255, 255, 255))
            self.draw_grid()
            self.draw_objectives()
            self.draw_agents()
            self.draw_obstacles()
            pygame.display.flip()
            self.clock.tick(30)
            self.model.step()
            self.model.count_intruders()


            # Ważne, procentowo szansa na zrespienie agenta z każdym tickiem
            if random.randint(1, 20) >= 17:
                self.model.spawn_agent()

            if all(not agent.has_moved for agent in self.model.schedule.agents):
                for agent in self.model.schedule.agents:
                    print(agent.reached_destination)
                running = False

        self.show_statistics_in_pygame()

        pygame.quit()

    def show_statistics_in_pygame(self):
        stats = Statistics()

        fig1 = stats.plot_space_frequency(self.model.visited_counts, self.model.grid.width,
                                                     self.model.grid.height)
        fig2 = stats.plot_collision_history(self.model.collision_history)
        fig3 = stats.plot_intruders_by_zone(self.model.intruders_history)
        self.add_plot(fig1)
        self.add_plot(fig2)
        self.add_plot(fig3)

        self.show_plots()

    def figure_to_surface(self, fig):

        canvas = FigureCanvas(fig)
        canvas.draw()
        width, height = canvas.get_width_height()
        buf = canvas.buffer_rgba()
        surface = pygame.image.frombuffer(buf, (width, height), "RGBA")

        return surface

    def add_plot(self, fig):
        surface = self.figure_to_surface(fig)
        self.plots.append(surface)

    def show_plots(self):
        running = True

        while running:
            self.screen.fill((255, 255, 255))

            if self.plots:
                plot_surface = self.plots[self.current_plot_index]
                plot_rect = plot_surface.get_rect(center=(250, 250))
                self.screen.blit(plot_surface, plot_rect.topleft)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        self.current_plot_index = (self.current_plot_index + 1) % len(self.plots)
                    if event.key == pygame.K_LEFT:
                        self.current_plot_index = (self.current_plot_index - 1) % len(self.plots)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()