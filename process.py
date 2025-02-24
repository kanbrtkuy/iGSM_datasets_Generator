import json
import hashlib

def calculate_template_hash(solution_text: str) -> int:
    # 1. 获取原始solution
    solution_lines = [s.strip() for s in solution_text.strip().split('. ')]
    
    # 2. 转换为template
    # 替换所有数字为'0'
    for i in range(23, -1, -1):  # 确保先替换大数字
        for j, line in enumerate(solution_lines):
            solution_lines[j] = line.replace(str(i), "0")
    
    # 收集并替换变量
    variables = []
    template_lines = []
    for line in solution_lines:
        if "Define" in line and " as " in line:
            try:
                # 分割成定义部分和计算部分
                define_part = line.split("; so ")[0]
                calc_part = line.split("; so ")[1] if "; so " in line else ""
                
                # 处理定义部分
                parts = define_part.split(" as ")
                if len(parts) >= 2:
                    var = parts[1]
                    if var not in variables:
                        variables.append(var)
                    var_index = variables.index(var)
                    new_var = chr(97 + var_index)  # a, b, c, ...
                    
                    # 构建新的模板行
                    new_line = "Define Inst as " + new_var
                    if calc_part:
                        new_line += "; so " + calc_part
                    template_lines.append(new_line)
            except Exception as e:
                print(f"Error processing line: {line}")
                print(f"Error: {e}")
                continue
    
    # 3. 计算hash值
    template_str = ". ".join(template_lines)
    hash_object = hashlib.sha256(template_str.encode())
    hash_integer = int(hash_object.hexdigest(), 16)
    hash_value = hash_integer % 23
    
    return hash_value

def process_data():
    # 读取原始数据
    with open('./processed_data.json', 'r') as f:
        data = [json.loads(line) for line in f]
    
    # 存储hash值>=17的数据
    eval_data = []
    
    # 处理每条数据
    for item in data:
        try:
            # 提取solution部分
            solution = item['text'].split('Solution: ')[1].split('Answer:')[0].strip()
            
            # 计算正确的hash值
            correct_hash = calculate_template_hash(solution)
            
            # 更新hash值
            item['solution_template_hash'] = correct_hash
            
            # 如果hash值>=17，加入评估数据集
            if correct_hash >= 17:
                eval_data.append(item)
        except Exception as e:
            print(f"Error processing item: {item}")
            print(f"Error: {e}")
            continue
    
    # 将评估数据写入文件
    with open('./output/igsm_med_pq_datasets/evaluation.json', 'w') as f:
        for item in eval_data:
            f.write(json.dumps(item) + '\n')
    
    print(f"Processed {len(data)} items")
    print(f"Found {len(eval_data)} items with hash >= 17")
    print("Evaluation data saved to ./output/igsm_med_pq_datasets/evaluation.json")

if __name__ == "__main__":
    process_data()
