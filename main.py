from engine.genome import Genome
from engine.ca import CellularAutomaton
from ui.interface import SimulationWindow


def main():
    # genome = Genome.make_conway()
    genome = Genome.make_random()
    
    grid_size = (400, 250)
    cell_size = 4
    
    ca = CellularAutomaton(genome, grid_size)
    window = SimulationWindow(ca, cell_size=cell_size)
    window.run(fps=30)


if __name__ == "__main__":
    main()
