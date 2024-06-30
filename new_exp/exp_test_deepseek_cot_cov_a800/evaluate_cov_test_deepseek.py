import os
import json
import sys
import subprocess as sp
import xml.etree.ElementTree as ET
from cli import call_checkout, call_coverage, call_clean

"""
Exp content:
run `test_deepseek_fix` in `focal_tgt`
run `test_deepseek_enhance` in `focal_tgt`
"""

def get_coverage_for_single_method(cov_xml, focal_path: str):
    if not os.path.exists(cov_xml):
        return None
    try:
        cov = {}
        tree = ET.parse(cov_xml)
        root = tree.getroot()
        class_name = focal_path.split('#')[0].split('/')[-1]
        method_name = focal_path.split('#')[-1]
        for package_node in root.findall('package'):
            for class_node in package_node.findall('class'):
                if class_node.attrib['sourcefilename'] == class_name:
                    for method_node in class_node.findall('method'):
                        if (method_node.attrib['name'] == method_name) or (method_name == class_name.replace('.java', '') and 'init' in method_node.attrib['name']):
                            covered = True
                            for counter in method_node.findall('counter'):
                                if counter.attrib['covered'] == 0:
                                    covered = False
                                    break
                                cov[counter.attrib['type']] = {'missed': counter.attrib['missed'], 'covered': counter.attrib['covered']}
                            if covered:
                                break
    except Exception as e:
        return None
    return cov

def get_coverage(cov_xml, focal_path: list):
    if not os.path.exists(cov_xml):
        return None
    cov = {}
    for path in focal_path:
        cov[path] = get_coverage_for_single_method(cov_xml, path)
    return cov

def checkout(pid, tid, repo_path, commit):
    sp.run('git reset --hard HEAD',
        cwd=repo_path, stdout=sp.DEVNULL, stderr=sp.DEVNULL, shell=True)
    sp.run('git clean -df',
        cwd=repo_path, stdout=sp.DEVNULL, stderr=sp.DEVNULL, shell=True)
    sp.run(f'git checkout {commit}',
        stdout=sp.PIPE, stderr=sp.PIPE, cwd=repo_path, shell=True)
    with open(f"{repo_path}/.pidtid.config", "w") as f:
        f.write("#File automatically generated\n")
        f.write(f"pid={pid}\n")
        f.write(f"tid={tid}")
        f.close()

if __name__ == "__main__":
    cli_path = r'/data/zhiquanyang/Co-evolution/Benchmark'
    data_path = os.path.abspath('./new_exp/exp_test_deepseek_cot_cov_a800/data')
    output_dir = os.path.abspath('./new_exp/exp_test_deepseek_cot_cov_a800/output')
    tmp_path = os.path.abspath('./new_exp/exp_test_deepseek_cot_cov_a800/tmp')
    files = [name for name in os.listdir(data_path)
            if name.endswith('.json')]
    cov_res = {}
    for file in files:
        if os.path.exists(os.path.join(output_dir, file.replace('verified_tuples', 'cov'))):
            continue
        with open(os.path.join(data_path, file), 'r', encoding='utf-8') as f:
            data = json.load(f)
        pid = file.replace('.json', '').split('_')[-1]
        cov_file = {}
        for key, value in data.items():
            if "exception_while_gen_deepseek-coder" in value.keys() and 'identify_result_deepseek-coder' not in value.keys():
                test_deepseek_fix = value['test_src_code']
                test_deepseek_enhance = value['test_src_code']
            else:
                identify_result = value['identify_result_deepseek-coder']
                if not identify_result:
                    test_deepseek_fix = value['test_src_code']
                    test_deepseek_enhance = value['test_src_code']
                else:
                    test_deepseek_fix = value['test_fix_deepseek-coder'][0]
                    if value['test_enhance_deepseek-coder'][0].startswith("// Fail to generate"):
                        test_deepseek_enhance = test_deepseek_fix
                    else:
                        test_deepseek_enhance = value['test_enhance_deepseek-coder'][0]
            test_id = value['test_id']
            commit_tgt = value['commit_tgt']
            work_dir = f'/data/zhiquanyang/Co-evolution/Benchmark/repo_mirrors/{pid}/{test_id}t'
            checkout(pid, f'{test_id}t', work_dir, commit_tgt)
            # output = call_clean(work_dir)
            # print(output)

            # test_deepseek_fix在focal_tgt下的覆盖率
            print(f"Evaluating test_deepseek_fix under focal_tgt for {pid}:{test_id}")
            output_folder = os.path.join(output_dir, 'test_deepseek_fix_focal_tgt')
            if not os.path.exists(tmp_path):
                os.makedirs(tmp_path)
            with open(os.path.join(tmp_path, 'input_file.java'), 'w', encoding='utf-8') as f:
                f.write(test_deepseek_fix)
            output = call_coverage(work_dir, os.path.join(tmp_path, 'input_file.java'), output_folder, False)
            print(output)
            cov_test_deepseek_fix_focal_tgt = get_coverage(os.path.join(output_folder, f'{pid}-{test_id}t_cov_jacoco.xml'), value['focal_path_src'])

            # test_deepseek_enhance在focal_tgt下的覆盖率
            print(f"Evaluating test_deepseek_enhance under focal_tgt for {pid}:{test_id}")
            output_folder = os.path.join(output_dir, 'test_deepseek_enhance_focal_tgt')
            if not os.path.exists(tmp_path):
                os.makedirs(tmp_path)
            with open(os.path.join(tmp_path, 'input_file.java'), 'w', encoding='utf-8') as f:
                f.write(test_deepseek_enhance)
            output = call_coverage(work_dir, os.path.join(tmp_path, 'input_file.java'), output_folder, False)
            print(output)
            cov_test_deepseek_enhance_focal_tgt = get_coverage(os.path.join(output_folder, f'{pid}-{test_id}t_cov_jacoco.xml'), value['focal_path_src'])



            cov_file[test_id] = {'cov_test_deepseek_fix_focal_tgt': cov_test_deepseek_fix_focal_tgt, 'cov_test_deepseek_enhance_focal_tgt': cov_test_deepseek_enhance_focal_tgt}
        cov_res[file] = cov_file
        with open(os.path.join(output_dir, file.replace('verified_tuples', 'cov')), 'w', encoding='utf-8') as f:
            json.dump(cov_file, f, indent=2)
    # with open(os.path.join(output_dir, 'cov_overall.json'), 'w', encoding='utf-8') as f:
    #     json.dump(cov_res, f, indent=2)
