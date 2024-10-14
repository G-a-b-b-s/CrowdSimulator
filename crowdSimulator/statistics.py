import matplotlib.pyplot as plt
import numpy as np


class Statistics:

    @staticmethod
    def plot_space_frequency(visited_counts, grid_width, grid_height):
        visit_density = np.zeros((grid_width, grid_height))

        for (x, y), count in visited_counts.items():
            visit_density[x, y] = count

        plt.figure(figsize=(10, 8))
        plt.imshow(visit_density.T, interpolation='nearest')
        plt.colorbar(label='Częstość odwiedzin')
        plt.title('Mapa gęstości odwiedzin danego pola przez agentów')
        plt.xlabel('Oś X siatki')
        plt.ylabel('Oś Y siatki')
        plt.show()

