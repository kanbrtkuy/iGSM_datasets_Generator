# from data_gen.pretrain.id_gen import IdGen
# from tools.tools import tokenizer, fix_seed, to_sketch, to_hash
# import random
# import json
# import os
# from tqdm.auto import tqdm
# import time
# import multiprocessing as mp
# import numpy as np
# import psutil

# def set_cpu_affinity(process_id, cpu_id):
#     """Set CPU affinity for a process"""
#     try:
#         proc = psutil.Process(process_id)
#         proc.cpu_affinity([cpu_id])
#     except Exception as e:
#         print(f"Failed to set CPU affinity: {e}")

# def generate_single_sample(args):
#     op_target, seed = args
    
#     # Set random seed for this process
#     random.seed(seed)
#     np.random.seed(seed)
    
#     # Generate med difficulty problem
#     id_gen = IdGen(
#         max_op=op_target,    # Target number of operations
#         max_edge=20,         # Maximum number of edges in the structure graph
#         perm_level=5,        # Random shuffle level for problem description
#         detail_level=0       # Most detailed solution format
#     )
    
#     try:
#         # Generate problem in pq format
#         id_gen.gen_prob([i for i in range(23)], p_format="pq")
        
#         # Check if the number of operations matches target
#         if id_gen.op_ != op_target:
#             return None
        
#         # Get problem, solution and answer
#         prob_text = tokenizer.decode(id_gen.prob_token)
#         sol_text = tokenizer.decode(id_gen.sol_token)
#         ans_text = tokenizer.decode(id_gen.ans_token)
        
#         # Calculate solution template hash
#         sketch = to_sketch(id_gen.problem, prob=None, sol=sol_text)
#         hash_val = to_hash(sketch['sol'], mod_num=23)
        
#         if hash_val >= 17:
#             # Construct data item
#             data = {
#                 "text": f"Question:{prob_text}\nSolution:{sol_text}\nAnswer:{ans_text}\n\n",
#                 "steps_required": len(sol_text.split('.')),
#                 "numerical_answer": ans_text.strip(),
#                 "solution_template_hash": hash_val,
#                 "operations": op_target
#             }
#             return data
#     except Exception as e:
#         print(f"Error generating sample: {str(e)}")
#     return None

# def worker(task_queue, result_queue, op_value):
#     while True:
#         try:
#             seed = task_queue.get_nowait()
#             result = generate_single_sample((op_value, seed))
#             if result is not None:
#                 result_queue.put((op_value, result))
#         except mp.queues.Empty:
#             break
#         except Exception as e:
#             print(f"Error in worker: {str(e)}")

# class MultiProgressManager:
#     def __init__(self, op_values, num_samples):
#         self.pbars = {}
#         for op_value in op_values:
#             self.pbars[op_value] = tqdm(total=num_samples, 
#                                       desc=f"Generating op={op_value}",
#                                       position=op_value-20)  # Position based on op_value
        
#     def update(self, op_value):
#         self.pbars[op_value].update(1)
        
#     def close(self):
#         for pbar in self.pbars.values():
#             pbar.close()

# def generate_datasets(op_values, num_samples=4096):
#     # Create output directory
#     output_dir = "./output/igsm_med_pq_datasets"
#     os.makedirs(output_dir, exist_ok=True)
    
#     # Create queues and result storage
#     task_queues = {op: mp.Queue() for op in op_values}
#     result_queue = mp.Queue()
#     valid_samples = {op: [] for op in op_values}
    
#     # Initialize progress bars
#     progress_manager = MultiProgressManager(op_values, num_samples)
    
#     # Generate seeds for each op value
#     for op_value in op_values:
#         base_seed = op_value * 100000
#         for i in range(num_samples * 10):
#             task_queues[op_value].put(base_seed + i)
    
#     # Create and start workers with CPU affinity
#     workers = []
#     for op_idx, op_value in enumerate(op_values):
#         base_cpu = op_idx * 24  # Each op gets 24 consecutive CPUs
#         for worker_idx in range(24):
#             cpu_id = base_cpu + worker_idx
#             p = mp.Process(target=worker, args=(task_queues[op_value], result_queue, op_value))
#             p.start()
#             # Set CPU affinity
#             set_cpu_affinity(p.pid, cpu_id)
#             workers.append(p)
#             print(f"Started worker for op={op_value} on CPU {cpu_id}")
    
