import collections, logging, itertools

import bashlex.parser
import bashlex.ast

def docker_bash_parser(commands):
    cmds = []

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
