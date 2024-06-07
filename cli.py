#!/usr/bin/python3.9

import os
import json

#from util import config, fix_build_env
import re
import subprocess as sp
import argparse
import javalang
import pandas as pd
import xml.etree.ElementTree as et
from datetime import datetime
from xml.dom import minidom

def call_info(pid):

    '''
    Summary of configuration for Project: {pid}
    ------------------------------------------
        Script dir: .../framework
        Base dir:   ...
        Major root: .../major
        Repo dir:   .../project_repos
    ------------------------------------------
        Project ID: 
        Program:    (name)
        Buildfile:  .../framework/projects/{pid}/{pid}.build.xml
    ------------------------------------------
        Number of bugs: 
        Commit db:
    '''

    '''
    bug_id, revision.id.buggy, revision.id.fixed, report.id, report.url
    '''
    with open("./project_id.json", "r") as f:
        project_id = json.load(f)
    
    if pid not in project_id.keys():
        output = "Wrong project id"
        return output
    
    owner = project_id[pid]["owner"]
    number_of_tests = project_id[pid]["number_of_tests"]
    repo_path = project_id[pid]["repo_path"]
    verified_db = project_id[pid]["verified_db"]


    output= (f'''
    Summary of configuration for Project: {pid}
    ------------------------------------------
        Repo dir:   {repo_path}
    ------------------------------------------
        Project ID: {pid}
        Program:    {owner}
    ------------------------------------------
        No. of tests:    {number_of_tests}
        Verified_db:     {verified_db}
    ''')
    return output

def call_checkout(pid, tid, dir):
    with open("./project_id.json", "r") as f:
        project_id = json.load(f)

    if pid not in project_id.keys():
        output = "Wrong project id"
        return output
    
    repo_path = project_id[pid]["repo_path"]

    with open(project_id[pid]["verified_db"], 'r', encoding='utf-8') as f:
        verified_db = json.load(f)

    test_id = tid[:-1]
    version = tid[-1]

    dir = os.path.abspath(dir)

    test_info = verified_db[test_id]

    commit = None
    
    output = "" 
    abs_path = os.getcwd()
    report_id = test_info['refer_PR']

    if version == "s":
        # source version
        commit = test_info["commit_src"]
    
    elif version == "t":
        # target version
        # commit = active_bugs.loc[active_bugs['bug_id'] == int(bid)]['revision.id.fixed'].values[0]
        commit = test_info["commit_tgt"]

    else:
        output = "Choose 's' for source version, 't' for target version"
        return output
    
    '''
    The working directory to which the buggy or fixed project version 
    shall be checked out. The working directory
    has to be either empty or a previously used working directory.

    ALL files in a previously used working directory are deleted prior 
    to checking out the requested project version.
    '''


    if commit != None:

        sp.run('git reset --hard HEAD',
            cwd=repo_path, stdout=sp.DEVNULL, stderr=sp.DEVNULL, shell=True)
        sp.run('git clean -df',
            cwd=repo_path, stdout=sp.DEVNULL, stderr=sp.DEVNULL, shell=True)

        # checkout to the buggy version and apply patch to the buggy version

        if dir is not None:
            #print("dir is not None 1")
            if not os.path.isdir(dir):
                os.mkdir(dir)

            if pid == "skywalking":
                p = sp.run(f'git clone {repo_path} {dir}', stdout=sp.PIPE, stderr=sp.PIPE, cwd=dir, shell=True)
                p = sp.run('git submodule init', stdout=sp.PIPE, stderr=sp.PIPE, cwd=dir, shell=True)
                p = sp.run('git submodule update', stdout=sp.PIPE, stderr=sp.PIPE, cwd=dir, shell=True)
                p = sp.run(f'git checkout {commit}', stdout=sp.PIPE, stderr=sp.PIPE, cwd=dir, shell=True)
                output += (f"Checking out \033[92m{commit}\033[0m to \033[92m{dir}\033[0m\n")
            else:
                
                # p = sp.run(['git', 'init'], stderr=sp.PIPE, stdout=sp.PIPE, cwd=dir)
                # p = sp.run(['git', 'fetch', 'origin', commit], 
                #                             stderr=sp.PIPE, stdout=sp.PIPE,
                #                             cwd=repo_path)

                # run = sp.run(['git', f'--work-tree={dir}', 'checkout', commit, '--', '.'], cwd=repo_path, shell=True)
                p = sp.run(f'git clone {repo_path} {dir}', stdout=sp.PIPE, stderr=sp.PIPE, cwd=dir, shell=True)
                p = sp.run(f'git checkout {commit}', stdout=sp.PIPE, stderr=sp.PIPE, cwd=dir, shell=True)
                output += (f"Checking out \033[92m{commit}\033[0m to \033[92m{dir}\033[0m\n")
        else:
            sp.run(f'git checkout {commit}', cwd=repo_path,
                stdout=sp.DEVNULL, stderr=sp.DEVNULL)
            output += (f"Checking out {commit} to {repo_path}\n")

        
        output += (f"Check out program version \033[4m{pid}-{tid}\033[0m\n")

        with open(f"{dir}/.pidtid.config", "w") as f:
            f.write("#File automatically generated\n")
            f.write(f"pid={pid}\n")
            f.write(f"tid={tid}")
            f.close()
    else:
        output += "Cannot find version..."
    
    return output

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

def call_compile(dir):
    '''
    Docker:
        maven 3.8.1, 3.8.6
        jdk 8, 11, 17
        gradle 7.6.2
    
    '''
    output = ""

    if not os.path.isfile(os.path.join(dir, ".pidtid.config")):
        output += "Config file not found...\n"
        output += "Re-run compile"
        return output
    
    with open(f"{dir}/.pidtid.config", "r") as f:
        content = f.read()

    pid_pattern = r'(pid=)(.*)\n'
    out = re.search(pid_pattern, content)
    pid = out.group(2)

    with open("./project_id.json", "r") as f:
        project_id = json.load(f)

    if pid not in project_id.keys():
        output = "No matching project id"
        return output

    repo_path = project_id[pid]["repo_path"]

    new_env, mvnw, gradlew = find_env(pid)

    path = repo_path if dir is None else dir
    #print(path)
    if pid == "jackson-core" or pid == "jackson-databind":
        fix_build_env(pid, path)

    if not mvnw and not gradlew:
        out = sp.run(f'{new_env["MAVEN_HOME"]}/mvn clean compile', env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, check=True, cwd=path, shell=True)
    elif mvnw:
        out = sp.run(['./mvnw clean compile'], env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, check=True, cwd=path, shell=True)
    
    elif gradlew:
        out = sp.run(['./gradlew clean compileJava'], env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, check=True, cwd=path, shell=True)

    if "BUILD SUCCESS" in out.stdout.decode(encoding='utf-8', errors='ignore'):
        output += "\033[92mBuild Success\033[0m"
    else:
        output += "\033[91mBuild Failed\033[0m"
    '''
    mvn clean install -DskipTests=true
    mvn clean package -Dmaven.buildDirectory='target'
    '''
    return output

