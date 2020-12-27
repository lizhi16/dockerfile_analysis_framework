import json
import hashlib
import random
import requests

#import filters

from collections import OrderedDict

_INSTRUCTIONS = ['FROM',
                 'MAINTAINER',
                 'RUN',
                 'CMD',
                 'LABEL',
                 'EXPOSE',
                 'ENV',
                 'ADD',
                 'COPY',
                 'ENTRYPOINT',
                 'VOLUME',
                 'USER',
                 'WORKDIR',
                 'ONBUILD']


def _hash_image_name(name):
    """
    Create fake `CONTAINER ID`
    """

    image_name = name + str(random.randint(100, 200))

    return hashlib.md5(image_name.encode("utf-8")).hexdigest()[12:]


def _get_dist_name(commands):
    """
    Get the first name of the operating system
    """

    for command in commands:
        line = [command.strip() for command in command.split(' ')]
        if len(line):
            if line[0] == 'FROM':
                return _hash_image_name(line[-1])

    return False


def _parse_raw_dockerfile(lines):
    """
    Author: Michal Papierski <michal@papierski.net>
    https://github.com/mpapierski/dockerfile-parser
    """

    result, current_line = [], []
    for line in lines:
        if line.startswith('#') or not line.strip():
            continue
        current_line.append(line)
        if line.rstrip()[-1] != '\\':
            result.append(''.join(current_line))
            current_line = []

    return result

def _to_commands(content):
    """
    Split dockerfile-file on the instructions
    """

    """
    if "http" in path:
        content = get_url(path)
        commands = _parse_raw_dockerfile(content.splitlines())
    else:
        with open(path) as f:
            commands = _parse_raw_dockerfile(f.read().splitlines())
    """

    commands = _parse_raw_dockerfile(content.splitlines())

    return commands


def parse(file_or_cmds, onbuild=False, with_container_id=False):
    """
    Getting the structure Dockerfile
    """

    commands = file_or_cmds if onbuild else _to_commands(file_or_cmds)
    image = _get_dist_name(commands)

    workdir, first, user, data, onbuild_lines = '/', True, 'root', \
                                                OrderedDict(), []
    for command in commands:
        if with_container_id:
            if image not in data:
                data[image] = OrderedDict()

            if not onbuild:
                if 'workdir' not in data[image]:
                    data[image]['workdir'] = OrderedDict()

                if workdir not in data[image]['workdir']:
                    data[image]['workdir'][workdir] = OrderedDict()

                if user not in data[image]['workdir'][workdir]:
                    data[image]['workdir'][workdir][user] = OrderedDict()

            struct = data[image]
        else:
            if not onbuild:
                if 'workdir' not in data:
                    data['workdir'] = OrderedDict()

                if workdir not in data['workdir']:
                    data['workdir'][workdir] = OrderedDict()

                if user not in data['workdir'][workdir]:
                    data['workdir'][workdir][user] = OrderedDict()

            struct = data

        if onbuild:
            udata = struct
        else:
            udata = struct['workdir'][workdir][user]
        split = [v for v in command.split() if len(v)]

        instr, value = split[0].upper(), ' '.join(split[1:]).strip()
        if instr not in _INSTRUCTIONS:
            break

        if instr == 'FROM':
            if with_container_id and not first:
                image = _hash_image_name(value)
                data[image] = OrderedDict()
                data[image]['from'] = from_filter(value)
            else:
                first = False
                struct['from'] = from_filter(value)
        elif instr == 'MAINTAINER':
            struct['maintainer'] = maintainer_filter(value)
        elif instr == 'RUN':
            if 'run' not in udata:
                udata['run'] = []
            udata['run'] = run_filter(udata['run'], value)
        elif instr == 'CMD':
            if 'cmd' not in udata:
                udata['cmd'] = []
            udata['cmd'] = cmd_filter(udata['cmd'], value)
        elif instr == 'LABEL':
            if 'label' not in struct:
                struct['label'] = OrderedDict()
            struct['label'] = label_filter(struct['label'], value)
        elif instr == 'EXPOSE':
            if 'expose' not in struct:
                struct['expose'] = []
            struct['expose'] = expose_filter(struct['expose'], value)
        elif instr == 'ENV':
            if 'env' not in struct:
                struct['env'] = OrderedDict()
            struct['env'] = env_filter(struct['env'], value)
        elif instr == 'ADD':
            if 'add' not in udata:
                udata['add'] = []
            udata['add'] = add_filter(udata['add'], value)
        elif instr == 'COPY':
            if 'copy' not in udata:
                udata['copy'] = []
            udata['copy'] = copy_filter(udata['copy'], value)
        elif instr == 'ENTRYPOINT':
            udata['entrypoint'] = entrypoint_filter(value)
        elif instr == 'VOLUME':
            if 'volume' not in struct:
                struct['volume'] = []
            struct['volume'] = volume_filter(struct['volume'], value)
        elif instr == 'USER':
            user = value
        elif instr == 'WORKDIR':
            workdir = value
        elif instr == 'ONBUILD':
            onbuild_lines.append(value)

        if len(onbuild_lines):
            struct['onbuild'] = parse(
                onbuild_lines, onbuild=True, with_container_id=False)

    return data


