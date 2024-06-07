import json
import os

BOTH_FAIL = 'both_fail'
UPDATE_FAIL = 'update_fail'

def cal_line_cov(cov):
    if cov is None:
        return None
    count = 0
    cov_res = 0
    for k, v in cov.items():
        if v is None or len(v) == 0:
            continue
        line_cov = int(v['LINE']['covered']) / (int(v['LINE']['covered']) + int(v['LINE']['missed']))
        cov_res += line_cov
        count += 1
    if count == 0:
        return None
    return cov_res / count

def cal_branch_cov(cov):
    if cov is None:
        return None
    count = 0
    cov_res = 0
    for k, v in cov.items():
        if v is None or len(v) == 0:
            continue
        if 'BRANCH' in v.keys():
            branch_cov = int(v['BRANCH']['covered']) / (int(v['BRANCH']['covered']) + int(v['BRANCH']['missed']))
        else:
            branch_cov = 1
        cov_res += branch_cov
        count += 1
    if count == 0:
        return None
    return cov_res / count

if __name__ == "__main__":
    ori_path = './new_exp/exp_test_src_cov/output'
    ori_files = [name for name in os.listdir(ori_path)
            if name.endswith('.json')]
    deep_seek_path = './new_exp/exp_test_deepseek_cov/output'
    deep_seek_files = [name for name in os.listdir(deep_seek_path)
            if name.endswith('.json')]
    cov_overall = {}
    for file in ori_files:
        with open(os.path.join(ori_path, file), 'r', encoding='utf-8') as f:
            cov = json.load(f)
        proj = file.split('_')[-1].replace('.json', '')
        cov_overall[proj] = {}
        for k, v in cov.items():
            cov_overall[proj][k] = {}

            cov_test_src_focal_src = v['cov_test_src_focal_src']
            line_cov = cal_line_cov(cov_test_src_focal_src)
            branch_cov = cal_branch_cov(cov_test_src_focal_src)
            cov_overall[proj][k]['test_src_focal_src'] = {'line_cov': line_cov, 'branch_cov': branch_cov}

            cov_test_tgt_focal_tgt = v['cov_test_tgt_focal_tgt']
            line_cov = cal_line_cov(cov_test_tgt_focal_tgt)
            branch_cov = cal_branch_cov(cov_test_tgt_focal_tgt)
            cov_overall[proj][k]['cov_test_tgt_focal_tgt'] = {'line_cov': line_cov, 'branch_cov': branch_cov}

            cov_test_src_focal_tgt = v['cov_test_src_focal_tgt']
            line_cov = cal_line_cov(cov_test_src_focal_tgt)
            branch_cov = cal_branch_cov(cov_test_src_focal_tgt)
            cov_overall[proj][k]['cov_test_src_focal_tgt'] = {'line_cov': line_cov, 'branch_cov': branch_cov}

    for file in deep_seek_files:
        with open(os.path.join(deep_seek_path, file), 'r', encoding='utf-8') as f:
            cov = json.load(f)
        proj = file.split('_')[-1].replace('.json', '')
        for k, v in cov.items():
            cov_test_deepseek_focal_tgt = v['cov_test_deepseek_focal_tgt']
            line_cov = cal_line_cov(cov_test_deepseek_focal_tgt)
            branch_cov = cal_branch_cov(cov_test_deepseek_focal_tgt)
            cov_overall[proj][k]['cov_test_deepseek_focal_tgt'] = {'line_cov': line_cov, 'branch_cov': branch_cov}

    with open('./cov_res.json', 'w', encoding='utf-8') as f:
        json.dump(cov_overall, f, indent=2)

    # test src under focal src
    line_cov_total = 0
    branch_cov_total = 0
    count = 0
    for proj, v in cov_overall.items():
        for test_id, cov_res in v.items():
            cov = cov_res['test_src_focal_src']
            line_cov = cov['line_cov']
            branch_cov = cov['branch_cov']
            if line_cov is None or branch_cov is None:
                line_cov = 0
                branch_cov = 0
            line_cov_total += line_cov
            branch_cov_total += branch_cov
            count += 1
    print(f"""
test_src_focal_src_all:
line_cov={line_cov_total/count}
branch_cov={branch_cov_total/count}
count={count}
""")
    
    # test tgt under focal tgt
    line_cov_total = 0
    branch_cov_total = 0
    count = 0
    for proj, v in cov_overall.items():
        for test_id, cov_res in v.items():
            cov = cov_res['cov_test_tgt_focal_tgt']
            line_cov = cov['line_cov']
            branch_cov = cov['branch_cov']
            if line_cov is None or branch_cov is None:
                continue
            line_cov_total += line_cov
            branch_cov_total += branch_cov
            count += 1
    print(f"""
test_tgt_focal_tgt_all:
line_cov={line_cov_total/count}
branch_cov={branch_cov_total/count}
count={count}
""")
    
    # test src under focal tgt
    line_cov_total = 0
    branch_cov_total = 0
    count = 0
    for proj, v in cov_overall.items():
        for test_id, cov_res in v.items():
            cov = cov_res['cov_test_src_focal_tgt']
            line_cov = cov['line_cov']
            branch_cov = cov['branch_cov']
            if line_cov is None or branch_cov is None:
                continue
            line_cov_total += line_cov
            branch_cov_total += branch_cov
            count += 1
    print(f"""
test_src_focal_tgt_all:
line_cov={line_cov_total/count}
branch_cov={branch_cov_total/count}
count={count}
""")
    # test src在focal tgt上能运行的对应的test src under focal src
    line_cov_total = 0
    branch_cov_total = 0
    count = 0
    for proj, v in cov_overall.items():
        for test_id, cov_res in v.items():
            cov = cov_res['cov_test_src_focal_tgt']
            line_cov = cov['line_cov']
            branch_cov = cov['branch_cov']
            if line_cov is None or branch_cov is None:
                continue
            line_cov_total += cov_res['test_src_focal_src']['line_cov'] if cov_res['test_src_focal_src']['line_cov'] is not None else 0
            branch_cov_total += cov_res['test_src_focal_src']['branch_cov'] if cov_res['test_src_focal_src']['branch_cov'] is not None else 0
            count += 1
    print(f"""
test_src_focal_src_src对应:
line_cov={line_cov_total/count}
branch_cov={branch_cov_total/count}
count={count}
""")
    # test src在focal tgt上能运行的对应的test tgt under focal tgt
    line_cov_total = 0
    branch_cov_total = 0
    count = 0
    for proj, v in cov_overall.items():
        for test_id, cov_res in v.items():
            cov = cov_res['cov_test_src_focal_tgt']
            line_cov = cov['line_cov']
            branch_cov = cov['branch_cov']
            if line_cov is None or branch_cov is None:
                continue
            line_cov_total += cov_res['cov_test_tgt_focal_tgt']['line_cov']
            branch_cov_total += cov_res['cov_test_tgt_focal_tgt']['branch_cov']
            count += 1
    print(f"""
test_tgt_focal_tgt_src对应:
line_cov={line_cov_total/count}
branch_cov={branch_cov_total/count}
count={count}
""")
    
    # test deepseek under focal tgt
    line_cov_total = 0
    branch_cov_total = 0
    count = 0
    for proj, v in cov_overall.items():
        for test_id, cov_res in v.items():
            if 'cov_test_deepseek_focal_tgt' not in cov_res.keys():
                continue
            if proj == 'shardingsphere' and test_id == '2':
                continue
            cov = cov_res['cov_test_deepseek_focal_tgt']
            line_cov = cov['line_cov']
            branch_cov = cov['branch_cov']
            if line_cov is None or branch_cov is None:
                continue
            line_cov_total += line_cov
            branch_cov_total += branch_cov
            count += 1
    print(f"""
test_deepseek_focal_tgt_all:
line_cov={line_cov_total/count}
branch_cov={branch_cov_total/count}
count={count}
""")
    # test deepseek在focal tgt上能运行的对应的test src under focal src
    line_cov_total = 0
    branch_cov_total = 0
    count = 0
    for proj, v in cov_overall.items():
        for test_id, cov_res in v.items():
            if 'cov_test_deepseek_focal_tgt' not in cov_res.keys():
                continue
            if proj == 'shardingsphere' and test_id == '2':
                continue
            cov = cov_res['cov_test_deepseek_focal_tgt']
            line_cov = cov['line_cov']
            branch_cov = cov['branch_cov']
            if line_cov is None or branch_cov is None:
                continue
            line_cov_total += cov_res['test_src_focal_src']['line_cov'] if cov_res['test_src_focal_src']['line_cov'] is not None else 0
            branch_cov_total += cov_res['test_src_focal_src']['branch_cov'] if cov_res['test_src_focal_src']['branch_cov'] is not None else 0
            count += 1
    print(f"""
test_src_focal_src_deepseek对应:
line_cov={line_cov_total/count}
branch_cov={branch_cov_total/count}
count={count}
""")
    # test deepseek在focal tgt上能运行的对应的test tgt under focal tgt
    line_cov_total = 0
    branch_cov_total = 0
    count = 0
    for proj, v in cov_overall.items():
        for test_id, cov_res in v.items():
            if 'cov_test_deepseek_focal_tgt' not in cov_res.keys():
                continue
            if proj == 'shardingsphere' and test_id == '2':
                continue
            cov = cov_res['cov_test_deepseek_focal_tgt']
            line_cov = cov['line_cov']
            branch_cov = cov['branch_cov']
            if line_cov is None or branch_cov is None:
                continue
            line_cov_total += cov_res['cov_test_tgt_focal_tgt']['line_cov']
            branch_cov_total += cov_res['cov_test_tgt_focal_tgt']['branch_cov']
            count += 1
    print(f"""
test_tgt_focal_tgt_deepseek对应:
line_cov={line_cov_total/count}
branch_cov={branch_cov_total/count}
count={count}
""")
    # test deepseek在focal tgt上能运行的对应的test src under focal tgt
    line_cov_total = 0
    branch_cov_total = 0
    count = 0
    for proj, v in cov_overall.items():
        for test_id, cov_res in v.items():
            if 'cov_test_deepseek_focal_tgt' not in cov_res.keys():
                continue
            cov = cov_res['cov_test_deepseek_focal_tgt']
            line_cov = cov['line_cov']
            branch_cov = cov['branch_cov']
            if line_cov is None or branch_cov is None:
                continue
            if cov_res['cov_test_src_focal_tgt']['line_cov'] is None:
                continue
            line_cov_total += cov_res['cov_test_src_focal_tgt']['line_cov'] if cov_res['cov_test_src_focal_tgt']['line_cov'] is not None else 0
            branch_cov_total += cov_res['cov_test_src_focal_tgt']['branch_cov'] if cov_res['cov_test_src_focal_tgt']['branch_cov'] is not None else 0
            count += 1
    print(f"""
test_src_focal_tgt_deepseek对应:
line_cov={line_cov_total/count}
branch_cov={branch_cov_total/count}
count={count}
""")

    print("Finish")