def run_test (new_env, mvnw, gradlew, test_case, path, command=None, tidy_pom = False, verify = False):

    output = ""

    if tidy_pom:
        run = sp.run(f'{new_env["MAVEN_HOME"]}/mvn tidy:pom',
                    env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path, shell=True)

    if not mvnw and not gradlew:
        default = [f'{new_env["MAVEN_HOME"]}/mvn', '-T', '0.8C', 'verify' if verify else 'test', f'-Dtest={test_case}', '-DfailIfNoTests=false', '--errors']
        if command is not None:
            extra_command = command.split()
            new_command = default + extra_command
            new_command = ' '.join(new_command)
            run = sp.run(new_command,
                         env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path, shell=True)
        else:
            default = ' '.join(default)
            run = sp.run(default,
                        env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path, shell=True)

    elif mvnw:
        default = [f'./mvnw', '-T', '0.8C', 'verify' if verify else 'test', f'-Dtest={test_case}', '-DfailIfNoTests=false', '--errors']
        if command is not None:
            extra_command = command.split()
            new_command = default + extra_command
            new_command = ' '.join(new_command)
            run = sp.run(new_command,
                        env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path, shell=True)
        else:
            default = ' '.join(default)
            run = sp.run(default,
                        env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path, shell=True)
    elif gradlew:
        default = [f"./gradlew", '-T', '0.8C', 'verify' if verify else "test", "--tests", f'{test_case}', '--info', '--stacktrace']
        if command is not None:
            if 'test' in command:
                new_command = ["./gradlew", command, '--tests', f'{test_case}']
                new_command = ' '.join(new_command)
                run = sp.run(new_command,
                             env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path, shell=True)
            else:
                new_command = ' '.join(new_command)
                run = sp.run(new_command,
                             env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path, shell=True)
        else:
            default = ' '.join(default)
            run = sp.run(default,
                         env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path, shell=True)

    stdout = run.stdout.decode(encoding='utf-8', errors='ignore')
    stderr = run.stderr.decode(encoding='utf-8', errors='ignore')

    test_output = False
    if "BUILD SUCCESS" in stdout:
        output += (f'''
\033[1mTEST: {test_case}\033[0m 

\033[92mTest Success\033[0m
------------------------------------------------------------------------\n''')
        test_output = True
    elif "There are test failures" in stdout:
        pattern = r'\[ERROR\] Failures:(.*?)\[INFO\]\s+\[ERROR\] Tests run:'
        match = re.search(pattern, stdout, re.DOTALL)
        if match is None:
            pattern = r'\[ERROR\] Errors:(.*?)\[INFO\]\s+\[ERROR\] Tests run:'
            match = re.search(pattern, stdout, re.DOTALL)
        if match is None:
            pattern = r'Results[^\n]*\n(.*?)Tests run'
            match = re.search(pattern, stdout, re.DOTALL)
        fail_part = match.group(1).strip()
        fail_part = re.sub(r'\[ERROR\]', '', fail_part).strip()
        output += (f'''
\033[1mTEST: {test_case}\033[0m

\033[91mFailure/Error info:\033[0m
    {fail_part}
------------------------------------------------------------------------\n''')
        test_output = False
    elif 'There were failing tests' in stderr:
        pattern = r'Task\s+:\S+\s+FAILED\n([\s\S]*)Throwable that failed the check'
        match = re.search(pattern, stdout, re.DOTALL)
        if match is None:
            pattern = r"Successfully started process 'Gradle Test Executor \d+'(.*)\n([\s\S]*)Finished generating"
            match = re.search(pattern, stdout, re.DOTALL)
        fail_part = match.group(1).strip()
        output += (f'''
\033[1mTEST: {test_case}\033[0m

\033[91mFailure/Error info:\033[0m
    {fail_part}
------------------------------------------------------------------------\n''')
        test_output = False
    else:
        output += (f'''
\033[1mBUILD FAILURE\033[0m
------------------------------------------------------------------------\n''')

    # output += stdout

    return output, test_output, stdout

def call_clean(dir):
    output = ""

    if not os.path.isfile(os.path.join(dir, ".pidtid.config")):
        output += "pidtid config file not found...\n"
        output += "Re-run compile"
        return output
    
    with open(f"{dir}/.pidtid.config", "r") as f:
        content = f.read()

    pid_pattern = r'(pid=)(.*)\n'
    out = re.search(pid_pattern, content)
    pid = out.group(2)
    new_env, mvnw, gradlew = find_env(pid)
    is_install = False
    if pid == 'pulsar' or pid == 'shardingsphere':
        is_install = True
    stdout, stderr = run_clean(new_env, mvnw, gradlew, dir, is_install)
    output = f"stdout={stdout}\nstderr={stderr}"
    return output

def run_clean (new_env, mvnw, gradlew, path, is_install):

    if not mvnw and not gradlew:
        default = f'{new_env["MAVEN_HOME"]}/mvn clean'
        if is_install:
            default += ' install -DskipTests -Dlicense.skip=true -Dsurefire.failIfNoSpecifiedTests=false -Dcheckstyle.skip=true'
        run = sp.run(default, env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path, shell=True)

    elif mvnw:
        default = f'./mvnw clean'
        if is_install:
            default += ' install -DskipTests -Dlicense.skip=true -Dsurefire.failIfNoSpecifiedTests=false -Dcheckstyle.skip=true'
        run = sp.run(default, env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path, shell=True)

    elif gradlew:
        default = f"./gradlew clean"
        if is_install:
            default += ' install -DskipTests -Dlicense.skip=true -Dsurefire.failIfNoSpecifiedTests=false -Dcheckstyle.skip=true'
        run = sp.run(default, env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path, shell=True)

    stdout = run.stdout.decode(encoding='utf-8', errors='ignore')
    stderr = run.stderr.decode(encoding='utf-8', errors='ignore')

    return stdout, stderr

