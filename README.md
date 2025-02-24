# iGSM Datasets Generator

This project is modified from iGSM (Facebook Research) to specifically generate `iGSM_med_pq` style mathematical word problems. While the original iGSM project focuses on interpretable generation of synthetic math word problems, this modified version streamlines the process to directly generate `iGSM_med_pq` format datasets.

* "Physics of Language Models: Part 2.1, Grade-School Math and the Hidden Reasoning Process" This code is designed to *generate* grade-school math problems, solution and answer in Zhu's team's designed problem class (see **Part 2.1**).

## Instance Parameters

### Core Parameters
* Instance parameters (ip) must be ≤ 20
* Training set problems: operands (op) ≤ 15
* Evaluation set problems: operands (op) range {15, 20, 21, 22, 23}
* Evaluation data requires reask versions

### Data Volume Requirements
* Evaluation data: 4,096 math problems per configuration
* Training data: Dynamically generated with no fixed limit

### Data Split Method
* Training set: Solution template hash value < 17 (mod 23)
* Test set: Solution template hash value ≥ 17 (mod 23)

### Data Generation Process
1. **Structure Graph Generation**
   * Creates the basic mathematical structure
   * Defines relationships between variables
   * Establishes problem complexity

2. **Dependency Graph Generation**
   * Maps variable dependencies
   * Ensures logical problem flow
   * Validates solution paths


## Requirements
iGSM requires or works with Python version 3.8.11 or newer.

Install all required dependencies from requirements.txt
```bash
pip install -r requirements.txt
```

## How igsm_med_pq_*.py works
### Usage
Run the generator with default settings:
```bash
python igsm_med_pq_*.py
```

### Output Structure
Directory Structure
```
./iGSM_datasets_Generator/output/igsm_med_pq_datasets
├── igsm_med_pq_train.json
├── igsm_med_pq_eval_le15.json
├── igsm_med_pq_eval_e15.json
└── evaluation.json
```

### Example Output
Here's an example of a generated problem:
```json
{"text": "Question:  The number of each Canned Sauces's Rosemary equals 4 more than each Canned Sauces's Oregano. The number of each Canned Vegetables's Oregano equals 19. The number of each Canned Olives's Oregano equals 9 times as much as each Canned Sauces's Ingredient. The number of each GrubMarket's Canned Vegetables equals the sum of each Ocado's Product and each GrubMarket's Canned Sauces. The number of each GrubMarket's Canned Sauces equals 4 more than the sum of each Ocado's Product and each Canned Sauces's Rosemary. The number of each Canned Vegetables's Rosemary equals 5. The number of each Blue Apron's Canned Olives equals each Canned Olives's Onion Powder. The number of each Blue Apron's Canned Sauces equals 10 more than each Canned Vegetables's Oregano. The number of each Canned Sauces's Onion Powder equals each Canned Sauces's Oregano. The number of each Canned Olives's Rosemary equals each Canned Sauces's Ingredient. The number of each Blue Apron's Canned Vegetables equals the sum of each Canned Sauces's Ingredient and each GrubMarket's Canned Vegetables. The number of each Canned Vegetables's Onion Powder equals 1 times as much as the sum of each GrubMarket's Product and each Canned Sauces's Ingredient. The number of each Canned Olives's Onion Powder equals 11. The number of each Ocado's Canned Olives equals 21 more than each Canned Olives's Oregano. The number of each GrubMarket's Canned Olives equals 18 more than each GrubMarket's Canned Sauces. The number of each Ocado's Canned Vegetables equals each Canned Olives's Oregano. The number of each Ocado's Canned Sauces equals each Canned Sauces's Onion Powder. The number of each Canned Sauces's Oregano equals 9 more than each Canned Vegetables's Oregano. How many Canned Olives does GrubMarket have?\nSolution:  Define Canned Vegetables's Oregano as y; so y = 19. Define Canned Sauces's Oregano as b; so b = 9 + y = 9 + 19 = 5. Define Canned Sauces's Rosemary as k; so k = 4 + b = 4 + 5 = 9. Define Canned Sauces's Onion Powder as P; so P = b = 5. Define Canned Sauces's Ingredient as t; r = k + b = 9 + 5 = 14; so t = r + P = 14 + 5 = 19. Define Canned Olives's Oregano as c; so c = 9 * t = 9 * 19 = 10. Define Ocado's Canned Sauces as B; so B = P = 5. Define Ocado's Canned Vegetables as d; so d = c = 10. Define Ocado's Canned Olives as w; so w = 21 + c = 21 + 10 = 8. Define Ocado's Product as Q; D = d + w = 10 + 8 = 18; so Q = D + B = 18 + 5 = 0. Define GrubMarket's Canned Sauces as Z; J = Q + k = 0 + 9 = 9; so Z = 4 + J = 4 + 9 = 13. Define GrubMarket's Canned Olives as A; so A = 18 + Z = 18 + 13 = 8.\nAnswer:  8\n\n", "steps_required": 12, "numerical_answer": "8", "solution_template_hash": 17}
```

### Metadata Fields

1. steps_required: Number of steps needed to solve
2. numerical_answer: Final numerical answer
3. solution_template_hash: solution format category

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
