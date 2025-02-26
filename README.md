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

## How to create train and evaluation datasets

### Usage

1. **Training Set Generator (Single CPU)**:
   Generate the training dataset (50k problems) on a single CPU machine:
   ```bash
   python igsm_med_pq_train.py
   ```

2. **Evaluation Set Generator (Cluster Required)**:
   Generate the evaluation datasets on a cluster with 96+ CPUs:
   ```bash
   python generate_parallel_*.py
   ```
   Note: This script requires a computing cluster with at least 96 CPUs to run properly.

### Output Structure

Directory Structure:
```
./iGSM_datasets_Generator/output/igsm_med_pq_datasets
├── igsm_med_pq_train_le15.json
├── igsm_med_pq_eval_le15.json
├── igsm_med_pq_eval_e15.json
├── igsm_med_pq_eval_e20.json
├── igsm_med_pq_eval_e21.json
├── igsm_med_pq_eval_e22.json
├── igsm_med_pq_eval_e23.json
└── evaluation.json
```

### Example Output

#### Example from Training Set (igsm_med_pq_train.py)

```json
{
  "text": "Question: The number of each Veins's Hepatocytes equals 0. The number of each Salt Marsh's Banshee equals 1. The number of each Banshee's Mitral Valve equals 6 more than each Leprechaun's Organs. The number of each Mitral Valve's Basal Cells equals 19 times as much as the sum of each Estuary's Cells, each Deep Sea Ecosystem's Creatures and each Deep Sea Ecosystem's Organs. The number of each Leprechaun's Capillaries equals 22 times as much as each Salt Marsh's Banshee. The number of each Banshee's Veins equals each Veins's Ciliated Epithelial Cells. The number of each Salt Marsh's Leprechaun equals each Veins's Ciliated Epithelial Cells. The number of each Salt Marsh's Gorgon equals each Deep Sea Ecosystem's Organs. The number of each Veins's Ciliated Epithelial Cells equals the sum of each Banshee's Mitral Valve and each Leprechaun's Capillaries. How many Veins does Banshee have?\nSolution: Define Salt Marsh's Banshee as T; so T = 1. Define Leprechaun's Capillaries as o; so o = 22 * T = 22 * 1 = 22. Define Leprechaun's Organs as p; so p = o = 22. Define Banshee's Mitral Valve as e; so e = 6 + p = 6 + 22 = 5. Define Veins's Ciliated Epithelial Cells as M; so M = e + o = 5 + 22 = 4. Define Banshee's Veins as V; so V = M = 4.\nAnswer: 4\n\n",
  "steps_required": 7,
  "numerical_answer": "4",
  "solution_template_hash": 0,
  "operations": 15
}
```

#### Example from Evaluation Set (generate_parallel_*.py)

```json
{
  "text": "Question: The number of each Tiergarten in Berlin's Dolphin equals 17. The number of each Dolphin's Hypothalamus equals 22. The number of each Tiergarten in Berlin's Sea Urchin equals 15. The number of each Griffith Park in Los Angeles's Puffer Fish equals 15 times as much as each Tiergarten in Berlin's Sea Urchin. The number of each Dolphin's Occipital Lobe equals each Sea Urchin's Organs. The number of each Dolphin's Autonomic Nerves equals 2 more than each Tiergarten in Berlin's Dolphin. How many Organs does Griffith Park in Los Angeles have?\nSolution: Define Tiergarten in Berlin's Sea Urchin as V; so V = 15. Define Griffith Park in Los Angeles's Puffer Fish as U; so U = 15 * V = 15 * 15 = 18. Define Puffer Fish's Organs as G; so G = 0. Define Griffith Park in Los Angeles's Organs as x; so x = U * G = 18 * 0 = 0.\nAnswer: 0\n\n",
  "steps_required": 5,
  "numerical_answer": "0",
  "solution_template_hash": 19,
  "operations": 15
}
```

### Metadata Fields

1. **steps_required**: Number of steps needed to solve the problem
2. **numerical_answer**: Final numerical answer
3. **solution_template_hash**: Solution format category identifier
4. **operations**: Number of mathematical operations needed to solve the problem

### How to use count_outputs_sol_op.py

### Usage

   igsm_med_pq_train.py script is used to query how many problem data entries correspond to each op value in each JSON file under the igsm_med_pq_datasets path

   ```bash
   python igsm_med_pq_train.py
   ```


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