def call_test(dir, test_case, test_class, test_suite, log, quiet):
    '''
    default is the current directory
    test_case -> By default all tests are executed
    test_suite -> The archive file name of an external test suite. 
    test_class
    '''
    output = ""

    if not os.path.isfile(os.path.join(dir, ".ghrb.config")):
        output += "GHRB config file not found...\n"
        output += "Re-run compile"
        return output
    
    with open(f"{dir}/.ghrb.config", "r") as f:
        content = f.read()

    pid_pattern = r'(pid=)(.*)\n'
    out = re.search(pid_pattern, content)
    pid = out.group(2)

    vid_pattern = r'(vid=)(.*)'
    out = re.search(vid_pattern, content)
    vid = out.group(2)
    bid = vid[:-1]

    with open("/root/framework/data/project_id.json", "r") as f:
        project_id = json.load(f)

    if pid not in project_id.keys():
        output = "No matching project id"
        return output

    commit_db = project_id[pid]["commit_db"]
    repo_path = project_id[pid]["repo_path"]

    owner = project_id[pid]["owner"]

    repo_name = owner + "_" + pid

    command = None

    if len(project_id[pid]['requirements']['extra']) != 0:
        command = project_id[pid]['requirements']['extra']['command']
    
    with open(f"verified_bug/verified_bugs_{repo_name}.json", "r") as f:
        verified_bugs = json.load(f)

    active_bugs = pd.read_csv(commit_db)
    report_id = active_bugs.loc[active_bugs['bug_id'] == int(bid)]['report.id'].values[0]
    
    target_tests = verified_bugs[report_id]["execution_result"]["success_tests"]

    new_env, mvnw, gradlew = find_env(pid)

    path = repo_path if dir is None else dir

    def find_test (input):
        for test in target_tests:
            if test.find(input) != -1:
                return test
            else:
                return None
    
    def write_output (_content, _test_output, _quiet, _output):
        if _test_output is True and _quiet is True:
            pass
        else:
            _output += _content
        return _output
            
    if test_case is not None:
        found_test_case = find_test(test_case)
        test_case = test_case.replace(":", "#")

        if found_test_case is None:
            content, test_output, stdout = run_test(new_env, mvnw, gradlew, test_case, path, command)
            output = write_output(content, test_output, quiet, output)
        else:
            content, test_output, stdout = run_test(new_env, mvnw, gradlew, test_case, path, command)
            output = write_output(content, test_output, quiet, output)
    elif test_class is not None:
        content, test_output, stdout = run_test(new_env, mvnw, gradlew, test_class, path, command)
        output = write_output(content, test_output, quiet, output)
    elif test_suite is not None:
        pass
    else:
        for test in target_tests:
            content, test_output, stdout = run_test(new_env, mvnw, gradlew, test, path, command)
            output = write_output(content, test_output, quiet, output)

    marker = ""

    if test_case is not None:
        marker += "_" + test_case
    elif test_class is not None:
        marker += "_" + test_class
    elif test_suite is not None:
        marker += "_" + test_suite
    
    if quiet is True:
        marker += "_quiet"

    if log is True:
        if not os.path.isdir("log"):
            os.mkdir("log")
        
        with open(f"log/{pid}_{vid}{marker}.log", "w") as f:
            f.writelines(stdout)
        
        f.close()
    
    return output

