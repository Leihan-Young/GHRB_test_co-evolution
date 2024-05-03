import glob
import os
import html
import json
import datetime
import pandas as pd
import subprocess 
import shlex
import shutil
import argparse
import subprocess as sp
import javalang
import re
from time import sleep
from tqdm import tqdm
from bs4 import BeautifulSoup

from collections import defaultdict

import langid

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.exceptions import TransportQueryError

def checkout(repo_path, commit_id):
    p = sp.run(['git', 'reset', '--hard', 'HEAD'],
           cwd=repo_path, stdout=sp.PIPE, stderr=sp.PIPE)
    p = sp.run(['git', 'clean', '-df'],
           cwd=repo_path, stdout=sp.PIPE, stderr=sp.PIPE)
    p = sp.run(['git', 'checkout', commit_id], cwd=repo_path,
           stdout=sp.PIPE, stderr=sp.PIPE)

def get_method_nodes(repo_path, related_prod_file):
    try:
        with open(os.path.join(repo_path, related_prod_file), 'r', encoding='utf-8') as f:
            tree = javalang.parse.parse(f.read())
        if len(tree.children[2]) == 0:
            return []
        class_node = tree.children[2][0]
        method_nodes = []
        for node in class_node.body:
            if isinstance(node, javalang.tree.MethodDeclaration) or isinstance(node, javalang.tree.ConstructorDeclaration):
                method_nodes.append(node)
        return method_nodes
    except:
        return []

def get_invoked_methods(repo_path, test_path, test_method_name):
    try:
        with open(os.path.join(repo_path, test_path), 'r', encoding='utf-8') as f:
            tree = javalang.parse.parse(f.read())
        if len(tree.children[2]) == 0:
            return None
        class_node = tree.children[2][0]
        invoked_methods = set()
        method_node = None
        for node in class_node.body:
            if hasattr(node, 'name') and node.name == test_method_name:
                method_node = node
        if method_node == None:
            return None
        for path, node in method_node:
            if isinstance(node, javalang.tree.MethodInvocation):
                if node.member == 'fail' or node.member == 'verifyException' or 'assert' in node.member:
                    continue
                invoked_methods.add(node.member)
            if isinstance(node, javalang.tree.ClassCreator):
                invoked_methods.add(node.type.name)
        return invoked_methods
    except:
        return None

