import crawl
import download
import parse2cmds

basePath = "./results/"

"""
trace the keywords in dockerfile:
keywords: target keyword list
"""
def trace_keywords(dockerfile, keywords):
    # trace the source of the scripts
    sourceEntry = parse2cmds.trace_entry_images(dockerfile)
    write_log(image, sourceEntry, "images")

    # identify the keywords
    keywords = ["paste ", "split "]
    identify = parse2cmds.identify_keywords(dockerfile, keywords)
    write_log(image, identify, "keywords")


"""
    trace the source of scripts in the entrypoint and cmd
"""
def trace_entry_images(dockerfile):
    # trace scripts
    sources_scripts = {}

    # get the entrypoint 
    entrypoint = parse2cmds.parse_exe_from_dockerfile(dockerfile)
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
    commands = parse2cmds.parse_cmds_from_dockerfile(dockerfile)
    for script in scripts:
        # from RUN commands
        for command in commands:
            if script in command:
                if script not in sources_scripts:
                    sources_scripts[script] = [command]
                else:
                    sources_scripts[script].append(command)

        # from COPY or ADD
        copy = parse2cmds.parse_add_from_dockerfile(dockerfile)
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
    commands = parse2cmds.parse_cmds_from_dockerfile(dockerfile)

    # "ENTRYPOINT" or "CMD"
    entrypoints = parse2cmds.parse_exe_from_dockerfile(dockerfile)

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



# log the detection results
"""
def write_log(image, results, filename):
    path = basePath + filename + ".csv"
    with open(path, "a+") as log:
        for item in results:
            log.write(image + ", " + item + ", ")
            for obj in results[item]:
                log.write(obj.replace("\n", " "))
            log.write("\n") 
"""