def call_coverage(work_dir, input_file, output_dir, use_test_tgt):
    output = ""

    if not os.path.isfile(os.path.join(work_dir, ".pidtid.config")):
        output += "pidtid config file not found...\n"
        output += "Re-run compile"
        return output
    
    with open(f"{work_dir}/.pidtid.config", "r") as f:
        content = f.read()

    pid_pattern = r'(pid=)(.*)\n'
    out = re.search(pid_pattern, content)
    pid = out.group(2)

    tid_pattern = r'(tid=)(.*)'
    out = re.search(tid_pattern, content)
    full_tid = out.group(2)
    tid = full_tid[:-1]
    version = full_tid[-1]

    with open("./project_id.json", "r") as f:
        project_id = json.load(f)

    if pid not in project_id.keys():
        output = "No matching project id"
        return output

    with open(project_id[pid]["verified_db"], 'r', encoding='utf-8') as f:
        verified_db = json.load(f)
    repo_path = project_id[pid]["repo_path"]

    owner = project_id[pid]["owner"]

    repo_name = owner + "_" + pid

    command = None

    if len(project_id[pid]['requirements']['extra']) != 0:
        command = project_id[pid]['requirements']['extra']['command']

    test_src = verified_db[tid]['test_src']
    test_tgt = verified_db[tid]['test_tgt']
    focal_src_path = verified_db[tid]['focal_path_src']
    changed_tests = verified_db[tid]['changed_tests']

    new_env, mvnw, gradlew = find_env(pid)

    path = repo_path if work_dir is None else work_dir

    if version == 's':
        commit = verified_db[tid]['commit_src']
    elif version == 't':
        commit = verified_db[tid]['commit_tgt']
    else:
        output = f"Wrong tid version in {path}"
        return output

    # _ = call_checkout(pid, full_tid, path)

    test_cases = ''
    if input_file is None:
        if use_test_tgt:
            test_cases = ','.join(test_tgt)
        else:
            test_cases = test_src
    else:
        try:
            prefix = test_src.split('#')[0]
            t = []
            with open(input_file, 'r', encoding='utf-8') as f:
                method_lines = f.readlines()
                tree = javalang.parse.parse("public class tempClassName { $TEST_METHODS$ }".replace("$TEST_METHODS$", ''.join(method_lines)))
            for _, node in tree:
                if isinstance(node, javalang.tree.MethodDeclaration):
                    t.append(f'{prefix}#{node.name}')
            test_cases = ','.join(t)
        except Exception as e:
            output = f"Fail to parse {input_file}"
            return output

    if test_cases == '':
        output = "No test case is found"
        return out
    
    # insert test methods into test_src file
    related_path = test_src.split('#')[0].replace('.', '/')
    test_path = None
    for changed_test in changed_tests:
        if related_path in changed_test:
            test_path = changed_test
            break
    if test_path == None:
        output = f"Fail to find test_src file for {path}"
        return output
    if input_file != None:
        with open(os.path.join(path, test_path), 'r', encoding='utf-8') as f:
            test_class_lines = f.readlines()
        test_class_lines = delete_test_methods_with_code_lines(test_class_lines, test_cases.split(','))
        test_class_lines = insert_test_methods_into_code_lines(test_class_lines, method_lines)
        with open(os.path.join(path, test_path), 'w', encoding='utf-8') as f:
            f.writelines(test_class_lines)

    # root pom
    try:
        with open(os.path.join(path, "pom.xml"), 'r') as f:
            pom_root = et.fromstring(f.read())
        prefix = pom_root.tag[:pom_root.tag.find('project')] if pom_root.tag != 'project' else ""
        pom_root = add_jacoco_dependency(pom_root, prefix)
        pom_root = add_plugin_config(pom_root, prefix)
        et.register_namespace('', prefix[1:-1])
        with open(os.path.join(path, "pom.xml"), 'w') as f:
            str = minidom.parseString(et.tostring(pom_root, method='xml').decode()).toprettyxml(indent="  ")
            list = str.split('\n')
            write_content = '\n'.join([l for l in list if len(l.lstrip()) != 0])
            write_content = write_content.replace("<jacoco.skip>true</jacoco.skip>", "<jacoco.skip>false</jacoco.skip>")
            write_content = write_content.replace("<jacoco.report.skip>true</jacoco.report.skip>", "<jacoco.report.skip>false</jacoco.report.skip>")
            write_content = write_content.replace(r"${testJacocoAgentArgument}", r"@{argLine}")
            f.write(write_content)
    except Exception as e:
        output = f"Fail to add jacoco dependency and set plugin config to {path}/pom.xml"
        return output

    # 修改目标module中pom.xml的surefire配置（如果有)
    try:
        tgt_modules = []
        test_path = test_path.split('/')[:-1]
        cur = path
        for i in range(len(test_path)):
            if 'pom.xml' not in os.listdir(os.path.join(cur, test_path[i])):
                cur = os.path.join(cur, test_path[i])
                continue
            cur = os.path.join(cur, test_path[i])
            tgt_modules.append(cur)
        for tgt_module in tgt_modules:
            with open(os.path.join(tgt_module, "pom.xml"), 'r') as f:
                pom_root = et.fromstring(f.read())
            prefix = pom_root.tag[:pom_root.tag.find('project')] if pom_root.tag != 'project' else ""
            pom_root = correct_surefire_argLine(pom_root, prefix)
            et.register_namespace('', prefix[1:-1])
            with open(os.path.join(tgt_module, "pom.xml"), 'w') as f:
                str = minidom.parseString(et.tostring(pom_root, method='xml').decode()).toprettyxml(indent="  ")
                list = str.split('\n')
                write_content = '\n'.join([l for l in list if len(l.lstrip()) != 0])
                write_content = write_content.replace("<jacoco.skip>true</jacoco.skip>", "<jacoco.skip>false</jacoco.skip>")
                f.write(write_content)
    except Exception as e:
        output = f"Fail to correct surefire argLine for modules in {path}"
        return output
    
    tidy_pom = False
    with open(os.path.join(path, "pom.xml"), 'r') as f:
        x = f.read()
        if "org.codehaus.mojo" in x and "tidy-maven-plugin" in x:
            tidy_pom = True
    verify = False
    if pid == 'pulsar':
        verify = True
    output, test_output, stdout = run_test(new_env, mvnw, gradlew, test_cases, path, command, tidy_pom, verify)
    if "Test Success" in output:
        output += "Test passed\n"
    elif "Failure/Error info" in output:
        output += "Test failed\n"
    elif "BUILD FAILURE" in output:
        output += "Build failed\n"
    tgt_cov_xml = None
    jacoco_out_path = None
    if len(tgt_modules) == 0:
        if os.path.exists(os.path.join(path, 'target', 'site', 'jacoco', 'jacoco.xml')):
            tgt_cov_xml = os.path.join(path, 'target', 'site', 'jacoco', 'jacoco.xml')
            jacoco_out_path = os.path.join(path, 'target', 'site', 'jacoco')
    else:
        for tgt_module in tgt_modules:
            if os.path.exists(os.path.join(tgt_module, 'target', 'site', 'jacoco', 'jacoco.xml')):
                tgt_cov_xml = os.path.join(tgt_module, 'target', 'site', 'jacoco', 'jacoco.xml')
                jacoco_out_path = os.path.join(tgt_module, 'target', 'site', 'jacoco')
    if tgt_cov_xml == None:
        output += f"Fail to generate jacoco report for {path}"
        return output
    
    output += (f"Coverage report generated to \033[4m{os.path.join(cur, 'target', 'site', 'jacoco', 'jacoco.xml')}\033[0m\n")

    tgt_cov_html_files = []
    focal_files = set()
    for focal_path in focal_src_path:
        focal_files.add(focal_path.split('#')[0])
    for focal_file in focal_files:
        ind = focal_file.rfind('/')
        folders = focal_file[:ind].replace('/', '.')
        focal_class = focal_file[ind+1:]
        folder_name = folders[folders.find('.java.') + len('.java.'):]
        tgt_cov_html_files.append(os.path.join(jacoco_out_path, folder_name, f'{focal_class}.html'))

    with open(tgt_cov_xml, 'r', encoding='utf-8') as f:
        s = f.read()
    os.remove(tgt_cov_xml)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    try:
        with open(os.path.join(output_dir, f'{pid}-{full_tid}_cov_jacoco.xml'), 'w', encoding='utf-8') as f:
            f.write(minidom.parseString(s).toprettyxml(indent="  "))
    except Exception as e:
        output += (f"Error coverage report, no content")
        return output

    output += (f"Formatted report xml is written to \033[4m{os.path.join(output_dir, f'{pid}_{full_tid}-cov-jacoco.xml')}\033[0m\n")

    for html_file in tgt_cov_html_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            s = f.read()
        os.remove(html_file)
        file_name = html_file.split('/')[-1]
        with open(os.path.join(output_dir, file_name), 'w', encoding='utf-8') as f:
            f.write(s)
    
    output += (f"Jacoco report html is written to \033[4m{','.join([os.path.join(output_dir, x.split('/')[-1]) for x in tgt_cov_html_files])}\033[0m\n")

    return output

def delete_test_methods_with_code_lines(code_lines, test_cases):
    tree = javalang.parse.parse(''.join(code_lines))
    test_methods = [t.split('#')[-1] for t in test_cases]
    positions = []
    for path, node in tree:
        if isinstance(node, javalang.tree.MethodDeclaration) and 'annotations' in node.attrs and node.name in test_methods:
            for anno in getattr(node, 'annotations'):
                if anno.name == 'Test':
                    positions.append((node.name, node.position.line))
    for pos in reversed(sorted(positions, key=lambda x:x[1])):
        code_lines = delete_test_method_with_code_lines(code_lines, pos)
    return code_lines