def parse_focal_method(repo_path, commit_src, commit_tgt, test_src, test_tgt, diff_name):
    changed_prod_files = []
    # changed_methods = {}
    if not os.path.exists(f'./collected/prod_diff/{diff_name}.diff'):
        print("No prod changed")
        return None, None, None
    with open(f'./collected/prod_diff/{diff_name}.diff', 'r', encoding='utf-8') as f:
        diff_lines = f.readlines()
    for i in range(len(diff_lines)):
        if i > 0 and diff_lines[i-1].startswith('--- a/') and diff_lines[i].startswith('+++ b/'):
            changed_prod_files.append(diff_lines[i][6:-1])

    test_path = test_src.split('#')[0]
    test_class_name = test_path.split('/')[-1].replace('.java', '')
    test_method_name = test_src.split('#')[1]

    related_prod_files = [f for f in changed_prod_files if f.split('/')[-1].replace('.java', '') in test_class_name]
    if len(related_prod_files) == 0:
        return None, None, None
    related_prod_files = [max(related_prod_files, key=len)]

    methods_tgt = {}
    checkout(repo_path, commit_tgt)
    for related_prod_file in related_prod_files:
        methods_tgt[related_prod_file] = get_method_nodes(repo_path, related_prod_file)
    methods_src = {}
    checkout(repo_path, commit_src)
    for related_prod_file in related_prod_files:
        methods_src[related_prod_file] = get_method_nodes(repo_path, related_prod_file)
    invoked_methods = get_invoked_methods(repo_path, test_path, test_method_name)
    
    changed_prod_methods = []
    for related_prod_file in related_prod_files:
        methods_src_list = methods_src[related_prod_file]
        methods_tgt_list = methods_tgt[related_prod_file]

        # delete duplicated methods
        dup_src = []
        dup_tgt = []
        for i in range(len(methods_src_list)):
            for j in range(len(methods_tgt_list)):
                if node_equal(methods_src_list[i], methods_tgt_list[j]):
                    dup_src.append(i)
                    dup_tgt.append(j)
                    break
        dup_src = reversed(sorted(dup_src))
        dup_tgt = reversed(sorted(dup_tgt))
        for ind in dup_src:
            methods_src_list.pop(ind)
        for ind in dup_tgt:
            methods_tgt_list.pop(ind)

        for method_src in methods_src_list:
            for method_tgt in methods_tgt_list:
                if method_src.name != method_tgt.name:
                    continue
                changed_prod_methods.append((related_prod_file, method_src, method_tgt))
    
    related_methods = []
    length = 0
    for related_prod_file, method_src, method_tgt in changed_prod_methods:
        if method_src.name.lower() in test_method_name.lower():
            if len(method_src.name) > length:
                related_methods = [(related_prod_file, method_src, method_tgt)]
                length = len(method_src.name)
    if len(related_methods) == 0 and invoked_methods != None:
        for related_prod_file, method_src, method_tgt in changed_prod_methods:
            if method_src.name in invoked_methods:
                related_methods.append((related_prod_file, method_src, method_tgt))
    if len(related_methods) > 0:
        # print("More than 1 related methods")
        focal_path = []
        focal_src = []
        focal_tgt = []
        for related_prod_file, method_src, method_tgt in related_methods:
            focal_path.append(f"{related_prod_file}#{method_src.name}")
            checkout(repo_path, commit_src)
            focal_src.append(''.join(extract_focal_code(repo_path, related_prod_file, method_src)))
            checkout(repo_path, commit_tgt)
            focal_tgt.append(''.join(extract_focal_code(repo_path, related_prod_file, method_tgt)))
        return focal_path, focal_src, focal_tgt
    # if len(related_methods) == 1:
    #     # extract focal_src & focal_tgt
    #     related_prod_file, method_src, method_tgt = related_methods[0]
    #     checkout(repo_path, commit_src)
    #     focal_src = extract_focal_code(repo_path, related_prod_file, method_src)
    #     checkout(repo_path, commit_tgt)
    #     focal_tgt = extract_focal_code(repo_path, related_prod_file, method_tgt)
    #     return [''.join(focal_src)], [''.join(focal_tgt)]
    return None, None, None

def extract_focal_code(repo_path, prod_file, method):
    java_file_path = os.path.join(repo_path, prod_file)
    method_name = method.name
    target_line_number = method.position.line
    with open(java_file_path, 'r', encoding='utf-8') as f:
        java_code = f.readlines()
    start = target_line_number
    while start >= 0:
        if java_code[start].find(method_name) != -1 and (java_code[start].find('public ') != -1 or java_code[start].find('private ') != -1 or java_code[start].find('protected ') != -1):
            break
        start = start - 1
    # 如果方法前有Annotations
    define_line = start
    while start > 0:
        start = start - 1
        if java_code[start].find('@') == -1:
            break
    start = start + 1
    # 寻找方法注释
    tmp = start
    while start >= 0:
        if java_code[start].find('/*') != -1:
            break
        elif re.match('\s*(})\s*', java_code[start]) or java_code[start].find(' class ') != -1 or java_code[start].find(' interface ') != -1:
            start = tmp
            break
        start = start - 1
    if start < 0:
        raise Exception("Error:" + method_name + " not found in " + java_file_path)
    # 找方法结尾
    end = define_line
    comment = False
    count = None
    end = end - 1
    while end + 1 < len(java_code) or count == None:
        end = end + 1
        if comment and java_code[end].find('*/') != -1:
            comment = False
            continue
        if java_code[end].find('/*') != -1 and java_code[end].find('*/') == -1 and java_code[end][:java_code[end].find('/*')].find('"') == -1 and java_code[end][:java_code[end].find('/*')].find('}') == -1:
            comment = True
            continue
        if countSymbol(java_code[end], ';') != 0 and count == None:
            break
        left_count = countSymbol(java_code[end], '{')
        right_count = countSymbol(java_code[end], '}')
        diff = left_count - right_count
        if count == None and diff != 0:
            count = diff
        elif count != None:
            count = count + diff
        if count != None and count <= 0:
            break
    if java_code[end].find('/*') != -1 and java_code[end][:java_code[end].find('/*')].find('"') == -1 and java_code[end][:java_code[end].find('/*')].find('}') == -1:
        java_code[end] = java_code[end][:java_code[end].find('}') + 1]
    end = end + 1
    if end >= len(java_code):
        raise Exception("Error:Unexpected error in extract_focal_code()")
    # 回退末尾不需要的内容
    if java_code[end].find('public ') != -1 or java_code[end].find('private ') != -1:
        end = end - 1
        while end > target_line_number and java_code[end].find('@') != -1:
            end = end - 1
        if java_code[end].find('*/') != -1:
            while end > target_line_number and java_code[end].find('/*') == -1:
                end = end - 1
    return java_code[start:end]

