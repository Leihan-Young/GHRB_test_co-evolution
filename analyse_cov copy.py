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
    ceprot_path = './new_exp/exp_test_ceprot_cov/output'
    ceprot_files = [name for name in os.listdir(ceprot_path)
            if name.endswith('.json')]
    approach_deepseek_path = './new_exp/exp_test_deepseek_fix_and_enhance_cov/output'
    approach_deepseek_files = [name for name in os.listdir(approach_deepseek_path)
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
            cov_overall[proj][k]['cov_test_src_focal_src'] = {'line_cov': line_cov, 'branch_cov': branch_cov}

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

    for file in ceprot_files:
        with open(os.path.join(ceprot_path, file), 'r', encoding='utf-8') as f:
            cov = json.load(f)
        proj = file.split('_')[-1].replace('.json', '')
        for k, v in cov.items():
            cov_test_ceprot_focal_tgt = v['cov_test_ceprot_focal_tgt']
            line_cov = cal_line_cov(cov_test_ceprot_focal_tgt)
            branch_cov = cal_branch_cov(cov_test_ceprot_focal_tgt)
            cov_overall[proj][k]['cov_test_ceprot_focal_tgt'] = {'line_cov': line_cov, 'branch_cov': branch_cov}

    for file in approach_deepseek_files:
        with open(os.path.join(approach_deepseek_path, file), 'r', encoding='utf-8') as f:
            cov = json.load(f)
        proj = file.split('_')[-1].replace('.json', '')
        for k, v in cov.items():
            cov_test_deepseek_fix_focal_tgt = v['cov_test_deepseek_fix_focal_tgt']
            line_cov = cal_line_cov(cov_test_deepseek_fix_focal_tgt)
            branch_cov = cal_branch_cov(cov_test_deepseek_fix_focal_tgt)
            cov_overall[proj][k]['cov_test_deepseek_fix_focal_tgt'] = {'line_cov': line_cov, 'branch_cov': branch_cov}

            cov_test_deepseek_enhance_focal_tgt = v['cov_test_deepseek_enhance_focal_tgt']
            line_cov = cal_line_cov(cov_test_deepseek_enhance_focal_tgt)
            branch_cov = cal_branch_cov(cov_test_deepseek_enhance_focal_tgt)
            cov_overall[proj][k]['cov_test_deepseek_enhance_focal_tgt'] = {'line_cov': line_cov, 'branch_cov': branch_cov}

    with open('./cov_res.json', 'w', encoding='utf-8') as f:
        json.dump(cov_overall, f, indent=2)

    data_row = 'cov_test_deepseek_enhance_focal_tgt'
    back_row = 'cov_test_deepseek_fix_focal_tgt'

    # 编译不通过
    line_cov_total = 0
    branch_cov_total = 0
    count = 0
    not_none = 0
    for proj, v in cov_overall.items():
        for test_id, cov_res in v.items():
            cov = cov_res['cov_test_src_focal_tgt']
            line_cov = cov['line_cov']
            branch_cov = cov['branch_cov']
            if not (line_cov is None or branch_cov is None):
                continue
            line_cov = cov_res[data_row]['line_cov']
            branch_cov = cov_res[data_row]['branch_cov']
            if line_cov == None:
                line_cov = cov_res[back_row]['line_cov']
                branch_cov = cov_res[back_row]['branch_cov']
            if line_cov == None:
                line_cov = 0
            else:
                not_none += 1
            if branch_cov == None:
                branch_cov = 0
            line_cov_total += line_cov
            branch_cov_total += branch_cov
            count += 1
    print(f"""
Fail to compile:
line_cov={line_cov_total/count}
branch_cov={branch_cov_total/count}
count={count}
not_none={not_none}
""")
    
    # 编译通过
    line_cov_total = 0
    branch_cov_total = 0
    count = 0
    not_none = 0
    for proj, v in cov_overall.items():
        for test_id, cov_res in v.items():
            cov = cov_res['cov_test_src_focal_tgt']
            line_cov = cov['line_cov']
            branch_cov = cov['branch_cov']
            if line_cov is None or branch_cov is None:
                continue
            line_cov = cov_res[data_row]['line_cov']
            branch_cov = cov_res[data_row]['branch_cov']
            if line_cov == None:
                line_cov = cov_res[back_row]['line_cov']
                branch_cov = cov_res[back_row]['branch_cov']
            if line_cov == None:
                line_cov = 0
            else:
                not_none += 1
            if branch_cov == None:
                branch_cov = 0
            line_cov_total += line_cov
            branch_cov_total += branch_cov
            count += 1
    print(f"""
Succeed to compile:
line_cov={line_cov_total/count}
branch_cov={branch_cov_total/count}
count={count}
not_none={not_none}
""")
    # Overall
    line_cov_total = 0
    branch_cov_total = 0
    count = 0
    not_none = 0
    for proj, v in cov_overall.items():
        for test_id, cov_res in v.items():
            cov = cov_res['cov_test_src_focal_tgt']
            line_cov = cov['line_cov']
            branch_cov = cov['branch_cov']
            line_cov = cov_res[data_row]['line_cov']
            branch_cov = cov_res[data_row]['branch_cov']
            if line_cov == None:
                line_cov = cov_res[back_row]['line_cov']
                branch_cov = cov_res[back_row]['branch_cov']
            if line_cov == None:
                line_cov = 0
            else:
                not_none += 1
            if branch_cov == None:
                branch_cov = 0
            line_cov_total += line_cov
            branch_cov_total += branch_cov
            count += 1
    print(f"""
Overall:
line_cov={line_cov_total/count}
branch_cov={branch_cov_total/count}
count={count}
not_none={not_none}
""")

    print("Finish")