def delete_test_method_with_code_lines(code_lines, pos):
    method_name, target_line_number = pos
    start = target_line_number
    while start >= 0:
        if code_lines[start].find(method_name) != -1 or (code_lines[start].find('public ') != -1 or code_lines[start].find('private ') != -1 or code_lines[start].find('protected ') != -1):
            break
        start = start - 1
    # 如果方法前有Annotations
    define_line = start
    while start > 0:
        start = start - 1
        if code_lines[start].find('@') == -1:
            break
    start = start + 1
    # 寻找方法注释
    tmp = start
    while start >= 0:
        if code_lines[start].find('/*') != -1:
            break
        elif re.match('\s*(})\s*', code_lines[start]) or code_lines[start].find('class ') != -1 or code_lines[start].find('interface ') != -1:
            start = tmp
            break
        start = start - 1
    if start < 0:
        raise Exception("Error:" + method_name + " not found")
    # 找方法结尾
    end = define_line
    comment = False
    count = None
    end = end - 1
    while end + 1 < len(code_lines) or count == None:
        end = end + 1
        if comment and code_lines[end].find('*/') != -1:
            comment = False
            continue
        if code_lines[end].find('/*') != -1 and code_lines[end].find('*/') == -1 and code_lines[end][:code_lines[end].find('/*')].find('"') == -1 and code_lines[end][:code_lines[end].find('/*')].find('}') == -1:
            comment = True
            continue
        if countSymbol(code_lines[end], ';') != 0 and count == None:
            break
        left_count = countSymbol(code_lines[end], '{')
        right_count = countSymbol(code_lines[end], '}')
        diff = left_count - right_count
        if count == None and diff != 0:
            count = diff
        elif count != None:
            count = count + diff
        if count != None and count <= 0:
            break
    if code_lines[end].find('/*') != -1 and code_lines[end][:code_lines[end].find('/*')].find('"') == -1 and code_lines[end][:code_lines[end].find('/*')].find('}') == -1:
        code_lines[end] = code_lines[end][:code_lines[end].find('}') + 1]
    end = end + 1
    if end >= len(code_lines):
        raise Exception("Error:Unexpected error in extract_focal_code()")
    # 回退末尾不需要的内容
    if code_lines[end].find('public ') != -1 or code_lines[end].find('private ') != -1:
        end = end - 1
        while end > target_line_number and code_lines[end].find('@') != -1:
            end = end - 1
        if code_lines[end].find('*/') != -1:
            while end > target_line_number and code_lines[end].find('/*') == -1:
                end = end - 1
    return code_lines[:start] + code_lines[end:]

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

def insert_test_methods_into_code_lines(code_lines, method_lines):
    method_lines = ['\t'+l if l.endswith('\n') else '\t'+l+'\n' for l in method_lines]
    cur = len(code_lines) - 1
    while not code_lines[cur].startswith('}'):
        cur = cur - 1
    return code_lines[:cur] + method_lines + code_lines[cur:]

