################### Handle Dockerfile #####################
import json
from json import dumps
from dockerfile_parser import parser 

def parse_dockerfile(path):
    parsed = parser.parse(path)
    dockerfile = dumps(parsed, indent=2, separators=(',', ': '))
    dockerfile = json.loads(dockerfile)

    return dockerfile

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

def parse_cmds_from_dockerfile(dockerfile):
    commands = []

    try:
        for item in dockerfile['workdir']['/']['root']['run']:
            command = split_bash_cmds(item)
            commands = commands + command
    except:
        return commands

    return commands

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

"""
    trace the source of scripts in the entrypoint and cmd
"""
def trace_entry_images(dockerfile):
    # trace scripts
    sources_scripts = {}

    # get the entrypoint 
    entrypoint = parse_exe_from_dockerfile(dockerfile)
    if len(entrypoint) == 0:
        return sources_scripts

    # get scripts executed in ENTRYPOINT or CMD
    scripts = []
    for cmds in entrypoint:
        for cmd in cmds.split(" "):
            if ".sh" in cmd or ".py" in cmd:
                cmd = cmd.strip().replace("./", "")
                scripts.append(cmd)

    # trace the source of the scripts
    commands = parse_cmds_from_dockerfile(dockerfile)
    for script in scripts:
        # from RUN commands
        for command in commands:
            if script in command:
                if script not in sources_scripts:
                    sources_scripts[script] = [command]
                else:
                    sources_scripts[script].append(command)

        # from COPY or ADD
        copy = parse_add_from_dockerfile(dockerfile)
        for external in copy:
            if script in external:
                if script not in sources_scripts:
                    sources_scripts[script] = [external]
                else:
                    sources_scripts[script].append(external)

        # cannot find the source of script from commands
        if script not in sources_scripts:
            sources_scripts[script] = []

    #print (sources_scripts)
    return sources_scripts


"""
    find the keywords if it are in the dockerfile
"""
def identify_keywords(dockerfile, keywords):
    results = {}

    # "RUN" commands
    commands = parse_cmds_from_dockerfile(dockerfile)

    # "ENTRYPOINT" or "CMD"
    entrypoints = parse_exe_from_dockerfile(dockerfile)

    # "keywords" is a list of keyword
    for keyword in keywords:
        identify = []
        
        # strat detect
        for command in commands:
            if keyword in command:
                identify.append(command)

        for entry in entrypoints:
            if keyword in entry:
                identify.append(entry)

        if len(identify) != 0:
            results[keyword] = identify

    return results
