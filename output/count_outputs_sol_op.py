import os
import sys
import json
from collections import Counter
# Add project root directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Get parent directory
sys.path.append(project_root)

from tools.sol_parser import Parser
from math_gen.problem_gen import Problem
from data_gen.categ import Data

def analyze_file_solution_ops(file_path):
    """Analyze solution operations in a single file"""
    sol_op_values = []
    parse_failed_count = 0
    
    # Read each line in the file
    with open(file_path, 'r') as in_f:
        for idx, line in enumerate(in_f):
            data = json.loads(line)
            
            # Extract solution part
            text = data['text']
            solution_start = text.find("Solution:") + len("Solution:")
            solution_end = text.find("Answer:")
            solution_text = text[solution_start:solution_end].strip()
            
            # Extract question part for creating Problem instance
            question_text = text[:text.find("Solution:")].strip()
            if question_text.startswith("Question: "):
                question_text = question_text[len("Question: "):]
            
            # Extract answer
            answer_start = text.find("Answer:") + len("Answer:")
            answer_text = text[answer_start:].strip()
            
            # Create Problem instance
            args = {
                "rand_perm": "mild_0",
                "define_var": True,
                "define_detail": True,
                "inter_var": True,
                "name_omit": False,
                "cal_omit": True,
                "dot": "# ",
                "symbol_method": "seq",
                "sol_sort": False,
                "perm": True
            }
            
            problem = Problem(2, 2, 3, 5, 0.5, args=args)
            problem.problem = question_text.split(". ")
            try:
                problem.ans = int(answer_text)
            except:
                problem.ans = answer_text
            
            # Initialize Problem instance and calculate sol_op
            try:
                problem.gen(n=5, m=8, s=10)
                problem.to_problem()
                
                parser = Parser(gpt_sol=solution_text)
                parser.parse(problem=problem)
                sol_op_values.append(parser.sol_op)
            except Exception as e:
                parse_failed_count += 1
    
    return Counter(sol_op_values), parse_failed_count

def analyze_all_json_files():
    # Get all json files in directory
    dataset_dir = os.path.join(current_dir, 'igsm_med_pq_datasets')
    json_files = [f for f in os.listdir(dataset_dir) if f.endswith('.json')]
    
    # Sort files by name
    json_files.sort()
    
    # Analyze each file
    for json_file in json_files:
        file_path = os.path.join(dataset_dir, json_file)
        print(f"\nAnalyzing file: {json_file}")
        print("=" * 50)
        
        # Analyze current file
        op_counts, parse_failed_count = analyze_file_solution_ops(file_path)
        
        # Print statistics
        print("\nSolution Operations Statistics:")
        print("-" * 40)
        print("Operations | Problem Count")
        print("-" * 40)
        
        for op in sorted(op_counts.keys()):
            print(f"{op:^11d} | {op_counts[op]:^8d}")
        
        print("-" * 40)
        total_success = sum(op_counts.values())
        print(f"Successfully parsed problems: {total_success}")
        print(f"Failed to parse problems: {parse_failed_count}")
        print(f"Total problems: {total_success + parse_failed_count}")
        
        if op_counts:
            avg_ops = sum(op * count for op, count in op_counts.items()) / total_success
            print(f"Average operations: {avg_ops:.2f}")
        
        print("=" * 50)

if __name__ == "__main__":
    analyze_all_json_files()