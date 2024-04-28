import os
import re
import glob
import json
from os import path
from collections import Counter
from tqdm import tqdm


import subprocess as sp
import javalang
import argparse
import shutil
import copy

import subprocess
import shlex
import enlighten
import pandas as pd
import sys


file_path = os.getcwd()

config = {
    'alibaba_fastjson': {
        'repo_path': file_path + '/repos/fastjson',
        'src_dir': 'src/main/java/',
        'test_prefix': 'src/test/java',
        'project_name': 'alibaba_fastjson',
        'project_id': 'fastjson'
    },
    'TheAlgorithms_Java': {
        'repo_path': file_path + '/repos/Java',
        'src_dir': 'src/main/java/',
        'test_prefix': 'src/test/java',
        'project_name': 'TheAlgorithms_Java',
        'project_id': 'Java'
    },
    'ReactiveX_RxJava': {
        'repo_path': file_path + '/repos/RxJava',
        'src_dir': 'src/main/java',
        'test_prefix': 'src/test/java',
        'project_name': 'ReactiveX_RxJava',
        'project_id': 'RxJava'
    },
    'LMAX-Exchange_disruptor': {
        'repo_path': file_path + '/repos/disruptor',
        'src_dir': 'src/main/java',
        'test_prefix': 'src/test/java',
        'project_name': 'LMAX-Exchange_disruptor',
        'project_id': 'disruptor'
    },
    'assertj_assertj': {
        'repo_path': file_path + '/repos/assertj',
        'src_dir': 'src/main/java',
        'test_prefix': 'src/test/java',
        'project_name': 'assertj_assertj',
        'project_id': 'assertj'
    },
    'checkstyle_checkstyle': {
        'repo_path': file_path + '/repos/checkstyle',
        'src_dir': 'src/main/java',
        'test_prefix': 'src/test/java',
        'project_name': 'checkstyle_checkstyle',
        'project_id': 'checkstyle'
    },
    'FasterXML_jackson-core': {
        'repo_path': file_path + '/repos/jackson-core',
        'src_dir': 'src/main/java',
        'test_prefix': 'src/test/java',
        'project_name': 'FasterXML_jackson-core',
        'project_id': 'jackson-core'
    },
    'FasterXML_jackson-databind': {
        'repo_path': file_path + '/repos/jackson-databind',
        'src_dir': 'src/main/java',
        'test_prefix': 'src/test/java',
        'project_name': 'FasterXML_jackson-databind',
        'project_id': 'jackson-databind'
    },
    'jhy_jsoup': {
        'repo_path': file_path + '/repos/jsoup',
        'src_dir': 'src/main/java',
        'test_prefix': 'src/test/java',
        'project_name': 'jhy_jsoup',
        'project_id': 'jsoup'
    },
    'mockito_mockito': {
        'repo_path': file_path + '/repos/mockito',
        'src_dir': 'src/main/java',
        'test_prefix': 'src/test/java',
        'project_name': 'mockito_mockito',
        'project_id': 'mockito'
    },
    'FasterXML_jackson-dataformat-xml': {
        'repo_path': file_path + '/repos/jackson-dataformat-xml',
        'src_dir': 'src/main/java',
        'test_prefix': 'src/test/java',
        'project_name': 'FasterXML_jackson-dataformat-xml',
        'project_id': 'jackson-dataformat-xml'
    },
    'google_gson': {
        'repo_path': file_path + '/repos/gson',
        'src_dir': 'gson/src/main/java',
        'test_prefix': 'gson/src/test/java',
        'project_name': 'google_gson',
        'project_id': 'gson'
    },
    'Hakky54_sslcontext-kickstart': {
        'repo_path': file_path + '/repos/sslcontext-kickstart/sslcontext-kickstart',
        'src_dir': 'sslcontext-kickstart/src/main/java',
        'test_prefix': 'src/test/java',
        'project_name': 'Hakky54_sslcontext-kickstart',
        'project_id': 'sslcontext-kickstart'
    },
    'google_closure-compiler': {
        'repo_path': file_path + '/repos/closure-compiler',
        'src_dir': 'src/com/google',
        'test_prefix': 'test/com/google',
        'project_name': 'google_closure-compiler',
        'project_id': 'closure-compiler'
    },
    'netty_netty': {
        'repo_path': file_path + '/repos/netty',
        'src_dir': 'handler/src',
        'test_prefix': 'handler/src/test',
        'project_name': 'netty_netty',
        'project_id': 'netty'
    },
    'apache_rocketmq': {
        'repo_path': file_path + '/repos/rocketmq',
        'src_dir': '',
        'test_prefix': '',
        'project_name': 'apache_rocketmq',
        'project_id': 'rocketmq'
    },
    'apache_dubbo': {
        'repo_path': file_path + '/repos/dubbo',
        'src_dir': '',
        'test_prefix': '',
        'project_name': 'apache_dubbo',
        'project_id': 'dubbo',
    },
    'iluwatar_java-design-patterns': {
        'repo_path': file_path + '/repos/java-design-patterns',
        'project_name': 'iluwatar_java-design-patterns',
    },
    'dbeaver_dbeaver': {
        'repo_path': file_path + '/repos/dbeaver',
        'project_name': 'dbeaver_dbeaver'
    },
    'seata_seata': {
        'repo_path': file_path + '/repos/seata',
        'project_name': 'seata_seata',
        'project_id': 'seata'
    },
    'OpenAPITools_openapi-generator': {
        'repo_path': file_path + '/repos/openapi-generator',
        'project_name': 'OpenAPITools_openapi-generator',
        'project_id': 'openapi-generator'
    },
    'apache_shardingsphere': {
        'repo_path': file_path + '/repos/shardingsphere',
        'project_name': 'apache_shardingsphere'
    },
    'alibaba_nacos': {
        'repo_path': file_path + '/repos/nacos',
        'project_name': 'alibaba_nacos',
        'project_id': 'nacos'
    },
    'keycloak_keycloak': {
        'repo_path': file_path + '/repos/keycloak',
        'project_name': 'keycloak_keycloak'
    },
    'redisson_redisson': {
        'repo_path': file_path + '/repos/redisson',
        'project_name': 'redisson_redisson'
    },
    'elastic_elasticsearch': {
        'repo_path': file_path + '/repos/elasticsearch',
        'project_name': 'elastic_elasticsearch'
    },
    'iBotPeaches_Apktool': {
        'repo_path': file_path + '/repos/Apktool',
        'project_name': 'iBotPeaches_Apktool',
        'project_id': 'Apktool'
    },
    'spring-projects_spring-framework': {
        'repo_path': file_path + '/repos/spring-framework',
        'project_name': 'spring-projects_spring-framework'
    },
    'square_retrofit': {
        'repo_path': file_path + '/repos/retrofit',
        'project_name': 'square_retrofit',
        'project_id': 'retrofit'
    },
    'javaparser_javaparser': {
        'repo_path': file_path + '/repos/javaparser',
        'project_name': 'javaparser_javaparser',
        'project_id': 'javaparser'
    },
    'apache_incubator-seata': {
        'repo_path': file_path + '/repos/incubator-seata',
        'project_name': 'apache_incubator-seata',
        'project_id': 'incubator-seata'
    },
    'apache_skywalking': {
        'repo_path': file_path + '/repos/skywalking',
        'project_name': 'apache_skywalking',
        'project_id': 'skywalking'
    },
    'JodaOrg_joda-time': {
        'repo_path': file_path + '/repos/joda-time',
        'project_name': 'JodaOrg_joda-time',
        'project_id': 'joda-time',
        'src_dir': 'src/main/java',
        'test_prefix': 'src/test/java'
    }
    }

