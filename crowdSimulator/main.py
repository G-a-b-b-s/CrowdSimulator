import numpy as np
import pandas as pd
from crowd_model import CrowdModel
from model_visualization import SimulationVisualization


def main():
    """
    starter_model = CrowdModel(20)
    for i in range(250):
        starter_model.step()
    """

    model = CrowdModel(20, 10)
    visualization = SimulationVisualization(model)
    visualization.run()


if __name__=="__main__":
    main()