def add_plugin_config(root, prefix):
    build = root.find(prefix+"build")
    plugins = build.find(prefix+"plugins")
    new_plugins_node = False
    if plugins == None:
        new_plugins_node = True
        plugins = et.Element(prefix+"plugins")
    # jacoco plugin
    jacoco = None
    for plugin in plugins.findall(prefix+"plugin"):
        try:
            group_id = plugin.find(prefix+"groupId").text
            artifact_id = plugin.find(prefix+"artifactId").text
            if group_id == "org.jacoco" and artifact_id == "jacoco-maven-plugin":
                jacoco = plugin
                break
        except:
            continue
    new_jacoco_node = False
    if jacoco == None:
        new_jacoco_node = True
        jacoco = et.Element(prefix+"plugin")
        jacoco.append(create_element(prefix+"groupId", "org.jacoco"))
        jacoco.append(create_element(prefix+"artifactId", "jacoco-maven-plugin"))
    if jacoco.find(prefix+"version") == None:
        jacoco.append(create_element(prefix+"version", "0.8.11"))
    # else:
    #     jacoco.find(prefix+"version").text = "0.8.11"
    if jacoco.find(prefix+"configuration") != None:
        config_node = jacoco.find(prefix+"configuration")
        destFile_node = config_node.find(prefix+"destFile")
        dataFile_node = config_node.find(prefix+"dataFile")
        if destFile_node != None:
            destFile_node.text = "target/jacoco.exec"
        if dataFile_node != None:
            dataFile_node.text = "target/jacoco.exec"
    executions_node = jacoco.find(prefix+"executions")
    if executions_node == None:
        executions_node = et.Element(prefix+"executions")
        execution_node = et.Element(prefix+"execution")
        execution_node.append(create_element(prefix+"id", "default-prepare-agent"))
        goals_node = et.Element(prefix+"goals")
        goals_node.append(create_element(prefix+"goal", "prepare-agent"))
        execution_node.append(goals_node)
        executions_node.append(execution_node)
        execution_node = et.Element(prefix+"execution")
        execution_node.append(create_element(prefix+"id", "report"))
        execution_node.append(create_element(prefix+"phase", "test"))
        goals_node = et.Element(prefix+"goals")
        goals_node.append(create_element(prefix+"goal", "report"))
        execution_node.append(goals_node)
        configuration_node = et.Element(prefix+"configuration")
        configuration_node.append(create_element(prefix+"dataFile", "target/jacoco.exec"))
        formats_node = et.Element(prefix+"formats")
        formats_node.append(create_element(prefix+"format", "XML"))
        formats_node.append(create_element(prefix+"format", "HTML"))
        formats_node.append(create_element(prefix+"format", "CSV"))
        configuration_node.append(formats_node)
        excludes_node = et.Element(prefix+"excludes")
        excludes_node.append(create_element(prefix+"exclude", "META-INF/**"))
        configuration_node.append(excludes_node)
        execution_node.append(configuration_node)
        executions_node.append(execution_node)
        jacoco.append(executions_node)
    else:
        default_prepare_agent = False
        default_report = False
        # default_instrument = False
        default_restore = False
        default_prepare_agent_node = None
        default_report_node = None
        # default_instrument_node = None
        default_restore_node = None
        for execution_node in executions_node.findall(prefix+"execution"):
            tmp_goals_node = execution_node.find(prefix+"goals")
            if tmp_goals_node == None:
                continue
            tmp_goal_nodes = tmp_goals_node.findall(prefix+"goal")
            for tmp_goal_node in tmp_goal_nodes:
                goal = tmp_goal_node.text
                # if goal == "instrument":
                #     default_instrument_node = execution_node
                #     default_instrument = True
                if goal == "report":
                    default_report_node = execution_node
                    default_report = True
                elif goal == "restore-instrumented-classes":
                    default_restore_node = execution_node
                    default_restore = True
                elif goal == "prepare-agent":
                    default_prepare_agent_node = execution_node
                    default_prepare_agent = True
        if not default_prepare_agent:
            execution_node = et.Element(prefix+"execution")
            execution_node.append(create_element(prefix+"id", "default-prepare-agent"))
            goals_node = et.Element(prefix+"goals")
            goals_node.append(create_element(prefix+"goal", "prepare-agent"))
            execution_node.append(goals_node)
            executions_node.append(execution_node)
        else:
            goals_node = default_prepare_agent_node.find(prefix+"goals")
            new_goals_node = False
            if goals_node == None:
                new_goals_node = True
                goals_node = et.Element(prefix+"goals")
            add_new_goal = True
            for goal_node in goals_node.findall(prefix+"goal"):
                if goal_node.text == "prepare-agent":
                    add_new_goal = False
                    break
            if add_new_goal:
                goals_node.append(create_element(prefix+"goal", "prepare-agent"))
            if new_goals_node:
                default_prepare_agent_node.append(goals_node)
        if not default_report:
            execution_node = et.Element(prefix+"execution")
            execution_node.append(create_element(prefix+"id", "default-report"))
            execution_node.append(create_element(prefix+"phase", "test"))
            goals_node = et.Element(prefix+"goals")
            goals_node.append(create_element(prefix+"goal", "report"))
            execution_node.append(goals_node)
            configuration_node = et.Element(prefix+"configuration")
            configuration_node.append(create_element(prefix+"dataFile", "target/jacoco.exec"))
            formats_node = et.Element(prefix+"formats")
            formats_node.append(create_element(prefix+"format", "XML"))
            formats_node.append(create_element(prefix+"format", "HTML"))
            formats_node.append(create_element(prefix+"format", "CSV"))
            configuration_node.append(formats_node)
            execution_node.append(configuration_node)
            executions_node.append(execution_node)
        else:
            phase_node = default_report_node.find(prefix+"phase")
            if phase_node == None:
                default_report_node.append(create_element(prefix+"phase", "test"))
            else:
                phase_node.text = "test"
            new_goals_node = False
            if goals_node == None:
                new_goals_node = True
                goals_node = et.Element(prefix+"goals")
            add_new_goal = True
            for goal_node in goals_node.findall(prefix+"goal"):
                if goal_node.text == "report":
                    add_new_goal = False
                    break
            if add_new_goal:
                goals_node.append(create_element(prefix+"goal", "report"))
            if new_goals_node:
                default_report_node.append(goals_node)
            configuration_node = default_report_node.find(prefix+"configuration")
            new_config_node = False
            if configuration_node == None:
                new_config_node = True
                configuration_node = et.Element(prefix+"configuration")
            if configuration_node.find(prefix+"dataFile") == None:
                configuration_node.append(create_element(prefix+"dataFile", "target/jacoco.exec"))
            else:
                configuration_node.find(prefix+"dataFile").text = "target/jacoco.exec"
            formats_node = configuration_node.find(prefix+"formats")
            new_formats_node = False
            if formats_node == None:
                new_formats_node = True
                formats_node = et.Element(prefix+"formats")
            add_new_format_xml = True
            add_new_format_html = True
            add_new_format_csv = True
            for format_node in formats_node.findall(prefix+"format"):
                if format_node.text == "XML":
                    add_new_format_xml = False
                if format_node.text == "HTML":
                    add_new_format_html = False
                if format_node.text == "CSV":
                    add_new_format_csv = False
            if add_new_format_xml:
                formats_node.append(create_element(prefix+"format", "XML"))
            if add_new_format_html:
                formats_node.append(create_element(prefix+"format", "HTML"))
            if add_new_format_csv:
                formats_node.append(create_element(prefix+"format", "CSV"))
            if new_formats_node:
                configuration_node.append(formats_node)
            if new_config_node:
                default_report_node.append(configuration_node)
        if default_restore:
            phase_node = default_restore_node.find(prefix+"phase")
            if phase_node == None:
                default_restore_node.append(create_element(prefix+"phase", "test"))
            else:
                phase_node.text = "test"

    if new_jacoco_node:
        plugins.append(jacoco)

    # surefire plugin
    surefire = None
    for plugin in plugins.findall(prefix+"plugin"):
        try:
            group_id = plugin.find(prefix+"groupId").text
            artifact_id = plugin.find(prefix+"artifactId").text
            if group_id == "org.apache.maven.plugins" and artifact_id == "maven-surefire-plugin":
                surefire = plugin
                break
        except:
            continue
    new_surefire_node = False
    if surefire == None:
        new_surefire_node = True
        surefire = et.Element(prefix+"plugin")
        surefire.append(create_element(prefix+"groupId", "org.apache.maven.plugins"))
        surefire.append(create_element(prefix+"artifactId", "maven-surefire-plugin"))
    if surefire.find(prefix+"version") == None:
        surefire.append(create_element(prefix+"version", "3.0.0"))
    # else:
    #     surefire.find(prefix+"version").text = "3.0.0"
    configuration_node = surefire.find(prefix+"configuration")
    if configuration_node == None:
        configuration_node = et.Element(prefix+"configuration")
        configuration_node.append(create_element(prefix+"useSystemClassLoader", "false"))
        configuration_node.append(create_element(prefix+"forkMode", "once"))
        configuration_node.append(create_element(prefix+"reuseForks", "true"))
        configuration_node.append(create_element(prefix+"testFailureIgnore", "true"))
        configuration_node.append(create_element(prefix+"argLine", r"@{argLine}"))
        systemPropertyVariables_node = et.Element(prefix+"systemPropertyVariables")
        systemPropertyVariables_node.append(create_element(prefix+"jacoco-agent.destfile", "target/jacoco.exec"))
        configuration_node.append(systemPropertyVariables_node)
        surefire.append(configuration_node)
    else:
        if configuration_node.find(prefix+"useSystemClassLoader") == None:
            configuration_node.append(create_element(prefix+"useSystemClassLoader", "false"))
        if configuration_node.find(prefix+"forkMode") == None:
            configuration_node.append(create_element(prefix+"forkMode", "once"))
        if configuration_node.find(prefix+"reuseForks") == None:
            configuration_node.append(create_element(prefix+"reuseForks", "true"))
        if configuration_node.find(prefix+"testFailureIgnore") == None:
            configuration_node.append(create_element(prefix+"testFailureIgnore", "true"))
        if configuration_node.find(prefix+"argLine") == None:
            configuration_node.append(create_element(prefix+"argLine", r"@{argLine}"))
        systemPropertyVariables_node = configuration_node.find(prefix+"systemPropertyVariables")
        new_system_node = False
        if systemPropertyVariables_node == None:
            new_system_node = True
            systemPropertyVariables_node = et.Element(prefix+"systemPropertyVariables")
        if systemPropertyVariables_node.find(prefix+"jacoco-agent.destfile") == None:
            systemPropertyVariables_node.append(create_element(prefix+"jacoco-agent.destfile", "target/jacoco.exec"))
        else:
            systemPropertyVariables_node.find(prefix+"jacoco-agent.destfile").text = "target/jacoco.exec"
        if new_system_node:
            configuration_node.append(systemPropertyVariables_node)
        

    if new_surefire_node:
        plugins.append(surefire)

    if new_plugins_node:
        build.append(plugins)
    return root