license_sslcontext_kickstart = '''
/*
 * Copyright 2019-2022 the original author or authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
'''


properties_to_replace = {
    'jackson-core': {
        r'<javac.src.version>\s*1.6\s*</javac.src.version>': '',
        r'<javac.target.version>\s*1.6\s*</javac.target.version>': '',
        r'<maven.compiler.source>\s*1.6\s*</maven.compiler.source>': '<maven.compiler.source>11</maven.compiler.source>',
        r'<maven.compiler.target>\s*1.6\s*</maven.compiler.target>': '<maven.compiler.target>11</maven.compiler.target>',
    },
    'jackson-databind': {
        r'<version>\s*2.13.0-rc1-SNAPSHOT\s*</version>': '<version>2.14.0-SNAPSHOT</version>',
        r'<source>\s*14\s*</source>': '<source>17</source>',
        r'<release>\s*14\s*</release>': '<release>17</release>',
        r'<id>\s*java17\+\s*</id>': '<id>java17+</id>',
        r'<jdk>\s*\[17\,\)\s*</jdk>': '<jdk>[17,)</jdk>'
    }
}

def split_project_bug_id(bug_key):
    s = bug_key.split('_')
    project = '_'.join(s[:-1])
    bug_id = s[-1]

    return project, bug_id


