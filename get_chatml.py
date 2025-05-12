import json
import os
from glob import glob


def load_dialogue_data(folder_path):
    """
    读取文件夹下所有dialogue_data开头的JSON文件并合并数据

    :param folder_path: 包含JSON文件的文件夹路径
    :return: 合并后的对话数据列表
    """
    # 获取所有匹配的JSON文件
    file_pattern = os.path.join(folder_path, "dialogue_*.json")
    json_files = glob(file_pattern)

    if not json_files:
        print(f"警告：在{folder_path}中未找到任何dialogue_data*.json文件")
        return []

    all_dialogues = []

    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # 检查数据格式是否正确
                if isinstance(data, list):
                    all_dialogues.extend(data)
                else:
                    print(f"警告：{file_path}中的数据结构不是列表，已跳过")

        except json.JSONDecodeError as e:
            print(f"错误：无法解析{file_path} - {str(e)}")
        except Exception as e:
            print(f"错误：读取{file_path}时发生意外错误 - {str(e)}")
    all_data = []
    prompt = '你是泰康之家的客服管家，泰康之家是泰康人寿的养老社区，你需要耐心、热情、语气温和、富有共情能力，需要考虑共情能力,需要根据老人的特征进行回复。'
    feature = '客户老人的特征如下：\n{}'
    for d in all_dialogues:
        if 'system' in d:
            all_data.append({'messages':[{'role':'system','content':prompt+feature.format(d['system']['feature'])}]+d['messages']})
        else:
            all_data.append({'messages':[{'role':'system','content':prompt}]+d['messages']})


    return all_data


# 使用示例
if __name__ == "__main__":
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 设置数据文件夹路径为当前目录
    data_folder = current_dir
    dialogues = load_dialogue_data(data_folder)

    # 打印前3条数据作为示例
    for i, dialog in enumerate(dialogues[:3], 1):
        print(f"\n示例对话 {i}:")
        print(json.dumps(dialog, indent=2, ensure_ascii=False))

    # 保存结果到当前目录下的 doubao_data.json
    output_path = os.path.join(current_dir, 'style_chatbot.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dialogues, f, ensure_ascii=False, indent=4)

    print(f"数据已保存到 {output_path}")