#     # Collect results
#     completed_ops = set()
#     while len(completed_ops) < len(op_values):
#         try:
#             op_value, result = result_queue.get(timeout=1)
#             valid_samples[op_value].append(result)
#             progress_manager.update(op_value)
            
#             # Save results periodically
#             if len(valid_samples[op_value]) % 100 == 0:
#                 file_path = os.path.join(output_dir, f'igsm_med_pq_eval_e{op_value}.json')
#                 with open(file_path, 'a') as f:
#                     for sample in valid_samples[op_value][-100:]:
#                         f.write(json.dumps(sample) + '\n')
            
#             # Check if we have enough samples for this op_value
#             if len(valid_samples[op_value]) >= num_samples and op_value not in completed_ops:
#                 completed_ops.add(op_value)
                
#         except mp.queues.Empty:
#             # Check if all workers are done
#             if all(not p.is_alive() for p in workers):
#                 break
    
#     # Close progress bars
#     progress_manager.close()
    
#     # Wait for workers to finish
#     for p in workers:
#         p.join()
    
#     # Save final results
#     for op_value in op_values:
#         file_path = os.path.join(output_dir, f'igsm_med_pq_eval_e{op_value}.json')
#         with open(file_path, 'w') as f:
#             for sample in valid_samples[op_value][:num_samples]:
#                 f.write(json.dumps(sample) + '\n')
    
#     return {op: len(samples) for op, samples in valid_samples.items()}

# def main():
#     # Print CPU information
#     print(f"Total CPU cores available: {mp.cpu_count()}")
#     print(f"Physical cores: {psutil.cpu_count(logical=False)}")
#     print(f"Logical cores: {psutil.cpu_count(logical=True)}")
    
#     start_time = time.time()
    
#     # Generate all datasets
#     op_values = [20, 21, 22, 23]
#     results = generate_datasets(op_values, 4096)
    
#     # Print results
#     total_time = time.time() - start_time
#     print(f"\nGeneration completed:")
#     print(f"Total time: {total_time/60:.2f} minutes")
    
#     # Verify results
#     for op_value in op_values:
#         file_path = os.path.join("./output/igsm_med_pq_datasets", f'igsm_med_pq_eval_e{op_value}.json')
#         if os.path.exists(file_path):
#             with open(file_path, 'r') as f:
#                 count = sum(1 for _ in f)
#             print(f"op={op_value} dataset: {count} samples")
#         else:
#             print(f"Warning: No output file for op={op_value}")

# if __name__ == "__main__":
#     # Install psutil if not already installed
#     try:
#         import psutil
#     except ImportError:
#         import subprocess
#         subprocess.check_call(["pip", "install", "psutil"])
#         import psutil
    
#     # Clear screen and move cursor to top
#     print("\033[2J\033[H", end="")
    
#     # Set global random seed
#     fix_seed(42)
#     # Set start method for multiprocessing
#     mp.set_start_method('spawn')
#     main()

from data_gen.pretrain.id_gen import IdGen
from tools.tools import tokenizer, fix_seed, to_sketch, to_hash
import random
import json
import os
from tqdm import tqdm
import time
import multiprocessing as mp
import numpy as np
import psutil

def generate_single_sample(args):
    op_target, seed = args
    
    # Set random seed for this process
    random.seed(seed)
    np.random.seed(seed)
    
    # Generate med difficulty problem
    id_gen = IdGen(
        max_op=op_target,    
        max_edge=20,         
        perm_level=5,        
        detail_level=0       
    )
    
    try:
        # Generate problem in pq format
        id_gen.gen_prob([i for i in range(23)], p_format="pq")
        
        # Check if the number of operations matches target
        if id_gen.op_ != op_target:
            return None
        
        # Get problem, solution and answer
        prob_text = tokenizer.decode(id_gen.prob_token)
        sol_text = tokenizer.decode(id_gen.sol_token)
        ans_text = tokenizer.decode(id_gen.ans_token)
        
        # Calculate solution template hash
        sketch = to_sketch(id_gen.problem, prob=None, sol=sol_text)
        hash_val = to_hash(sketch['sol'], mod_num=23)
        
        if hash_val >= 17:
            # Construct data item
            data = {
                "text": f"Question:{prob_text}\nSolution:{sol_text}\nAnswer:{ans_text}\n\n",
                "steps_required": len(sol_text.split('.')),
                "numerical_answer": ans_text.strip(),
                "solution_template_hash": hash_val,
                "operations": op_target
            }
            return data
    except Exception as e:
        print(f"Error generating sample: {str(e)}")
    return None