def fix_build_env(repo_dir_path):
    if 'jackson-core' in repo_dir_path or 'jackson-databind' in repo_dir_path:
        pom_file = os.path.join(repo_dir_path, 'pom.xml')

        with open(pom_file, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'jackson-core' in repo_dir_path:
            replace_map = properties_to_replace['jackson-core']
        elif 'jackson-databind' in repo_dir_path:
            replace_map = properties_to_replace['jackson-databind']

        for unsupported_property in replace_map:
            content = re.sub(
                unsupported_property, replace_map[unsupported_property], content)

        with open(pom_file, 'w') as f:
            f.write(content)

def pit(it, *pargs, **nargs):
    # https://stackoverflow.com/questions/23113494/double-progress-bar-in-python

    global __pit_man__
    try:
        __pit_man__
    except NameError:
        __pit_man__ = enlighten.get_manager()
    man = __pit_man__
    try:
        it_len = len(it)
    except:
        it_len = None
    try:
        ctr = None
        for i, e in enumerate(it):
            if i == 0:
                ctr = man.counter(
                    *pargs, **{**dict(leave=False, total=it_len), **nargs})
            yield e
            ctr.update()
    finally:
        if ctr is not None:
            ctr.close()

DEBUG = True

def get_project_from_bug_id(bug_id):
    for project_identifier in config:
        if project_identifier in bug_id:
            return project_identifier
        
def get_project_id_from_project(project):
    return config[project]['project_id']
        
def find_env (pid):
    with open("./project_id.json", "r") as f:
        project_id = json.load(f)

    if pid not in project_id.keys():
        output = "No matching project id"
        return output

    requirements = project_id[pid]["requirements"]
    if len(requirements["extra"]) != 0:
        extra = requirements["extra"]
    
    build = requirements["build"]
    jdk_required = requirements["jdk"]
    wrapper = requirements["wrapper"]

    mvn_required = None
    mvnw = False
    gradlew = False

    if build == "maven":
        if wrapper:
            mvnw = True
        else:
            mvn_required = requirements["version"]
    elif build == "gradle":
        if wrapper:
            gradlew = True

    JAVA_HOME = mvn_path = None
    if jdk_required == '8':
        JAVA_HOME = r'/Java/jdk-1.8'
    elif jdk_required == '11':
        JAVA_HOME = r'/Java/jdk-11'
    elif jdk_required == '17':
        JAVA_HOME = r'/Java/jdk-17'
    
    if mvn_required is None:
        mvn_path = ""
    elif mvn_required == '3.8.6':
        mvn_path = r'/Maven/apache-maven-3.8.6/bin'
    elif mvn_required == '3.8.1':
        mvn_path = r'/Maven/apache-maven-3.8.1/bin'

    new_env = os.environ.copy()
    new_env['JAVA_HOME'] = JAVA_HOME
    new_env['MAVEN_HOME'] = mvn_path
    if JAVA_HOME is not None:
        new_env['PATH'] = os.pathsep.join([f'{JAVA_HOME}/bin', new_env['PATH']])

    return new_env, mvnw, gradlew


def run_test (new_env, mvnw, gradlew, test_case, path, command=None):

    if not mvnw and not gradlew:
        # default = ['timeout', '30m', 'mvn', 'test', f'-Dtest={test_case}', '-DfailIfNoTests=false', '--errors']
        default = [os.path.join(new_env['MAVEN_HOME'], 'mvn'), 'test', f'-Dtest={test_case}', '-DfailIfNoTests=false', '--errors']
        if command is not None:
            extra_command = command.split()
            new_command = default + extra_command
            run = sp.run(new_command,
                         env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path, shell=True)
        else:
            # run = sp.run([os.path.join(new_env['MAVEN_HOME'], 'mvn'), '-v'],
            #             env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path, shell=True)
            run = sp.run(default,
                        env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path, shell=True)

    elif mvnw:
        # default = ['timeout', '10m', './mvnw', 'test', f'-Dtest={test_case}', '-DfailIfNoTests=false', '--errors']
        default = ['.\mvnw', 'test', f'-Dtest={test_case}', '-DfailIfNoTests=false', '--errors']
        if command is not None:
            extra_command = command.split()
            new_command = default + extra_command

            run = sp.run(new_command,
                        env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path, shell=True)
        else:
            run = sp.run(default,
                        env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path, shell=True)
    elif gradlew:
        default = [".\gradlew", "test", "--tests", f'{test_case}', '--info', '--stacktrace']
        if command is not None:
            if 'test' in command:
                new_command = [".\gradlew", command, '--tests', f'{test_case}']
                run = sp.run(new_command,
                             env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path, shell=True)
            else:
                run = sp.run(new_command,
                             env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path, shell=True)
        else:
            run = sp.run(default,
                         env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path, shell=True)
    
    stdout = run.stdout.decode(encoding='gbk', errors='ignore')
    stderr = run.stderr.decode(encoding='gbk', errors='ignore')

    return stdout, stderr
            
def verify_in_buggy_version(buggy_commit, test_patch_dir, repo_path, test_prefix, build, pid):

    print(repo_path, buggy_commit, test_patch_dir)
    p = sp.run(['git', 'reset', '--hard', 'HEAD'],
           cwd=repo_path, stdout=sp.PIPE, stderr=sp.PIPE)
    
    print(p.stdout.decode())
    
    p = sp.run(['git', 'clean', '-df'],
           cwd=repo_path, stdout=sp.PIPE, stderr=sp.PIPE)

    print(p.stdout.decode())
    # checkout to the buggy version and apply patch to the buggy version
    p = sp.run(['git', 'checkout', buggy_commit], cwd=repo_path,
           stdout=sp.PIPE, stderr=sp.PIPE)
    print(p.stderr.decode())

    p = sp.run(['git', 'apply', test_patch_dir], cwd=repo_path,
           stdout=sp.PIPE, stderr=sp.PIPE)
    
    print(p.stdout.decode())

    p = sp.run(['git', 'status'], cwd=repo_path,
               stdout=sp.PIPE, stderr=sp.PIPE)
    
    print(p.stdout.decode())
    

    changed_test_files = [p.strip().split()[-1] for p in p.stdout.decode(
        'utf-8').split('\n') if p.strip().endswith('.java')]
    if len(changed_test_files) == 0:
        p = sp.run(['git', 'status', '-u'], cwd=repo_path, stdout=sp.PIPE, stderr=sp.PIPE)
        changed_test_files = [p.strip().split()[-1] for p in p.stdout.decode(
        'utf-8').split('\n') if p.strip().endswith('.java')]

    
    print("changed_test_files: ", changed_test_files)

    new_env, mvnw, gradlew = find_env(pid)
    
    with open("./project_id.json", "r") as f:
        project_id = json.load(f)
    
    if len(project_id[pid]['requirements']['extra']) != 0:
        command = project_id[pid]['requirements']['extra']['command']
    else:
        command = None

    fix_build_env(repo_path)
    
    modules = []

    def replace_index (x):
        test_dir = x.split('/')
        
        index = test_dir.index('src')
        test_dir = ".".join(test_dir[index+3:])
        test_dir = "." + test_dir
        return test_dir

    def find_repo_path (x):
        test_dir = x.split('/')
        repo = test_dir[0]
        return repo
    

    changed_test_id = list(map(lambda x: replace_index(x), changed_test_files))
    #print("changed_test_id_before: ", changed_test_id)
    if build == 'gradle':
        for i in range(len(changed_test_files)):

            changed_test_id[i] = changed_test_id[i][1:]
            changed_test_id[i] = changed_test_id[i][:-5] ## change to replace

    print("changed_test_id: ", changed_test_id)
    valid_tests = []
    for idx, test_id in enumerate(changed_test_id):

        captured_stdout, captured_stderr = run_test (new_env, mvnw, gradlew, test_id, repo_path, command)

        #print(captured_stdout)
        if 'There are test failures' in captured_stdout:
            print("There are test failures")
            valid_tests.append(test_id)
        elif 'There were failing tests' in captured_stderr:
            print("There were failing tests")
            valid_tests.append(test_id)
        

    specified_repo_path = None

    return valid_tests, repo_path, modules


def verify_in_fixed_version(fixed_commit, target_test_classes, repo_path, test_prefix, build, modules, pid):
    
    sp.run(['git', 'reset', '--hard', 'HEAD'],
           cwd=repo_path, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    sp.run(['git', 'clean', '-df'],
           cwd=repo_path, stdout=sp.DEVNULL, stderr=sp.DEVNULL)

    sp.run(['git', 'checkout', fixed_commit], cwd=repo_path)


    new_env, mvnw, gradlew = find_env(pid)
    
    with open("/root/framework/data/project_id.json", "r") as f:
        project_id = json.load(f)
    
    if len(project_id[pid]['requirements']['extra']) != 0:
        command = project_id[pid]['requirements']['extra']['command']
    else:
        command = None

    fix_build_env(repo_path)

    valid_tests = []

    print("target_test_classes: ", target_test_classes)
    for idx, test_id in enumerate(target_test_classes):

        captured_stdout, captured_stderr = run_test (new_env, mvnw, gradlew, test_id, repo_path, command)

        if 'BUILD SUCCESS' in captured_stdout:
            print("Maven build success")
            valid_tests.append(test_id)
        elif 'BUILD SUCCESSFUL' in captured_stdout:
            print("Gradle build success")
            valid_tests.append(test_id)
        elif 'There are test failures' in captured_stdout or 'There were failing tests' in captured_stdout:
            print("Test failed in fixed version")

    return valid_tests

def is_jackson_repos(name):
    return name in ('jackson-dataformat-xml', 'jackson-core', 'jackson-databind')

def get_compilable_tests(bug_id, buggy_commit, fixed_commit, build='maven'):
    project = get_project_from_bug_id(bug_id)
    repo_path = config[project]['repo_path']

    # src_dir = config[project]['src_dir']
    # test_prefix = config[project]['test_prefix']
    test_prefix = None
    valid_tests = 0
    success_tests = 0
    # print(bug_id)
    test_patch_dir = os.path.abspath(os.path.join(
        './collected/test_diff', f'{bug_id}.diff'))
    
    pid = get_project_id_from_project (project)

    test_trees_in_buggy_version, specified_repo_path = verify_compile(buggy_commit, test_patch_dir, repo_path, test_prefix, build, pid)

    test_trees_in_fixed_version, specified_repo_path = verify_compile(fixed_commit, test_patch_dir, repo_path, test_prefix, build, pid)

    # 除了@Test之外部分有修改则不加入数据集
    tests_src = []
    tests_tgt = []
    for (test_id_buggy, tree_buggy) in test_trees_in_buggy_version:
        for (test_id_fixed, tree_fixed) in test_trees_in_fixed_version:
            if test_id_buggy == test_id_fixed:
                context_modified, modified_methods = verify_context_modified(tree_buggy, tree_fixed, is_jackson_repos(pid))
                if context_modified:
                    continue
                (tests_in_buggy_version, tests_in_fixed_version) = modified_methods
                for node in tests_in_buggy_version:
                    tests_src.append(f"{test_id_buggy[:-5]}#{node.name}")
                for node in tests_in_fixed_version:
                    tests_tgt.append(f"{test_id_fixed[:-5]}#{node.name}")

    # print("tests_in_buggy_version: ", tests_in_buggy_version, "tests_in_fixed_version: ", tests_in_fixed_version)
    return tests_src, tests_tgt

def verify_context_modified(tree_buggy, tree_fixed, jackson_repos=False):
    # 不考虑Import和package
    if len(tree_buggy.children[2]) == 0:
        return True, None
    class_node_buggy = tree_buggy.children[2][0]
    class_node_fixed = tree_fixed.children[2][0]
    nodes_buggy = []
    test_methods_buggy = []
    for node in class_node_buggy.body:
        if isinstance(node, javalang.tree.MethodDeclaration) and 'annotations' in node.attrs:
            flag = False
            for anno in getattr(node, 'annotations'):
                if anno.name == 'Test':
                    flag = True
                    break
            if flag or (jackson_repos and node.name.startswith("test")):
                test_methods_buggy.append(node)
                continue
        nodes_buggy.append(node)
    nodes_fixed = []
    test_methods_fixed = []
    for node in class_node_fixed.body:
        if isinstance(node, javalang.tree.MethodDeclaration) and 'annotations' in node.attrs:
            flag = False
            for anno in getattr(node, 'annotations'):
                if anno.name == 'Test':
                    flag = True
                    break
            if flag or (jackson_repos and node.name.startswith("test")):
                test_methods_fixed.append(node)
                continue
        nodes_fixed.append(node)
    if not context_equal(nodes_buggy, nodes_fixed):
        return True, None
    
    # 加入以下methods
    # test_src中有，但test_tgt中没有的（根据node.name判断）
    # test_src和test_tgt中都有，但是二者不同的
    test_methods_src = []
    for node_buggy in test_methods_buggy:
        found = False
        for node_fixed in test_methods_fixed:
            if node_buggy.name == node_fixed.name:
                found = True
                if not context_equal(node_buggy, node_fixed):
                    test_methods_src.append(node_buggy)
                break
        if not found:
            test_methods_src.append(node_buggy)

    test_methods_tgt = []
    for node_fixed in test_methods_fixed:
        found = False
        for node_buggy in test_methods_buggy:
            if node_buggy.name == node_fixed.name:
                found = True
                if not context_equal(node_buggy, node_fixed):
                    test_methods_tgt.append(node_fixed)
                break
        if not found:
            test_methods_tgt.append(node_fixed)

    return False, (test_methods_src, test_methods_tgt)


def context_equal(node1, node2):
    if type(node1) != type(node2):
        return False
    if isinstance(node1, list):
        if len(node1) != len(node2):
            return False
        for i in range(len(node1)):
            if not context_equal(node1[i], node2[i]):
                return False
    elif isinstance(node1, javalang.tree.Node):
        for attr in node1.attrs:
            if attr == 'documentation' or attr == 'annotations':
                continue
            if not context_equal(getattr(node1, attr), getattr(node2, attr)):
                return False
    else:
        return node1 == node2
    return True

def verify_compile(commit, test_patch_dir, repo_path, test_prefix, build, pid):

    # print(repo_path, commit)
    p = sp.run(['git', 'reset', '--hard', 'HEAD'],
           cwd=repo_path, stdout=sp.PIPE, stderr=sp.PIPE)
    
    # print(p.stdout.decode())
    
    p = sp.run(['git', 'clean', '-df'],
           cwd=repo_path, stdout=sp.PIPE, stderr=sp.PIPE)

    # print(p.stdout.decode())
    # checkout to the buggy version and apply patch to the buggy version
    p = sp.run(['git', 'checkout', commit], cwd=repo_path,
           stdout=sp.PIPE, stderr=sp.PIPE)
    # print(p.stderr.decode())
    

    changed_test_files = get_changed_test_files(test_patch_dir)
    # print("changed_test_files: ", changed_test_files)

    new_env, mvnw, gradlew = find_env(pid)
    
    with open("./project_id.json", "r") as f:
        project_id = json.load(f)
    
    if len(project_id[pid]['requirements']['extra']) != 0:
        command = project_id[pid]['requirements']['extra']['command']
    else:
        command = None

    fix_build_env(repo_path)

    def replace_index (x):
        test_dir = x.split('/')
        
        index = test_dir.index('src')
        test_dir = ".".join(test_dir[index+3:])
        test_dir = "." + test_dir
        return test_dir

    def find_repo_path (x):
        test_dir = x.split('/')
        repo = test_dir[0]
        return repo
    

    changed_test_id = list(map(lambda x: replace_index(x), changed_test_files))
    # print("changed_test_id_before: ", changed_test_id)
    if build == 'gradle':
        for i in range(len(changed_test_files)):

            changed_test_id[i] = changed_test_id[i][1:]
            changed_test_id[i] = changed_test_id[i][:-5] ## change to replace

    print("changed_test_id: ", changed_test_id)
    valid_tests = []
    try:
        captured_stdout, captured_stderr = run_test (new_env, mvnw, gradlew, ','.join(changed_test_id), repo_path, command)
        valid_tests += changed_test_id
    except Exception as e:
        for idx, test_id in enumerate(changed_test_id):

            captured_stdout, captured_stderr = run_test (new_env, mvnw, gradlew, test_id, repo_path, command)

            #print(captured_stdout)
            if 'BUILD SUCCESS' in captured_stdout:
                print(f"{test_id}:BUILD SUCCESS")
                valid_tests.append(test_id)
    
    print("valid_tests: ", valid_tests)

    test_tree = []
    for valid_test in valid_tests:
        for file in changed_test_files:
            if valid_test[:-5].replace('.', '/') in file:
                if not os.path.exists(os.path.join(repo_path, file)):
                    continue
                with open(os.path.join(repo_path, file), 'r', encoding='utf-8') as f:
                    try:
                        tree = javalang.parse.parse(f.read())
                    except javalang.parser.JavaSyntaxError as e:
                        print(f"{valid_test}:JavaSyntaxError")
                        continue
                test_tree.append((valid_test, tree))

    return test_tree, repo_path

def parse_test_methods(tree, test_id):
    body = tree.children[2][0].body
    prefix = test_id[:-5]
    methods = []
    for dec in body:
        if isinstance(dec, javalang.tree.MethodDeclaration):
            flag = False
            for anno in dec.annotations:
                if anno.name == 'Test':
                    flag = True
                    break
            if not flag:
                continue
            methods.append((f'{prefix}::{dec.name}', dec))
    return methods

def get_changed_test_files(test_patch):
    with open(test_patch, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    lines = [l[:-1] if l.endswith('\n') else l for l in lines]
    changed_tests = []
    for i in range(len(lines)):
        if lines[i].startswith('+++ b'):
            file = lines[i][6:]
            if file.endswith('.java'):
                changed_tests.append(lines[i][6:])
    return changed_tests

def verify_bug(bug_id, buggy_commit, fixed_commit, build='maven'):
    project = get_project_from_bug_id(bug_id)
    repo_path = config[project]['repo_path']

    # src_dir = config[project]['src_dir']
    # test_prefix = config[project]['test_prefix']
    test_prefix = None
    valid_tests = 0
    success_tests = 0
    print(bug_id)
    test_patch_dir = os.path.abspath(os.path.join(
        './collected/test_diff', f'{bug_id}.diff'))
    
    pid = get_project_id_from_project (project)

    valid_tests, specified_repo_path, modules = verify_in_buggy_version(
        buggy_commit, test_patch_dir, repo_path, test_prefix, build, pid)

    success_tests = verify_in_fixed_version(
        fixed_commit, valid_tests, specified_repo_path, test_prefix, build, modules, pid)

    print("valid: ", valid_tests, "success: ", success_tests)
    return valid_tests, success_tests

def fetch_test_diff (report_map):

    new_cleaned_data = {}

    repo_path = ""
    if not os.path.isdir("collected/test_diff"):
        os.makedirs("collected/test_diff")

    for repo_name in report_map:
        
        new_cleaned_data[repo_name] = {}

        owner, name = repo_name.split("_")

        link = "https://github.com/" + owner + "/" + name
        repo_path = os.getcwd() + '/repos/' + name
        p = subprocess.Popen(['git', 'clone', link, repo_path], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        

        for bug_id, bug_info in report_map[repo_name].items():
            merge_commit = bug_info['merge_commit']
            buggy_commits = [c['oid'] for c in bug_info['buggy_commits']]

            if len(bug_info['changed_tests']) != 0:
                test_dir = bug_info['changed_tests'][0]
                test_dir = test_dir.split('/')
                if 'test' in test_dir:
                    index = test_dir.index('test')
                    test_dir = "/".join(test_dir[:index+2])
                else:
                    test_dir = 'src/test/java'

            selected_buggy_commit = None
            diff = None

            # get diff using buggy commit and fixed commit
            for buggy_commit in buggy_commits:
                p = subprocess.run(shlex.split(f'git diff {buggy_commit} {merge_commit} -- {test_dir}')
                                   , stdout=subprocess.PIPE, stderr=subprocess.PIPE
                                   , cwd=repo_path)
                

                diff = p.stdout.decode()
                error_msg = p.stderr.decode()


                if len(error_msg) > 0:
                    if merge_commit in error_msg:
                        p = subprocess.run(shlex.split(f'git fetch origin {merge_commit}'), 
                                           stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                           cwd=repo_path)
                    elif buggy_commit in error_msg:
                        p = subprocess.run(shlex.split(f'git fetch origin {buggy_commit}'),
                                           stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                           cwd=repo_path)
                    
                    p = subprocess.run(shlex.split(f'git diff {buggy_commit} {merge_commit} -- {test_dir}'),
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       cwd=repo_path)

                    diff = p.stdout.decode()
                    error_msg = p.stderr.decode()


                if len(diff.strip()) > 0 and len(error_msg) == 0:
                    selected_buggy_commit = buggy_commit
                    break

            if selected_buggy_commit is None:
                print(f'Failed to find test suite for {bug_id}')
                continue
            else:
                new_cleaned_data[repo_name][bug_id] = bug_info
            
            with open('collected/test_diff/{}.diff'.format(bug_info['bug_id']), 'w', encoding='utf-8') as f:
                f.write(diff)
            

def fetch_prod_diff (report_map):
    
    if not os.path.isdir("collected/prod_diff"):
        os.makedirs("collected/prod_diff")
    
    for repo_name in report_map:

        owner, name = repo_name.split("_")

        repo_path = os.getcwd() + '/repos/' + name


        for bug_id, bug_info in report_map[repo_name].items():
            if bug_id == "apache_rocketmq-5193":
                print(1)
            
            merge_commit = bug_info['merge_commit']
            buggy_commits = [c['oid'] for c in bug_info['buggy_commits']]

            if len(bug_info['changed_tests']) != 0:
                test_dir = bug_info['changed_tests'][0]
                test_dir = test_dir.split('/')
                if 'test' in test_dir:
                    index = test_dir.index('test')
                    test_dir = "/".join(test_dir[:index+2])
                else:
                    test_dir = 'src/test/java'

            selected_buggy_commit = None
            diff = None

            for buggy_commit in buggy_commits:
                
                p = subprocess.run(shlex.split(f"git diff {buggy_commit} {merge_commit} -- '*.java' ':!{test_dir}/*' ':!*/test/*'")
                                , stdout=subprocess.PIPE, stderr=subprocess.PIPE
                                , cwd=repo_path)
                

                diff = p.stdout.decode()
                error_msg = p.stderr.decode()

                if len(error_msg) > 0:
                    if merge_commit in error_msg:
                        p = subprocess.run(shlex.split(f'git fetch origin {merge_commit}'), 
                                           stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                           cwd=repo_path)
                    elif buggy_commit in error_msg:
                        p = subprocess.run(shlex.split(f'git fetch origin {buggy_commit}'),
                                           stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                           cwd=repo_path)
                    
                    p = subprocess.run(shlex.split(f"git diff {buggy_commit} {merge_commit} -- '*.java' ':!{test_dir}/*' ':!*/test/*'"),
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       cwd=repo_path)

                    diff = p.stdout.decode()
                    error_msg = p.stderr.decode()


                if len(diff.strip()) > 0 and len(error_msg) == 0:
                    selected_buggy_commit = buggy_commit
                    break

            if selected_buggy_commit is None:
                print(f'Failed to find prod diff for {bug_id}')
                continue
            
            with open('collected/prod_diff/{}.diff'.format(bug_id), 'w', encoding='utf-8') as f:
                f.write(diff)

def verify_test_exist(diff_id):
    # 是否有修改前后的test，如果只有t或t'则返回False
    with open('collected/test_diff/{}.diff'.format(diff_id), 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for i in range(len(lines)):
        if lines[i].startswith('--- a'):
            if not lines[i+1].startswith('+++ b'):
                continue
            if lines[i][5:] == lines[i+1][5:]:
                return True
    return False

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--file', default="report.json")
    args = parser.parse_args()

    if not os.path.isdir("unverified"):
        os.makedirs("unverified")

    with open(args.file, 'r', encoding='utf-8') as f:
        report_test_mappings = json.load(f)

    # fetch_test_diff(report_test_mappings)
    fetch_prod_diff(report_test_mappings)

    projects = report_test_mappings.keys()

    file_names = []

    for repo_name in projects:
        print(repo_name)

        file_name = f"unverified/unverified_samples_{repo_name}.json"        
        if os.path.exists(file_name):
            continue

        dataset = report_test_mappings[repo_name]
        report = copy.deepcopy(report_test_mappings[repo_name])
        
        temp_save = f"unverified/temp_save_report_{repo_name}.json"
        start_id = None
        if os.path.exists(temp_save):
            with open(temp_save, 'r', encoding='utf-8') as f:
                report_saved = json.load(f)
            for bug_id, bug_info in report_saved.items():
                if 'execution_result' in bug_info.keys():
                    report[bug_id] = bug_info
                    start_id = bug_id

        for bug_id in tqdm(dataset):

            if start_id != None:
                if start_id == bug_id:
                    start_id = None
                continue

            buggy_commit = report_test_mappings[repo_name][bug_id]['buggy_commit']
            fixed_commit = report_test_mappings[repo_name][bug_id]['merge_commit']


            if not verify_test_exist(bug_id):
                continue

            test_src, test_tgt = get_compilable_tests(bug_id, buggy_commit, fixed_commit)


            if test_src == None or test_tgt == None:
                continue

            report[bug_id]['execution_result'] = {
                'test_src': test_src,
                'test_tgt': test_tgt,
            }

    
        verified_samples = {}

        for bug_id, bug_info in report.items():
            if 'execution_result' in bug_info.keys() and len(bug_info['execution_result']['test_src']) > 0:
                verified_samples[bug_id] = bug_info

        #print("total bugs: ", len(verified_bugs))

        # file_name = f"unverified/unverified_samples_{repo_name}.json"

        if len(verified_samples) > 0:
            with open(file_name, 'w') as f:
                json.dump(verified_samples, f, indent=2)
            
            file_names.append(file_name)
    
    # # Remove redundant diff files
            
    # cur_dir = os.getcwd()

    # bug_names = []

    # for file_name in file_names:
        
    #     with open(file_name, "r") as f:
    #         bug_list = json.load(f)

    #     bug_names += bug_list.keys()

    # all_diff_list = os.listdir(cur_dir + "/collected/test_diff")

    # collected_test_diff = cur_dir + "/collected/test_diff"
    # collected_prod_diff = cur_dir + "/collected/prod_diff"

    # data_test_diff = cur_dir + "/data/test_diff"
    # data_prod_diff = cur_dir + "/data/prod_diff"

    # for bug in bug_names:
    #     shutil.move(f"{cur_dir}/collected/test_diff/{bug}.diff", f"{cur_dir}/data/test_diff/{bug}.diff")
    #     if os.path.isfile(f"{cur_dir}/collected/prod_diff/{bug}.diff"):
    #         shutil.move(f"{cur_dir}/collected/prod_diff/{bug}.diff", f"{cur_dir}/data/prod_diff/{bug}.diff")

    # subprocess.run(["rm", "-rf", f"{cur_dir}/collected"])

    # ### Auto - Verify

    # unverified_bugs = []

    # for bug_name in bug_names:
    #     bug_number = bug_name.split("-")[-1]
    #     owner_name = bug_name.replace("-" + bug_number, "")

    #     with open(f"verified_bug/verified_bugs_{owner_name}.json", "r") as f:
    #         v_b = json.load(f)
        
    #     with open(f"unverified/unverified_bugs_{owner_name}.json", "r") as ff:
    #         n_v_b = json.load(ff)
        
    #     if bug_name not in v_b.keys():
    #         unverified_bugs.append(bug_name)
        
    #     v_b[bug_name] = n_v_b[bug_name]

    #     with open(f"verified_bug/verified_bugs_{owner_name}.json", "w") as f:
    #         json.dump(v_b, f, indent=2)
        
    
    # subprocess.run([sys.executable, "debug/collector.py"], stdout=subprocess.PIPE)

    # with open("/root/framework/data/project_id.json", "r") as f:
    #     project_id = json.load(f)
    
    # wrong_bugs = []

    # for bug_name in bug_names:
    #     name_number = bug_name.split("_")[1]
    #     bug_number = name_number.split("-")[-1]
    #     pid = name_number.replace("-" + bug_number, "")

    #     commit_db = project_id[pid]["commit_db"]
    #     commit_db = pd.read_csv(commit_db)

    #     bug_id = commit_db.loc[commit_db['report.id'] == bug_name]["bug_id"].values[0]

    #     delete_testing = shlex.split("rm -rf testing")
    #     subprocess.run(delete_testing)
    #     checkout = shlex.split(f"{sys.executable} cli.py checkout -p {pid} -v {bug_id}b -w /root/framework/testing")
    #     subprocess.run(checkout, stdout=subprocess.PIPE)
    #     compil = shlex.split(f"{sys.executable} cli.py compile -w /root/framework/testing")
    #     compile_err = subprocess.run(compil, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    #     compile_err = compile_err.stderr.decode()
    #     if len(compile_err) > 0:
    #         print("compile error")
    #         wrong_bugs.append(bug_name)
    #         continue

    #     test = shlex.split(f"{sys.executable} cli.py test -w /root/framework/testing -q")
    #     test_output = subprocess.run(test, stdout=subprocess.PIPE)

    #     test_output = test_output.stdout.decode()

    #     if test_output.find("Failure") == -1:
    #          print("no failure for buggy version")
    #          wrong_bugs.append(bug_name)
    #          continue

    #     subprocess.run(delete_testing)
    #     checkout = shlex.split(f"{sys.executable} cli.py checkout -p {pid} -v {bug_id}f -w /root/framework/testing")
    #     subprocess.run(checkout, stdout=subprocess.PIPE)
    #     compil = shlex.split(f"{sys.executable} cli.py compile -w /root/framework/testing")
    #     compile_err = subprocess.run(compil, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    #     compile_err = compile_err.stderr.decode()
        
    #     if len(compile_err) > 0:
    #         print("compile error")
    #         wrong_bugs.append(bug_name)
    #         continue
        
    #     test = shlex.split(f"{sys.executable} cli.py test -w /root/framework/testing -q")
    #     test_output = subprocess.run(test, stdout=subprocess.PIPE)
    #     test_output = test_output.stdout.decode()
    #     if test_output.find("Failure") != -1:
    #         print("failure for fixed version")
    #         wrong_bugs.append(bug_name)
    #         continue

    # for wb in wrong_bugs:
    #     print("wrong bug: ", wb)

    # if len(wrong_bugs) == 0:
    #     print("no wrong bug")

    # for wrong_bug in wrong_bugs:
    #     bug_number = wrong_bug.split("-")[-1]
    #     owner_name = wrong_bug.replace("-" + bug_number, "")

    #     with open(f"unverified/unverified_bugs_{owner_name}.json", "r") as f:
    #         v_b = json.load(f)
        
    #     del v_b[wrong_bug]

    #     with open(f"unverified/unverified_bugs_{owner_name}.json", "w") as f:
    #         json.dump(v_b, f, indent=2)
    

    # for bug_name in unverified_bugs:
    #     bug_number = bug_name.split("-")[-1]
    #     owner_name = bug_name.replace("-" + bug_number, "")

    #     with open(f"verified_bug/verified_bugs_{owner_name}.json", "r") as f:
    #         v_b = json.load(f)
        
    #     del v_b[bug_name]

    #     with open(f"verified_bug/verified_bugs_{owner_name}.json", "w") as f:
    #         json.dump(v_b, f, indent=2)

    # subprocess.run([sys.executable, "debug/collector.py"], stdout=subprocess.PIPE)
    # delete_testing = shlex.split("rm -rf testing")
    # subprocess.run(delete_testing)