def add_jacoco_dependency(root, prefix):
    dependency_manager = root.find(prefix+"dependencyManagement")
    if dependency_manager == None:
        dependencies = root.find(prefix+"dependencies")
    else:
        dependencies = dependency_manager.find(prefix+"dependencies")
    for dep in dependencies.findall(prefix+"dependency"):
        group_id = dep.find(prefix+"groupId").text
        artifact_id = dep.find(prefix+"artifactId").text
        if group_id == "org.jacoco" and artifact_id == "org.jacoco.agent":
            # dep.find(prefix+"version").text = "0.8.11"
            return root
    jacoco_dep = et.Element(prefix+"dependency")
    jacoco_dep.append(create_element(prefix+"groupId", "org.jacoco"))
    jacoco_dep.append(create_element(prefix+"artifactId", "org.jacoco.agent"))
    jacoco_dep.append(create_element(prefix+"version", "0.8.11"))
    jacoco_dep.append(create_element(prefix+"classifier", "runtime"))
    dependencies.append(jacoco_dep)
    return root

def create_element(tag, text):
    x = et.Element(tag)
    x.text = text
    return x

def correct_surefire_argLine(root, prefix):
    build = root.find(prefix+"build")
    if build == None:
        return root
    plugins = build.find(prefix+"plugins")
    if plugins == None:
        return root
    surefire_node = None
    plugin_nodes = plugins.findall(prefix+"plugin")
    for plugin_node in plugin_nodes:
        if plugin_node.find(prefix+'artifactId').text == "maven-surefire-plugin":
            surefire_node = plugin_node
            break
    if surefire_node == None:
        return root
    configuration_node = surefire_node.find(prefix+"configuration")
    if configuration_node == None:
        return root
    useSystemClassLoader_node = configuration_node.find(prefix+"useSystemClassLoader")
    if useSystemClassLoader_node != None:
        useSystemClassLoader_node.text = "false"
    forkMode_node = configuration_node.find(prefix+"forkMode")
    if forkMode_node != None:
        forkMode_node.text = "once"
    reuseForks_node = configuration_node.find(prefix+"reuseForks")
    if reuseForks_node != None:
        reuseForks_node.text = "true"
    testFailureIgnore_node = configuration_node.find(prefix+"testFailureIgnore")
    if testFailureIgnore_node != None:
        testFailureIgnore_node.text = "true"
    argLine_node = configuration_node.find(prefix+"argLine")
    if argLine_node != None:
        argLine_node.text = f'{argLine_node.text} ' + r"@{argLine}"
    return root
    


def call_bid(pid, quiet):
    with open("/root/framework/data/project_id.json", "r") as f:
        project_id = json.load(f)

    if pid not in project_id.keys():
        output = "Wrong project id"
        return output
    
    number_of_bugs = project_id[pid]["number_of_bugs"]
    commit_db = project_id[pid]["commit_db"]
    output = ""
    if not quiet:
        output += f'''
    Bug Information for {pid}

    Total number of bugs: {number_of_bugs}
    ------------------------------------------
'''

    active_bugs = pd.read_csv(commit_db)

    for bug_id in active_bugs["bug_id"]:
        output += f"\t{bug_id}\n"
    
    return output

def call_pid(quiet):

    if quiet:
        output = ""
    else:
        output = '''
    Owner:\t\tProject ID
    ----------------------------------------
''' 
    with open("./project_id.json", "r") as f:
        project_id = json.load(f)
    
    for pid in project_id.keys():
        project_name = project_id[pid]["owner"]
        if quiet:
            output += f"{pid}\n"
        else:
            output += f"    {project_name}:\t\t{pid}\n"
    
    return output

def call_env(pid):
    
    with open("./project_id.json", "r") as f:
        project_id = json.load(f)
    
    if pid not in project_id.keys():
        output = "Wrong project id"
        return output
    
    requirements = project_id[pid]["requirements"]

    output = requirements

    return output

def call_ptr(pid):

    with open("/root/framework/data/project_id.json", "r") as f:
        project_id = json.load(f)

    if pid not in project_id.keys():
        output = "Wrong project id"
        return output
    
    with open("contamination.json", "r") as f:
        portrait_result = json.load(f)

    owner = project_id[pid]["owner"]
    
    output += portrait_result[f'{owner}_{pid}']
    
    return output


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

def fix_build_env(project, path):

    pom_file = os.path.join(path, 'pom.xml')

    with open(pom_file, 'r') as f:
        content = f.read()

    if project == 'jackson-core':
        replace_map = properties_to_replace['jackson-core']
    elif project == 'jackson-databind':
        replace_map = properties_to_replace['jackson-databind']

    for unsupported_property in replace_map:
        content = re.sub(
            unsupported_property, replace_map[unsupported_property], content)

    with open(pom_file, 'w') as f:
        f.write(content)

def call_export(pid, tid, output_dir):
    with open("./project_id.json", "r") as f:
        project_id = json.load(f)

    if pid not in project_id.keys():
        output = "Wrong project id"
        return output
    
    repo_path = project_id[pid]["repo_path"]

    with open(project_id[pid]["verified_db"], 'r', encoding='utf-8') as f:
        verified_db = json.load(f)

    test_id = tid[:-1]
    version = tid[-1]

    test_info = verified_db[test_id]
    
    output = ""
    content = {}

    content['commit_src'] = test_info['commit_src']
    content['commit_tgt'] = test_info['commit_tgt']
    content['focal_src'] = test_info['focal_src']
    content['focal_tgt'] = test_info['focal_tgt']
    content['test_src'] = test_info['test_src']
    content['test_tgt'] = test_info['test_tgt']
    content['changed_tests'] = test_info['changed_tests']

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(os.path.join(output_dir, f"{pid}_{test_id}_export.json"), 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=2)
    
    output += "\033[92mExport Success\033[0m"

    return output

def call_cut(date):
    with open("/root/framework/data/project_id.json", "r") as f:
        project_id = json.load(f)
    
    output = ""

    date = datetime.strptime(date, "%Y-%m-%d").date()

    for pid in project_id.keys():
        commit_db = project_id[pid]["commit_db"]
        owner = project_id[pid]["owner"]
        repo_name = owner + "_" + pid

        with open(f"verified_bug/verified_bugs_{repo_name}.json", "r") as f:
            verified_bugs = json.load(f)

        active_bugs = pd.read_csv(commit_db)

        for bug_id in active_bugs["bug_id"]:
            report_id = active_bugs.loc[active_bugs['bug_id'] == int(bug_id)]["report.id"].values[0]
            created_date = datetime.strptime(verified_bugs[report_id]['PR_createdAt'], "%Y-%m-%dT%H:%M:%SZ")
            created_date = created_date.date()
            
            if created_date >= date:
                output += f"{pid}_{bug_id}\n"
        
    return output


