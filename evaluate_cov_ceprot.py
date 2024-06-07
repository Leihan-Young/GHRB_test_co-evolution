import os
import json
import subprocess as sp
import xml.etree.ElementTree as ET
from cli import call_checkout, call_coverage

def get_coverage(cov_xml, focal_path):
    if not os.path.exists(cov_xml):
        return None
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
                        for counter in method_node.findall('counter'):
                            cov[counter.attrib['type']] = {'missed': counter.attrib['missed'], 'covered': counter.attrib['covered']}
                        break
    return cov

if __name__ == "__main__":
    data_path = './ceprot_gen'
    cli_path = r'./'
    output_dir = os.path.abspath('./output')
    tmp_path = os.path.abspath('./tmp')
    files = [name for name in os.listdir(data_path)
            if name.endswith('.json')]
    cov_res = {}
    for file in files:
        if file not in ('verified_tuples_apache_dubbo.json', 'verified_tuples_apache_rocketmq.json'):
            continue
        with open(os.path.join(data_path, file), 'r', encoding='utf-8') as f:
            data = json.load(f)
        pid = file.replace('.json', '').split('_')[-1]
        cov_file = {}
        for key, value in data.items():
            test_src = value['test_src_code']
            test_tgt = value['CEPROT_gen_test_tgt']
            test_id = value['test_id']
            work_dir = os.path.join(tmp_path, 'repos', pid, f'{test_id}s')
            if not os.path.exists(work_dir):
                os.makedirs(work_dir)
            if os.path.exists(os.path.join(output_dir, f'{pid}-{test_id}s_cov_jacoco.xml')):
                cov_src = get_coverage(os.path.join(output_dir, f'{pid}-{test_id}s_cov_jacoco.xml'), value['focal_path'])
                cov_tgt = get_coverage(os.path.join(output_dir, f'{pid}-{test_id}t_cov_jacoco.xml'), value['focal_path'])
                cov_file[test_id] = {'cov_src': cov_src, 'cov_tgt': cov_tgt}
                continue
            output = call_checkout(pid, f"{test_id}s", work_dir)
            print(output)
            with open(os.path.join(tmp_path, 'input_file.java'), 'w', encoding='utf-8') as f:
                f.write(test_src)
            output = call_coverage(work_dir, os.path.join(tmp_path, 'input_file.java'), output_dir, False)
            print(output)
            cov_src = get_coverage(os.path.join(output_dir, f'{pid}-{test_id}s_cov_jacoco.xml'), value['focal_path'])
            work_dir = os.path.join(tmp_path, 'repos', pid, f'{test_id}t')
            if not os.path.exists(work_dir):
                os.makedirs(work_dir)
            output = call_checkout(pid, f"{test_id}t", work_dir)
            print(output)
            with open(os.path.join(tmp_path, 'input_file.java'), 'w', encoding='utf-8') as f:
                f.write(test_src)
            output = call_coverage(work_dir, os.path.join(tmp_path, 'input_file.java'), output_dir, False)
            print(output)
            cov_tgt = get_coverage(os.path.join(output_dir, f'{pid}-{test_id}t_cov_jacoco.xml'), value['focal_path'])
            cov_file[test_id] = {'cov_src': cov_src, 'cov_tgt': cov_tgt}
        cov_res[file] = cov_file
    with open('./cov_res_ceprot.json', 'w', encoding='utf-8') as f:
        json.dump(cov_res, f, indent=2)