################# filter.py ###############
def _strip_quote(value):
    """
    Removing the quotes around the edges
    """

    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    elif value.startswith("'") and value.endswith("'"):
        value = value[1:-1]

    return value


def _strip_backslash(value):
    """
    Remove backslashes from the string
    """

    return ' '.join(value.replace('\\', '').split())


def _detect(value, assumption):
    """
    Definition format string
    """

    if assumption == 'array':
        return value.startswith('[') and value.endswith(']')

    return False


def _key_value_splitter(value):
    """
    Separation `key=value` in the convenient form
    """

    value = _strip_backslash(value)

    if '=' not in value:
        return [value]

    values, i = OrderedDict(), 0
    for line in value.split():
        if '=' in line:
            values[i] = [line]
            i += 1
        else:
            values[i - 1].append(line)

    return [' '.join(v) for v in [k[1] for k in values.items()]]


def from_filter(value):
    """
    Specification:
        FROM <image>
        or
        FROM <image>:<tag>
        or
        FROM <image>@<digest>
    """

    detail = None
    if '@' in value:
        image, digest = value.split('@')
        detail = {'image': image, 'digest': digest}

    if ':' in value:
        image, tag = value.split(':')
        detail = {'image': image, 'tag': tag}

    if detail:
        return {'full_name': value, 'detail': detail}
    else:
        return {'full_name': value}


def maintainer_filter(value):
    """
    Specification:
        MAINTAINER <name>
    """

    return value


def run_filter(items, value):
    """
    Specification:
        RUN <command>
        or
        RUN ["executable", "param1", "param2"]
    """

    print (value, type(value))
    if _detect(value, assumption='array'):
        parse = json.loads(value)
        items.append(parse)
    else:
        items.append(_strip_backslash(value))

    return items


def cmd_filter(items, value):
    """
    Specification:
        CMD ["executable","param1","param2"]
        or
        CMD ["param1","param2"]
        or
        CMD command param1 param2
    """
    if _detect(value, assumption='array'):
        parse = json.loads(value)
        items.append(parse)
    else:
        items.append(value)

    return items


def label_filter(items, value):
    """
    Specification:
        LABEL <key>=<value> <key>=<value> <key>=<value> ...
        or
        LABEL "com.example.vendor"="ACME Incorporated"
        or
        LABEL com.example.label-without-value
        or
        LABEL com.example.label-with-value="foo"
    """

    for label in _key_value_splitter(value):
        split = label.split('=')
        if len(split) == 2:
            items[split[0]] = _strip_quote(split[1])
        else:
            items[label] = None

    return items


def expose_filter(items, value):
    """
    Specification:
        EXPOSE <port> [<port>...]
        or
        Open range of ports (Docker 1.5):
        EXPOSE <port-start>-<port-end>
    """

    if _detect(value, assumption='array'):
        for port in map(int, value[1:-1].split(', ')):
            items.append(port)
    else:
        if '-' in value:
            items.append(value)
        else:
            ports = value.split()
            if len(ports):
                for port in ports:
                    items.append(int(port))

    return items


def env_filter(items, value):
    """
    Specification:
        ENV <key> <value>
        ENV <key>=<value> ...
    """

    if '=' in value:
        for env in _key_value_splitter(value):
            variable, value = env.split('=')
            items[variable] = _strip_quote(value)
    else:
        split = _strip_backslash(value).split()
        if len(split) >= 2:
            variable, value = split[0], ' '.join(split[1:])
            items[variable] = _strip_quote(value)

    return items


def add_filter(items, value):
    """
    Specification:
        ADD <src>... <dest>
        or
        ADD ["<src>"... "<dest>"]
    """

    src, dest = value.split()
    items.append({'src': src, 'dest': dest})

    return items


def copy_filter(items, value):
    """
    Specification:
        COPY <src>... <dest>
        or
        COPY ["<src>"... "<dest>"]
    """

    src, dest = value.split()
    items.append({'src': src, 'dest': dest})

    return items


def entrypoint_filter(value):
    """
    Specification:
        ENTRYPOINT ["executable", "param1", "param2"]
        or
        ENTRYPOINT command param1 param2
    """

    if _detect(value, assumption='array'):
        parse = json.loads(value)
        return parse
    else:
        return value


def volume_filter(items, value):
    """
    Specification:
        VOLUME ["/data"]
        or if folder without spaces
        VOLUME /src
    """

    if _detect(value, 'array'):
        for item in json.loads(value):
            items.append(item)
    else:
        items.append(value)

    return items
