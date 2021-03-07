################### Parser Dockerfile #####################
import json
import crawler
import collections, logging, itertools

import bashlex.parser
import bashlex.ast

from json import dumps
from dockerfile_parser import parser 

# major function
# paras "dockerfile": return from crawler.resolve_images_info(image)
def dockerfile2bash(dockerfile):
    cmds = []
    commands = dockerfile2cmds(dockerfile)
    if len(commands) == 0:
        return cmds

    for command in commands["RUN"]:
        # get beshlex AST
        try:
            parts = bashlex.parse(command)
        except:
            return cmds

        for ast in parts:
            cmd = []
            try:
                for i in range(len(ast.parts)):
                    word = ast.parts[i].word
                    cmd.append(word)
                cmds.append(cmd)
            except:
                continue

    return cmds

def dockerfile2cmds(dockerfile):
    commands = {}
    if dockerfile == None or dockerfile == "":
        print ("[ERR] dockerfile format error...")
        return commands

    # resolve the dockerfile
    try:
        dockerfile = parse_dockerfile(dockerfile)
    except:
        print ("[ERR] Dockerfile parsing failed...")
        return commands

    commands["RUN"] = parse_cmds_from_dockerfile(dockerfile)
    commands["CMD"] = parse_exe_from_dockerfile(dockerfile)
    commands["ADD"] = parse_add_from_dockerfile(dockerfile)

    return commands

def parse_dockerfile(path):
    parsed = parser.parse(path)
    dockerfile = dumps(parsed, indent=2, separators=(',', ': '))
    dockerfile = json.loads(dockerfile)

    return dockerfile

# parsing "CMD" and "ENTRYPOINT"
def parse_exe_from_dockerfile(dockerfile):
    entrypoints = []
    try:
        entrypoint = dockerfile['workdir']['/']['root']['entrypoint']
    except:
        entrypoint = []

    try:
        cmd = dockerfile['workdir']['/']['root']['cmd']
    except:
        cmd = []

    # list to str
    for entry in entrypoint:
        if type(entry) is list:
            for e in entry:
                entrypoints.append(e) 
        else:
            entrypoints.append(entry) 

    for entry in cmd:
        if type(entry) is list:
            for e in entry:
                entrypoints.append(e) 
        else:
            entrypoints.append(entry) 

    return entrypoints


def split_bash_cmds(commands):
    # store the function in bash
    commands = commands.replace("&&", ";")
    command = commands.split(";")
    
    return command

# parsing "RUN" commnads
def parse_cmds_from_dockerfile(dockerfile):
    commands = []

    try:
        for item in dockerfile['workdir']['/']['root']['run']:
            command = split_bash_cmds(item)
            commands = commands + command
    except:
        return commands

    return commands

# parsing "ADD" and "COPY" commnads
def parse_add_from_dockerfile(dockerfile):
    copy = []

    try:
        for item in dockerfile['workdir']['/']['root']['copy']:
            command = "COPY " + item['src'] + " " + item['dest']
            copy.append(command)
    except:
        pass

    try:
        for item in dockerfile['workdir']['/']['root']['add']:
            command = "ADD " + item['src'] + " " + item['dest']
            copy.append(command)
    except:
        pass

    return copy