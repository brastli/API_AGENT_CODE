import db
import ai_agent
import executor
import time

def main():
    print("🚀 AutoTestAgent 启动...")
    
    # 1. 初始化数据库（建表）
    db.init_db()
    
    while True:
        # 2. 获取任务
        tasks = db.get_pending_tasks()
        if not tasks:
            print("💤 暂无任务，等待 10 秒...")
            time.sleep(10)
            continue
            
        task = tasks[0]
        print(f"👉 处理任务: {task['url']}")

        # 3. AI 生成初版代码
        code = ai_agent.generate_test_code(task)
        
        # 4. 迭代运行与修复 (最多重试 3 次)
        final_output = ""
        run_success = False
        
        for attempt in range(3):
            print(f"   🔄 第 {attempt + 1} 次尝试运行...")
            is_ok, output = executor.run_python_code(code)
            
            if is_ok:
                run_success = True
                final_output = output
                print("   ✅ 代码运行成功！")
                break
            else:
                print(f"   ❌ 运行报错: {output.strip()[:50]}...")
                # 让 AI 修复代码
                code = ai_agent.fix_code(code, output)

        # 5. AI 评估结果
        if run_success:
            evaluation = ai_agent.evaluate_output(task, final_output)
            is_pass = "PASS" in evaluation
        else:
            evaluation = "FAIL: 代码经过 3 次修复仍无法运行"
            final_output = output # 最后的错误信息
            is_pass = False

        print(f"🤖 评估结果: {evaluation}")

        # 6. 存入数据库
        db.save_result(task['id'], code, final_output, evaluation, is_pass)
        print("💾 结果已保存。\n")

if __name__ == "__main__":
    main()