if __name__ == '__main__':

    default_dir = os.getcwd()

    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="command")

    #  d4j-info -p project_id [-b bug_id]
    parser_info = subparsers.add_parser('info',
                                        help="View configuration of a specific project")
    
    parser_info.add_argument('-p', dest="project_id", action="store",
                             help="The id of the project for which the information shall be printed")
    

    #  d4j-checkout -p project_id -v version_id -w work_dir
    parser_checkout = subparsers.add_parser('checkout',
                                        help="Check out a buggy or a fixed project version")

    parser_checkout.add_argument("-p", dest="project_id", action="store",
                                 help="The id of the project for which the information shall be checked out")
    
    parser_checkout.add_argument("-t", dest="test_id", action="store",
                                 help="The test id that shall be checked out. E.g. 4s, 5t (s for source, t for target)")
    
    parser_checkout.add_argument("-w", dest="work_dir", action="store",
                                 help="The working directory")
    

    # d4j-compile -- compile a checked-out project version.
    parser_compile = subparsers.add_parser('compile',
                                        help="Compile sources and developer-written tests of a buggy or a fixed project version")
    
    parser_compile.add_argument("-w", dest="work_dir", action="store",
                                help="The working directory of the checked-out project version (optional). Default is the current directory")
    

    parser_clean = subparsers.add_parser('clean',
                                        help="Clean the work dir")
    
    parser_clean.add_argument("-w", dest="work_dir", action="store",
                                help="The working directory of the checked-out project version (optional). Default is the current directory")
    

    #  d4j-test [-w work_dir] [-r | [-t single_test] [-s test_suite]]
    parser_cov = subparsers.add_parser('coverage',
                                        help="Run tests in the input test file on a buggy or a fixed project version and calculate the coverage with jacoco")
    
    parser_cov.add_argument("-w", dest="work_dir", action="store",
                             help="The working directory of the checked-out project version (optional). Default is the current directory")
    
    parser_cov.add_argument("-i", dest="input_file", action="store", default=None,
                             help="The test file that contains one or more test methods")
    
    parser_cov.add_argument("-o", dest="output_dir", action="store",
                             help="The dir where the coverage result stores")
    
    parser_cov.add_argument("-t", "--test_tgt", dest="test_tgt", action="store_true",
                             help="When input file is not specified, use test_src if there is no -t, and use test_tgt if there is -t")
    
    #   d4j-bids -p project_id [-D|-A]

    # parser_bid = subparsers.add_parser('bid',
    #                                    help="Print the list of available active bug IDs")
    
    # parser_bid.add_argument("-p", dest='project_id', action="store",
    #                         help="The ID of the project for which the list of bug IDs is returned")
    
    # parser_bid.add_argument("-q", "--quiet", dest='quiet', action='store_true',
    #                         help="Print only the bug IDs")
    
    #   d4j-pids
    
    parser_pid = subparsers.add_parser('pid',
                                       help="Print the list of available project IDs")
    
    parser_pid.add_argument("-q", "--quiet", dest="quiet", action="store_true",
                            help="Print only the Project IDs")
    
    #   d4j-env

    parser_env = subparsers.add_parser('env',
                                       help="Print the environment of each project")
    
    parser_env.add_argument("-p", dest='project_id', action="store",
                            help="The ID of the project for which the environment is returned")
    
    # export the focal_src focal_tgt etc
    parser_export = subparsers.add_parser('export',
                                          help="Export the focal_src, focal_tgt and e.t.c.")

    parser_export.add_argument("-p", dest='project_id', action="store",
                            help="The ID of the project for which the environment is returned")
    
    parser_export.add_argument("-t", dest="test_id", action="store",
                                 help="The test id that shall be checked out.")

    parser_export.add_argument("-o", dest="output_dir", action="store",
                                 help="The output dir where the infomation stores")
    
    #   extra--portrait

    # parser_portrait = subparsers.add_parser('ptr',
    #                                         help="Print the collected results from dataportraits.org (oldest commit for each project)")
    
    # parser_portrait.add_argument("-p", dest='project_id', action="store",
    #                              help="The ID of the project for which the result is returned")

    #   d4j-export

    # parser_export = subparsers.add_parser('export',
    #                                       help="Export version-specific properties")
    
    # parser_export.add_argument("-p", dest='property', action="store",
    #                            help="Export the values of this property")
    
    # parser_export.add_argument("-o", dest='output_file', action="store",
    #                            help="Write output to this file")
    
    # parser_export.add_argument("-w", dest='working_dir', action="store",
    #                            help="The working directory of the checked-out project version")
    
    #   cut-off

    # parser_cut = subparsers.add_parser('cut',
    #                                    help="Print the list of available project IDs and bug IDs, created after the manually set cut-off point")
    
    # parser_cut.add_argument("-d", dest='date', action="store",
    #                         help="Cut-off point. Format: YYYY-MM-DD")
    
    args = parser.parse_args()
    #print(args)
    if args.command == "info":
        output = call_info(args.project_id)
        print(output)
    elif args.command == "checkout":
        output = call_checkout(args.project_id, args.test_id, args.work_dir)
        print(output)
    elif args.command == "compile":
        output = call_compile(args.work_dir)
        print(output)
    # elif args.command == "test":
    #     output = call_test(args.work_dir, args.single_test, args.test_class, args.test_suite, args.log, args.quiet)
    #     print(output)
    # elif args.command == "bid":
    #     output = call_bid(args.project_id, args.quiet)
    #     print(output)
    elif args.command == "pid":
        output = call_pid(args.quiet)
        print(output)
    elif args.command == "env":
        output = call_env(args.project_id)
        print(output)
    elif args.command == "export":
        output = call_export(args.project_id, args.test_id, args.output_dir)
        print(output)
    elif args.command == "coverage":
        output = call_coverage(args.work_dir, args.input_file, args.output_dir, args.test_tgt)
        print(output)
    elif args.command == "clean":
        output = call_clean(args.work_dir)
        print(output)
    # elif args.command == "ptr":
    #     output = call_ptr(args.project_id)
    #     print(output)
    # elif args.command == "export":
    #     output = call_export(args.property, args.output_file, args.working_dir)
    #     print(output)
    # elif args.command == "cut":
    #     output = call_cut(args.date)
    #     print(output)

    
