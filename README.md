generalized_game_of_life/
│
├── README.md
├── requirements.txt
├── main.py                 # Entry point to run the interactive UI
│
├── engine/
│   ├── __init__.py
│   ├── ca.py               # Cellular Automaton simulation logic
│   └── genome.py           # Genotype definition, mutation, and crossover
│
└── ui/
    ├── __init__.py
    └── interface.py        # Window management, rendering, and user input

    
notes:
    Scene manager:
        I like it
    Simulation panel:
        I like it, but it should also have a configurable cell_size
    Terminal widget:
        good ideas, I want to add some things as well
            - a side window that for each current state
              gives a list of available commands
            - when options can be selected (picking from
              genomes or config files, etc) I want those 
              options displayed, and for there to be 
              autocomplete behaior when I click tab
    Central Command Handling:
        I like it
