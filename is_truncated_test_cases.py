import os
import json
import javalang

template = r"class TestClassName { $TEST$ }"

if __name__ == "__main__":
    with open('./ceprot_gen/verified_tuples_apache_rocketmq.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    fail_count = 0
    for key, value in data.items():
        try:
            tree = javalang.parse.parse(template.replace("$TEST$", value['CEPROT_gen_test_tgt']))
        except Exception as e:
            fail_count += 1
    print(fail_count)