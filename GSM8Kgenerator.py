import json
import os
import random
from data_gen.pretrain.id_gen import IdGen
from tools.tools import fix_seed, tokenizer
from typing import Literal, Dict, List
from tqdm import tqdm

class MathProblemGenerator:
    def __init__(self):
        self.topics = [
            "basic_arithmetic",  # Basic operations
            "percentage",        # Percentage calculations
            "ratio",            # Ratio problems
            "time",             # Time-related problems
            "money",            # Money calculations
            "measurement",      # Measurement problems
            "word_problems"     # Word problems
        ]
        
        self.difficulty_params = {
            "easy": {"max_op": 10, "max_edge": 15, "perm_level": 3},
            "med": {"max_op": 15, "max_edge": 20, "perm_level": 5},
            "hard": {"max_op": 21, "max_edge": 28, "perm_level": 7}
        }

    def generate_problem(self, difficulty: str, topic: str) -> Dict:
        """Generate a single math problem"""
        params = self.difficulty_params[difficulty]
        
        id_gen = IdGen(
            max_op=params["max_op"],
            max_edge=params["max_edge"],
            perm_level=params["perm_level"],
            detail_level=0
        )
        
        id_gen.gen_prob([i for i in range(23)], p_format="pq")
        
        # Decode tokens to text
        question = tokenizer.decode(id_gen.prob_token)
        solution = tokenizer.decode(id_gen.sol_token)
        answer = tokenizer.decode(id_gen.ans_token)
        
        # Calculate number of solution steps (split by periods, remove empty strings)
        solution_steps = [s.strip() for s in solution.split('.') if s.strip()]
        
        # Format the text field
        text = f"Question: {question}\nSolution: {solution}\nAnswer: {answer}\n\n"
        
        return {
            "text": text,
            "difficulty": difficulty,
            "topic": topic,
            "steps_required": len(solution_steps),
            "numerical_answer": answer.strip()
        }

class GSM8KDatasetCreator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.generator = MathProblemGenerator()
        
    def create_split(self, num_problems: int) -> List[Dict]:
        """Create dataset problems
        
        Args:
            num_problems: Number of problems to generate
            
        Returns:
            List of problem dictionaries
        """
        problems = []
        generated_questions = set()  # Track unique questions
        
        difficulty_dist = {
            "easy": 0.3,  # 30% easy problems
            "med": 0.5,   # 50% medium problems
            "hard": 0.2   # 20% hard problems
        }
        
        pbar = tqdm(total=num_problems, desc="Generating problems")
        while len(problems) < num_problems:
            try:
                difficulty = random.choices(
                    list(difficulty_dist.keys()),
                    weights=list(difficulty_dist.values())
                )[0]
                topic = random.choice(self.generator.topics)
                
                problem = self.generator.generate_problem(difficulty, topic)
                
                # Check if this question is unique
                if problem["text"] not in generated_questions:
                    generated_questions.add(problem["text"])
                    problems.append(problem)
                    pbar.update(1)
                    
            except Exception as e:
                print(f"Error generating problem: {str(e)}")
                continue
            
        pbar.close()
        return problems

    def create_dataset(self, total_problems: int):
        """Create complete dataset
        
        Args:
            total_problems: Total number of problems to generate
        """
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Calculate split sizes
        train_size = int(total_problems * 0.9)
        inference_size = total_problems - train_size
        
        # Generate all problems
        all_problems = self.create_split(total_problems)
        
        # Split problems
        train_problems = all_problems[:train_size]
        inference_problems = all_problems[train_size:]
        
        # Save splits
        splits = {
            "train": (train_problems, "train.json"),
            "inference": (inference_problems, "inference.json")
        }
        
        for split_name, (problems, filename) in splits.items():
            output_path = os.path.join(self.output_dir, filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(problems, f, indent=2, ensure_ascii=False)

def main():
    # Set random seeds for reproducibility
    fix_seed(42)
    random.seed(42)
    
    # Configure parameters
    TOTAL_PROBLEMS = 8500
    OUTPUT_DIR = "output/gsm8k_extended"
    
    # Create dataset
    creator = GSM8KDatasetCreator(OUTPUT_DIR)
    creator.create_dataset(TOTAL_PROBLEMS)
    
    print(f"\nDataset creation completed. Files saved in {OUTPUT_DIR}")
    
    # Print example
    try:
        with open(os.path.join(OUTPUT_DIR, "train.json"), 'r') as f:
            train_data = json.load(f)
            print("\nExample problem from training set:")
            example = train_data[0]  # Changed to access first element directly
            print("Text:", example["text"])
            print("Difficulty:", example["difficulty"])
            print("Topic:", example["topic"])
            print("Steps Required:", example["steps_required"])
            print("Numerical Answer:", example["numerical_answer"])
    except Exception as e:
        print(f"Error reading example: {str(e)}")

if __name__ == "__main__":
    main()