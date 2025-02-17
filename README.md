# GSM8K Generator
This project is modified from iGSM (Facebook Research) to specifically generate GSM8K-style mathematical word problems. While the original iGSM project focuses on interpretable generation of synthetic math word problems, this modified version streamlines the process to directly generate GSM8K format datasets.

* ["Physics of Language Models: Part 2.1, Grade-School Math and the Hidden Reasoning Process"](https://arxiv.org/abs/2407.20311)

This code is designed to *generate* grade-school math problems, solution and answer in Zhu's team's designed problem class (see **Part 2.1**).


## Requirements
iGSM requires or works with Python version 3.8.11 or newer.

Install all required dependencies from requirements.txt
```bash
pip install -r requirements.txt
```

## How GSM8Kgenerator.py works
### Usage
Run the generator with default settings:
```bash
python example_iGSM.py
```

### Key Parameters
In the code, you can modify these main parameters:
```python
TOTAL_PROBLEMS = 8500  # Total number of problems to generate
OUTPUT_DIR = "output/gsm8k_extended"  # Output directory
```

### Difficulty Parameters
```python
difficulty_params = {
    "easy": {"max_op": 10, "max_edge": 15, "perm_level": 3},
    "med": {"max_op": 15, "max_edge": 20, "perm_level": 5},
    "hard": {"max_op": 21, "max_edge": 28, "perm_level": 7}
}
```

1. max_op: Maximum number of operations
2. max_edge: Maximum number of edges in problem structure
3. perm_level: Level of permutation in problem description

### Topic Distribution
Available topics:

1. basic_arithmetic
2. percentage
3. ratio
4. time
5. money
6. measurement
7. word_problems

### Output Structure
Directory Structure
```
./GSM8K_GENERATOR/output/gsm8k_extended/
├── train.json
└── inference.json
```

### Data Split Distribution

1. Training set: 90% (7650 problems)
2. Inference set: 10% (850 problems)

### Example Output
Here's an example of a generated problem:
```json
{
  "text": "Question:  The number of each Skyview University's Engineering Workshop equals each Skyview University's Number Theory Room. The number of each Skyview University's Number Theory Room equals 19 times as much as each Seaview University's Robotics Lab. The number of each Meadowland University's Robotics Lab equals 11. The number of each Seaview University's Robotics Lab equals 3 more than each Meadowland University's Classroom. How many Engineering Workshop does Skyview University have?\nSolution:  Define Meadowland University's Robotics Lab as U; so U = 11. Define Meadowland University's Classroom as d; so d = U = 11. Define Seaview University's Robotics Lab as M; so M = 3 + d = 3 + 11 = 14. Define Skyview University's Number Theory Room as F; so F = 19 * M = 19 * 14 = 13. Define Skyview University's Engineering Workshop as l; so l = F = 13.\nAnswer:  13\n\n",
  "difficulty": "med",
  "topic": "basic_arithmetic",
  "steps_required": 5,
  "numerical_answer": "13"
}
```

### Metadata Fields

1. difficulty: Problem difficulty level (easy/med/hard)
2. topic: Mathematical topic category
3. steps_required: Number of steps needed to solve
4. numerical_answer: Final numerical answer

### Modifying Difficulty Distribution
You can adjust the distribution of problem difficulties by modifying:
```python
difficulty_dist = {
    "easy": 0.3,  # 30% easy problems
    "med": 0.5,   # 50% medium problems
    "hard": 0.2   # 20% hard problems
}
```

### Adding New Topics
Add new topics to the topics list in MathProblemGenerator class:
```python
self.topics = [
    "basic_arithmetic",
    "percentage",
    # Add new topics here
]
```

### Error Handling
The generator includes error handling for:

1. Problem generation failures
2. File I/O operations
3. Token decoding issues
   
Failed problem generations are logged but don't halt the overall process.

### Notes

1. Uses random seed (42) for reproducibility
2. Generates problems with varying complexity
3. Includes detailed step-by-step solutions
4. Provides metadata for each problem

## Full Documentation

### Problem and Graph Inheritance
When `id_gen.gen_prob()` is invoked, it initializes a `Problem` instance named `id_gen.problem`. The `Problem` class extends the `Graph` class, which is designed to handle the generation and management of specific details relevant to the problem:
- **Graph Class**: Stores structural and dependency graphs that outline the relationships and dependencies among different elements of the problem.
- **Problem Class**: Responsible for generating the names and exact values of parameters, along with crafting descriptive narratives for both the problem and its solution.

### Structure Graph
The structure graph is encoded in `id_gen.problem.G`, stored as a list of NumPy matrices with boolean values. Each entry `id_gen.problem.G[i][j, k]` signifies a connection between the node `(i, j)` and `(i+1, k)`, where `(i, j)` represents the `j`-th node at the `i`-th layer. This matrix helps visualize how nodes are interconnected layer by layer.

### Dependency Graph Nodes
The nodes within the dependency graph are represented by four-integer tuples, `(i, j, k, l)`, with specific meanings based on the value of `i`:
- **RNG Representation (`i = -1`)**: When `i` is -1, `j`, `k`, and `l` must all be 0, making the tuple `(-1, 0, 0, 0)` denote the **Random Number Generator (RNG)** used within the problem context.
- **Instance Parameter (`i = 0`)**: When `i` is 0, the tuple `(i, j, k, l)` identifies an **instance parameter**. It specifically counts the number of Item `(j, k)` in relation to Item `(j+1, k)`, such as counting the number of Music Rooms in Riverview High. The existence of such a parameter depends strictly on the truth of `id_gen.problem.G[j][k, l]`.
- **Abstract Parameter (`i = 1`)**: When `i` is 1, the tuple represents an **abstract parameter**, counting items of Category `k` within Item `(j, k)`, like the number of classrooms in Riverview High. Such parameters are only defined if feasible and if `j < l`.

The dependency graph is instantiated as ``id_gen.problem.template``, a directed graph using the ``networkx.DiGraph`` class.

### Additional Components
- **Value Lookup (`id_gen.problem.lookup`)**: This component is a dictionary mapping from the four-integer tuples to the respective parameter values.
- **Name Lookup (`id_gen.problem.N`)**: The array `id_gen.problem.N[i][j]` holds the name of the Item `(i, j)`.
- **Draw Graphs (`id_gen.problem.draw()`)**: This function will plot the structure graph and the dependency graph.

# Citation

Please cite this code and our iGSM dataset using
```bibtex
  @article{YXLA2024-gsm1,
    author = {Ye, Tian and Xu, Zicheng and Li, Yuanzhi and {Allen-Zhu}, Zeyuan},
    title = {{Physics of Language Models: Part 2.1, Grade-School Math and the Hidden Reasoning Process}},
    journal = {ArXiv e-prints},
    year = 2024,
    month = jul,
    volume = {abs/2407.20311},
    note = {Full version available at \url{http://arxiv.org/abs/2407.20311}}
  }
```

If you plan to use our retry data or the box-over-box data, please also cite our Part 2.2 paper as follows:
```bibtex
  @article{YXLA2024-gsm2,
    author = {Ye, Tian and Xu, Zicheng and Li, Yuanzhi and {Allen-Zhu}, Zeyuan},
    title = {{Physics of Language Models: Part 2.2, How to Learn From Mistakes on Grade-School Math Problems}},
    journal = {ArXiv e-prints},
    year = 2024,
    month = aug,
    volume = {abs/2408.16293},
    note = {Full version available at \url{http://arxiv.org/abs/2408.16293}}
  }
```

MIT License; please contact Tian Ye or Zeyuan Allen-Zhu if you have any questions.
