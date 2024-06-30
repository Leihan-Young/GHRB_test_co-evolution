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
from tqdm import tqdm

def run_clean (new_env, mvnw, gradlew, path, is_install):

    if not mvnw and not gradlew:
        default = f'{new_env["MAVEN_HOME"]}/mvn clean'
        if is_install:
            default += ' install -DskipTests -Dlicense.skip=true'
        run = sp.run(default, env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path, shell=True)

    elif mvnw:
        default = f'./mvnw clean'
        if is_install:
            default += ' install -DskipTests -Dlicense.skip=true'
        run = sp.run(default, env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path, shell=True)

    elif gradlew:
        default = f"./gradlew clean"
        if is_install:
            default += ' install -DskipTests -Dlicense.skip=true'
        run = sp.run(default, env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path, shell=True)

    stdout = run.stdout.decode(encoding='utf-8', errors='ignore')
    stderr = run.stderr.decode(encoding='utf-8', errors='ignore')

    return stdout, stderr

def read_json(json_file):
    if not os.path.isfile(json_file):
        return None
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)
    
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

if __name__ == '__main__':
    data_path = '/data/zhiquanyang/Co-evolution/Benchmark/verified'
    repo_path = '/data/zhiquanyang/Co-evolution/Benchmark/collected/raw_repos'
    target_path = '/data/zhiquanyang/Co-evolution/Benchmark/repo_mirrors'
    cli_path = '/data/zhiquanyang/Co-evolution/Benchmark'
    files = [name for name in os.listdir(data_path)
                if name.endswith('.json')]
    for idx, file in enumerate(files):
        print(file)
        pid = file.split('_')[-1].replace('.json', '')
        source_path = f'/data/zhiquanyang/Co-evolution/Benchmark/collected/raw_repos/{pid}'
        sample_dict = read_json(os.path.join(data_path, file))
        for key, value in tqdm(sample_dict.items()):
            test_id = value['test_id']
            commit_tgt = value['commit_tgt']
            target = os.path.join(target_path, pid, f"{test_id}t")
            if os.path.exists(target):
                continue
            os.makedirs(target)
            command = f'git clone {source_path} {target} --depth=1'
            run = sp.run(command, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
            print(run.stdout.decode())
            checkout(pid, f'{test_id}t', target, commit_tgt)
            command = f"python cli.py clean -w {target}"
            run = sp.run(command, stdout=sp.PIPE, stderr=sp.PIPE, cwd=cli_path, shell=True)
            print(run.stdout.decode())
            command = f"python cli.py coverage -w {target} -o {os.path.abspath('./tmp_to_del')}"
            run = sp.run(command, stdout=sp.PIPE, stderr=sp.PIPE, cwd=cli_path, shell=True)
            print(run.stdout.decode())
            while "BUILD FAILURE" in run.stdout.decode():
                print("Again")
                command = f"python cli.py clean -w {target}"
                run = sp.run(command, stdout=sp.PIPE, stderr=sp.PIPE, cwd=cli_path, shell=True)
                print(run.stdout.decode())
                command = f"python cli.py coverage -w {target} -o {os.path.abspath('./tmp_to_del')}"
                run = sp.run(command, stdout=sp.PIPE, stderr=sp.PIPE, cwd=cli_path, shell=True)
                print(run.stdout.decode())