# 判断一行中symbol的数量，除去引号内以及单行注释
def countSymbol(line, symbol):
    count = 0
    string_flag = False
    char_flag = False
    for i in range(len(line)):
        if line[i] == '/' and i + 1 < len(line) and line[i+1] == '/' and not string_flag and not char_flag:
            break
        if line[i] == '"' and (i == 0 or line[i - 1] != '\\'):
            string_flag = not string_flag
        if line[i] == '\'' and (i == 0 or line[i - 1] != '\\') and not string_flag:
            char_flag = not char_flag
        if string_flag or char_flag:
            continue
        if line[i] == symbol:
            count = count + 1
    return count

# MethodDeclaration
def is_signature_equal(method1, method2):
    if method1.name != method2.name:
        return False
    if not node_equal(getattr(method1, 'return_type'), getattr(method2, 'return_type')):
        return False
    params1 = getattr(method1, 'parameters')
    params2 = getattr(method2, 'parameters')
    if len(params1) != len(params2):
        return False
    for i in range(len(params1)):
        param1 = params1[i]
        param2 = params2[i]
        for attr in param1.attrs:
            if attr == 'name':
                continue
            if not node_equal(getattr(param1, attr), getattr(param2, attr)):
                return False
    return True

def node_equal(node1, node2):
    if type(node1) != type(node2):
        return False
    if isinstance(node1, list):
        if len(node1) != len(node2):
            return False
        for i in range(len(node1)):
            if not node_equal(node1[i], node2[i]):
                return False
    elif isinstance(node1, javalang.tree.Node):
        for attr in node1.attrs:
            if attr == 'documentation':
                continue
            if not node_equal(getattr(node1, attr), getattr(node2, attr)):
                return False
    else:
        return node1 == node2
    return True

def extract_tuples_from_sample_info(sample_info, project_info):
    tuples = []
    test_src = sample_info['execution_result']['test_src']
    test_tgt = sample_info['execution_result']['test_tgt']
    for test in test_src:
        tuple = {}
        tuple['commit_src'] = sample_info['buggy_commit']
        tuple['commit_tgt'] = sample_info['merge_commit']
        tuple['changed_tests'] = sample_info['changed_tests']
        tuple['refer_PR'] = sample_info['bug_id']
        tuple['test_src'] = test
        class_name = test.split('#')[0]
        test_method_name = test.split('#')[1]
        related_test_tgt = []
        for t in test_tgt:
            if t.startswith(class_name):
                related_test_tgt.append(t)
        class_path = class_name.replace('.', '/')
        test_path = None
        for changed_test in sample_info['changed_tests']:
            if class_path in changed_test:
                test_path = changed_test
                break
        if test_path == None:
            continue
        tuple['test_tgt'] = filter_unchanged_tests(test_path, test, related_test_tgt, project_info['repo_path'], sample_info['buggy_commit'], sample_info['merge_commit'])
        focal_path, focal_src, focal_tgt = parse_focal_method(project_info['repo_path'], sample_info['buggy_commit'], 
                                                  sample_info['merge_commit'], f'{test_path}#{test_method_name}', 
                                                  related_test_tgt, sample_info['bug_id'])
        tuple['test_src_code'] = parse_test_src_code(project_info['repo_path'], sample_info['buggy_commit'], f'{test_path}#{test_method_name}')
        if focal_path == None or focal_src == None or focal_tgt == None:
            continue
        for i in range(len(focal_path)):
            tuple_copy = tuple.copy()
            tuple_copy['focal_path'] = focal_path[i]
            tuple_copy['focal_src'] = focal_src[i]
            tuple_copy['focal_tgt'] = focal_tgt[i]
            tuples.append(tuple_copy)
    return tuples

