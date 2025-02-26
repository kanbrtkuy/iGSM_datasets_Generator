from data_gen.pretrain.id_gen import IdGen
from tools.tools import tokenizer, fix_seed, to_sketch, to_hash
from tools.tools_test import true_correct
import random
import json
import os
from tqdm import tqdm
import time

def generate_igsm_med_dataset(num_samples=500, seed=42):
    # Set random seed
    fix_seed(seed)
    
    # Store generated data
    count = 0
    attempts = 0
    
    # Batch write to file
    batch_size = 1000
    
    # Create output directory
    output_dir = "./output/igsm_med_pq_datasets"
    os.makedirs(output_dir, exist_ok=True)
    
    file_path = os.path.join(output_dir, 'igsm_med_pq_train_le15.json')
    
    # Create progress bar
    pbar = tqdm(total=num_samples, desc="Generating samples")
    start_time = time.time()
    
    with open(file_path, 'w') as f:
        while count < num_samples:
            attempts += 1
            # Generate med difficulty problem
            id_gen = IdGen(
                max_op=15,        # Maximum number of operations
                max_edge=20,      # Maximum number of edges in the structure graph
                perm_level=5,     # Random shuffle level for problem description
                detail_level=0    # Most detailed solution format
            )
            
            # Generate problem in pq format (problem first)
            id_gen.gen_prob([i for i in range(23)], p_format="pq")
            
            # Get problem, solution and answer
            prob_text = tokenizer.decode(id_gen.prob_token)
            sol_text = tokenizer.decode(id_gen.sol_token)
            ans_text = tokenizer.decode(id_gen.ans_token)
            
            # 添加解决方案验证
            correct, my_print, parser = true_correct(sol_text, id_gen.problem)
            
            # 只保留验证通过的问题
            if not correct:
                continue
            
            # Calculate solution template hash
            sketch = to_sketch(id_gen.problem, prob=None, sol=sol_text)
            hash_val = to_hash(sketch['sol'], mod_num=23)
            
            # Check if hash value meets requirement (< 17)
            if hash_val < 17:
                # Construct complete text
                full_text = f"Question:{prob_text}\nSolution:{sol_text}\nAnswer:{ans_text}\n\n"
                
                # Construct data item
                data = {
                    "text": full_text,
                    "steps_required": len(sol_text.split('.')), # Number of solution steps
                    "numerical_answer": ans_text.strip(),
                    "solution_template_hash": hash_val
                }
                
                # Write to file
                f.write(json.dumps(data) + '\n')
                
                count += 1
                pbar.update(1)
                
                # Update progress bar description, show success rate and estimated time remaining
                if count % 100 == 0:
                    elapsed_time = time.time() - start_time
                    success_rate = count / attempts * 100
                    avg_time_per_sample = elapsed_time / count
                    remaining_samples = num_samples - count
                    eta = remaining_samples * avg_time_per_sample
                    
                    pbar.set_description(
                        f"Generated: {count}/{num_samples} | "
                        f"Success rate: {success_rate:.2f}% | "
                        f"ETA: {eta/60:.2f}min"
                    )
    
    # Close progress bar
    pbar.close()
    
    # Print final statistics
    total_time = time.time() - start_time
    final_success_rate = count / attempts * 100
    print(f"\nGeneration completed:")
    print(f"Total samples: {count}")
    print(f"Total attempts: {attempts}")
    print(f"Success rate: {final_success_rate:.2f}%")
    print(f"Total time: {total_time/60:.2f} minutes")
    print(f"Average time per sample: {total_time/count:.2f} seconds")
    print(f"Output saved to: {file_path}")

# Generate dataset
generate_igsm_med_dataset()