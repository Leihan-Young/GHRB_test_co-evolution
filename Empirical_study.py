import json
import os
import subprocess as sp

from cli import call_coverage
from cli import find_env

if __name__ == "__main__":
    with open("./project_id.json", "r") as f:
        project_id = json.load(f)

    tmp_work_dir = "../tmp_dir"
    tmp_output_dir = "../tmp_out_dir"


    for pid, val in project_id.items():
        res = {}
        if os.path.exists(f'./tmp_res/{pid}_result.json'):
            continue
        repo_path = project_id[pid]["repo_path"]
        with open(project_id[pid]["verified_db"], 'r', encoding='utf-8') as f:
            verified_db = json.load(f)
        new_env, mvnw, gradlew = find_env(pid)
        for i in range(val["number_of_tests"]):
            success_in_src = False
            success_in_tgt = False
            refer_pr = verified_db[f"{i+1}"]["refer_PR"]
            prod_diff = os.path.abspath(f'./collected/prod_diff/{refer_pr}.diff')
            work_dir = os.path.join(tmp_work_dir, f"{pid}_{i+1}s")
            if os.path.exists(work_dir):
                if os.path.exists(os.path.join(tmp_output_dir, "before_apply", f"{pid}-{i+1}s_cov_jacoco.xml")):
                    success_in_src = True
                if os.path.exists(os.path.join(tmp_output_dir, "after_apply", f"{pid}-{i+1}s_cov_jacoco.xml")):
                    success_in_tgt = True
                
            else:
                command = ['python', 'cli.py', 'checkout', '-p', pid, '-t', f'{i+1}s', '-w', work_dir]
                run = sp.run(command,
                            env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd='./', shell=True)
                output = run.stdout.decode(encoding='gbk', errors='ignore')
                print(output)
                # command = ['python', 'cli.py', 'coverage', '-w', work_dir, '-o', os.path.join(tmp_output_dir, "before_apply")]
                # run = sp.run(command,
                #             env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd='./', shell=True)
                output = call_coverage(work_dir, None, os.path.join(tmp_output_dir, "before_apply"), False)
                print(output)
                if "Test Success" in output:
                    success_in_src = True
                # else:
                #     print("Try coverage again")
                #     output = call_coverage(work_dir, None, os.path.join(tmp_output_dir, "before_apply"), False)
                #     print(output)
                #     if "Test Success" in output:
                #         success_in_src = True

                command = ['git', 'apply', '--ignore-space-change', '--ignore-whitespace', prod_diff]
                run = sp.run(command,
                            env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=work_dir, shell=True)
                output = run.stdout.decode(encoding='gbk', errors='ignore')
                print(output)
                if not mvnw and not gradlew:
                    out = sp.run([f'{new_env["MAVEN_HOME"]}/mvn', 'clean'], env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=work_dir, shell=True)
                elif mvnw:
                    out = sp.run(['./mvnw', 'clean'], env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=work_dir, shell=True)
                elif gradlew:
                    out = sp.run(['./gradlew', 'clean'], env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=work_dir, shell=True)
                
                # command = ['python', 'cli.py', 'coverage', '-w', work_dir, '-o', os.path.join(tmp_output_dir, "after_apply")]
                # run = sp.run(command,
                #             env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd='./', shell=True)
                output = call_coverage(work_dir, None, os.path.join(tmp_output_dir, "after_apply"), False)
                print(output)
                if "Test Success" in output:
                    success_in_tgt = True
                # else:
                #     print("Try coverage again")
                #     output = call_coverage(work_dir, None, os.path.join(tmp_output_dir, "after_apply"), False)
                #     print(output)
                #     if "Test Success" in output:
                #         success_in_tgt = True
                
            res[f"{pid}_{i+1}"] = {"success_in_src": success_in_src, "success_in_tgt": success_in_tgt}
            
        with open(f'./tmp_res/{pid}_result.json', 'w', encoding='utf-8') as f:
            json.dump(res, f, indent=2)
