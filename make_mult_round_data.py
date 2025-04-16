# -*- coding: utf-8 -*-
"""
大学生对话数据生成系统 - 修改版
"""

# 初始化OpenAI客户端
client = OpenAI(
    api_key="******",
    base_url="*****",
)



# 全局变量和锁
lock = threading.Lock()
dialogs = []
processed_count = 0

def generate_student_profile():
    """生成随机大学生特征组合"""
    profile = {}
    for category in trait_db:
        trait, description = random.choice(list(trait_db[category].items()))
        profile[category] = {
            "类型": trait,
            "描述": description
        }
    return profile

def generate_dialog(topic_dict, rounds, length_range, examples):
    """生成对话的核心函数"""
    global dialogs, processed_count

    length = random.randint(length_range[0], length_range[1])
    feature = generate_student_profile()

    content_prompt = f"""
    1. assistant是校园心理咨询师
    2. user是在校大学生，其特征如下，生成对话在保证逻辑通畅的前提下，考虑以下特征{feature},并且以尽量贴近现实的语气对话。
    3. 生成的多轮对话中的assistant需要耐心、专业、富有共情能力，需要根据学生的特征进行回复。
    4. 多轮对话以user开始以assistant结束，格式和样例完全相同。
    5. 生成{rounds}轮次的以{topic_dict}为主题的多轮对话。
    6. assistant的每次对话的长度控制在{length}左右。
    7. 请注意user是学生，语气较为随意。
    - 参考以下风格：
    {examples}
    现在请你生成以上内容：
    """
    system_prompt={"feature":feature,'topic':topic_dict,}

    messages = [{"role": "user", "content": content_prompt}]

    try:
        completion = client.chat.completions.create(
            model="doubao-1.5-lite-32k-250115",
            messages=messages,
            temperature=0.7,
            max_tokens=3000
        )
        content = completion.choices[0].message.content
        content = json.loads(content)
        print(content)

        with lock:
            dialogs.append({'messages': content,"system":system_prompt})
            processed_count += 1

            if processed_count % 100 == 0:
                with open(r'D:\Mycode\xiaotai_data\create_long\dialogue_data.json', 'w', encoding='utf-8') as f:
                    json.dump(dialogs, f, ensure_ascii=False, indent=4)
                print(f'已保存{processed_count}条数据')

        return content
    except Exception as e:
        print(f"生成失败: {str(e)}")
        return None

def worker(task_args):
    """线程工作函数"""
    topic_dict, rounds, length_range, examples = task_args
    return generate_dialog(topic_dict, rounds, length_range, examples)

if __name__ == "__main__":
    # 加载真实样例数据
    with open(r'D:\Mycode\data\create_long\data_example.json', 'r', encoding='utf-8') as f:
        style_examples = json.load(f)
    #加载真实主题数据
    with open(r'D:\Mycode\data\create_long\主题.json', 'r', encoding='utf-8') as f:
        sample_topics = json.load(f)
    types = list(sample_topics[0].keys())

    # 准备任务列表
    tasks = []
    for _ in range(10000):
        sample_topic = random.choice(sample_topics[0][random.choice(types)])
        example = random.choice(style_examples)['messages']
        tasks.append((sample_topic, [3, 20], [60, 100], example))

    # 创建线程池
    max_workers = 60
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for task in tasks:
            future = executor.submit(worker, task)
            futures.append(future)

        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"任务异常: {str(e)}")

    # 最终保存
    with open(r'D:\Mycode\xiaotai_data\create_long\dialogue_data.json', 'w', encoding='utf-8') as f:
        json.dump(dialogs, f, ensure_ascii=False, indent=4)
    print(f'任务完成，共生成{len(dialogs)}条有效数据')