def parse_test_src_code(repo_path, commit, test):
    checkout(repo_path, commit)
    test_method_name = test.split('#')[-1]
    test_path = os.path.join(repo_path, test.split('#')[0])
    with open(test_path, 'r', encoding='utf-8') as f:
        root_node = javalang.parse.parse(f.read())
    test_node = None
    for path, node in root_node:
        if isinstance(node, javalang.tree.MethodDeclaration) and node.name == test_method_name:
            test_node = node
            break
    if test_node == None:
        return ""
    test_src_code = extract_focal_code(repo_path, test_path, test_node)
    return "".join(test_src_code)

def filter_unchanged_tests(test_path, test_src, test_tgt, repo_path, commit_src, commit_tgt):
    checkout(repo_path, commit_src)
    test_src_method_names = get_test_method_names(os.path.join(repo_path, test_path))
    checkout(repo_path, commit_tgt)
    test_tgt_method_names = get_test_method_names(os.path.join(repo_path, test_path))
    res = []
    for t in test_tgt:
        if t == test_src:
            res.append(t)
            continue
        t_name = t.split('#')[-1]
        if t_name not in test_src_method_names and t_name in test_tgt_method_names:
            res.append(t)
    return res

def get_test_method_names(file_path):
    res = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = javalang.parse.parse(f.read())
        for path, node in tree:
            if isinstance(node, javalang.tree.MethodDeclaration) and 'annotations' in node.attrs:
                for anno in getattr(node, 'annotations'):
                    if anno.name == 'Test':
                        res.append(node.name)
                        break
        return res
    except:
        return res

def extract_tuples_from_json(json_path, project_info):
    with open(json_path, 'r', encoding='utf-8') as f:
        unverified_samples = json.load(f)
    tuples = []
    for sample_id, sample_info in tqdm(unverified_samples.items()):
        # if sample_info['PR_number'] != 12158:
        #     continue
        tuples += extract_tuples_from_sample_info(sample_info, project_info)
    tuples_with_test_id = {}
    for i in range(len(tuples)):
        tuples[i]["test_id"] = i+1
        tuples_with_test_id[i+1] = tuples[i]
    return tuples_with_test_id

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--samples', type=str, help="The folder with unverified samples")
    args = parser.parse_args()

    sample_path = args.samples

    if not os.path.exists('verified'):
        os.mkdir('verified')

    with open('./project_id.json') as f:
        projects_info = json.load(f)

    for root, dirs, files in os.walk(sample_path):
        for file in files:
            if file.startswith("unverified_samples_") and file.endswith(".json"):
                output_name = file.replace("unverified_samples", "verified_tuples")
                project_name = file.split('_')[-1].replace(".json", "")
                # if os.path.exists(f"verified/{output_name}"):
                #     continue
                # if project_name not in ('rocketmq'):
                #     continue
                print(project_name)
                try:
                    tuples = extract_tuples_from_json(os.path.join(root, file), projects_info[project_name])
                except:
                    continue
                if len(tuples) == 0:
                    continue
                with open(f"verified/{output_name}", 'w', encoding='utf-8') as f:
                    json.dump(tuples, f, indent=2)
    

