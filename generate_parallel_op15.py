from data_gen.pretrain.id_gen import IdGen
from tools.tools import tokenizer, fix_seed, to_sketch, to_hash
from tools.tools_test import true_correct  # 添加验证函数
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
        max_op=op_target,    # Target op value
        max_edge=20,         # Maximum number of edges in the structure graph
        perm_level=5,        # Random shuffle level for problem description
        detail_level=0       # Most detailed solution format
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
        
        # 添加解决方案验证
        correct, my_print, parser = true_correct(sol_text, id_gen.problem)
        
        # 只保留验证通过的问题
        if not correct:
            return None
        
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
    op_value = 15  # Target op value
    num_cpus = 96  # Total number of CPUs
    total_samples = 4096  # Total required samples
    samples_per_cpu = (total_samples + num_cpus - 1) // num_cpus  # Ceiling division
    
    # Create output directory specific to this op value
    output_dir = f"./output/igsm_med_pq_datasets_op{op_value}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Print configuration
    print(f"Generating dataset for op={op_value}")
    print(f"Using {num_cpus} CPUs")
    print(f"Each CPU will generate {samples_per_cpu} samples")
    print(f"Total expected samples: {samples_per_cpu * num_cpus}")
    print(f"Output directory: {output_dir}")
    
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
    
    # Save final results
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