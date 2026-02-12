import subprocess
import os

def run_python_code(code_str):
    filename = "temp_test_script.py"
    
    # 1. 写入临时文件
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code_str)
    
    try:
        # 2. 调用子进程运行
        # timeout=10 防止死循环
        result = subprocess.run(
            ["python3", filename], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        # 3. 清理文件
        if os.path.exists(filename):
            os.remove(filename)

        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr

    except subprocess.TimeoutExpired:
        return False, "Error: Execution timed out."
    except Exception as e:
        return False, str(e)