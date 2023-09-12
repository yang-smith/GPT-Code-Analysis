import inspect
import re
import subprocess

from enum import Enum
from typing import List, Union

from langchain.schema import AIMessage, HumanMessage, SystemMessage
from termcolor import colored
from gpt_code_analysis.ai import AI
from gpt_code_analysis.chat_to_files import to_files
from gpt_code_analysis.db import DBs
from gpt_code_analysis.tree import save_structure_to_file
# from gpt_code_analysis.learning import human_input
import ast
import chardet
from pathlib import Path

Message = Union[AIMessage, HumanMessage, SystemMessage]

def get_file_encoding(file_path: str) -> str:
    try:
        with open(file_path, 'rb') as file:
            return chardet.detect(file.read())['encoding']
    except Exception as e:
        print(f"Could not determine the encoding of file {file_path}. Error: {e}")
        return 'utf-8'  # 默认返回 'utf-8' 编码
    
def display_file_structure(input_path: str) -> str:
    """显示文件结构并返回system message"""
    save_structure_to_file(input_path, input_path / "filestructer.txt", input_path / "ignore.txt")
    with open(input_path / "filestructer.txt", "r") as file:
        return "this is the file structure.\n" + file.read()

def get_user_question() -> str:
    """从用户获取问题"""
    return input('(tell me what you want, or "c" to move on)\n')

def extract_needed_files_from_ai_response(messages: List[Message]) -> List[str]:
    """从AI的回应中提取需要的文件列表"""
    content = messages[-1].content.strip()
    
    # 尝试解析内容为Python列表
    try:
        file_paths = ast.literal_eval(content)
        # 额外的检查以确保它是一个列表
        if isinstance(file_paths, list):
            return file_paths
    except (SyntaxError, ValueError):
        pass
    
    # 如果内容不是预期的Python列表格式，则返回空列表
    return []


def fetch_file_contents(input_path: str, file_paths: List[str]) -> str:
    """从给定的文件路径中提取内容"""
    file_content = ""
    log = []

    for path in file_paths:
        full_path = Path(input_path) / path
        if not full_path.is_file():
            log.append(f"File not found: {full_path}")
            continue
        
        encoding = get_file_encoding(str(full_path))
        
        try:
            with open(full_path, "r", encoding=encoding) as file:
                file_content += "\n####" + path + "####\n"
                file_content += file.read()
        except UnicodeDecodeError:
            try:
                with open(full_path, "r", encoding='utf-8') as file: # 尝试另一个常见的编码
                    file_content += "\n####" + path + "####\n"
                    file_content += file.read()
            except Exception as e:
                log.append(f"Error reading file {full_path} with alternate encoding. Error: {e}")
                continue
        except Exception as e:
            log.append(f"Error reading file {full_path} with encoding {encoding}. Error: {e}")
            continue

    for message in log:
        print(message)
        
    return file_content


def analyze(ai, dbs, input_path):
    # 显示文件结构
    system_message = display_file_structure(input_path)
    

    while True:
        # 用户提出问题
        user_question = get_user_question()
        if user_question.lower() == 'c':
            break
        messages: List[Message] = [ai.fsystem(system_message)]
        user_input = dbs.preprompts["clarify"] + "My question is: " + user_question 
        messages = ai.next(messages, user_input, step_name="user_question")
        dbs.logs["user_question"] = AI.serialize_messages(messages)
        while True:
            # 从AI回应中提取需要的文件列表
            file_paths = extract_needed_files_from_ai_response(messages)
            if not file_paths:
                break
            # 获取文件内容
            file_content = fetch_file_contents(input_path, file_paths)
            further_question = file_content  + dbs.preprompts["clarify"]
            messages = ai.next(messages, further_question, step_name="test")
            dbs.logs["extern"] = AI.serialize_messages(messages)
        to_files(messages[-1].content.strip(), dbs.workspace)
        
        # for path in file_paths:
        #     messages = ai.next(messages, path + dbs.preprompts["gen_code"], step_name="test")
        #     to_files(messages[-1].content.strip(), dbs.workspace)

        # # 存储最后的消息
        # to_files(messages[-1].content.strip(), dbs.workspace)