def worker_process(cpu_id, op_value, samples_per_cpu, output_dir):
    # Set CPU affinity
    try:
        proc = psutil.Process()
        proc.cpu_affinity([cpu_id])
    except Exception as e:
        print(f"Failed to set CPU affinity for CPU {cpu_id}: {e}")
    
    # Create unique base seed for this CPU
    base_seed = op_value * 1000000 + cpu_id * 10000
    
    valid_samples = []
    attempts = 0
    
    # Create progress bar for this worker
    pbar = tqdm(total=samples_per_cpu, 
                desc=f"CPU {cpu_id:02d}",
                position=cpu_id)
    
    while len(valid_samples) < samples_per_cpu:
        seed = base_seed + attempts
        result = generate_single_sample((op_value, seed))
        if result is not None:
            valid_samples.append(result)
            pbar.update(1)
        attempts += 1
    
    pbar.close()
    
    # Save results to temporary file
    temp_file = os.path.join(output_dir, f'temp_cpu_{cpu_id:02d}.json')
    with open(temp_file, 'w') as f:
        for sample in valid_samples:
            f.write(json.dumps(sample) + '\n')
    
    return len(valid_samples)

def main():
    # Parameters
    op_value = 23  # Target op value
    num_cpus = 96  # Total number of CPUs
    total_samples = 4096  # Total required samples
    samples_per_cpu = (total_samples + num_cpus - 1) // num_cpus  # Ceiling division
    
    # Create output directory
    output_dir = "./output/igsm_med_pq_datasets"
    os.makedirs(output_dir, exist_ok=True)
    
    # Print configuration
    print(f"Generating dataset for op={op_value}")
    print(f"Using {num_cpus} CPUs")
    print(f"Each CPU will generate {samples_per_cpu} samples")
    print(f"Total expected samples: {samples_per_cpu * num_cpus}")
    
    # Create and start processes
    processes = []
    start_time = time.time()
    
    for cpu_id in range(num_cpus):
        p = mp.Process(
            target=worker_process,
            args=(cpu_id, op_value, samples_per_cpu, output_dir)
        )
        p.start()
        processes.append(p)
    
    # Wait for all processes to complete
    for p in processes:
        p.join()
    
    # Combine all temporary files
    all_samples = []
    for cpu_id in range(num_cpus):
        temp_file = os.path.join(output_dir, f'temp_cpu_{cpu_id:02d}.json')
        if os.path.exists(temp_file):
            with open(temp_file, 'r') as f:
                for line in f:
                    all_samples.append(json.loads(line))
            # Remove temporary file
            os.remove(temp_file)
    
    # Save final results (taking exactly total_samples samples)
    final_file = os.path.join(output_dir, f'igsm_med_pq_eval_e{op_value}.json')
    with open(final_file, 'w') as f:
        for sample in all_samples[:total_samples]:
            f.write(json.dumps(sample) + '\n')
    
    # Print statistics
    total_time = time.time() - start_time
    print(f"\nGeneration completed:")
    print(f"Total time: {total_time/60:.2f} minutes")
    print(f"Total samples generated: {len(all_samples)}")
    print(f"Samples kept: {total_samples}")
    print(f"Output saved to: {final_file}")

if __name__ == "__main__":
    # Clear screen
    print("\033[2J\033[H", end="")
    
    # Set global random seed
    fix_seed(42)
    # Set start method for multiprocessing
    mp.set_start_method('spawn')
    main()
