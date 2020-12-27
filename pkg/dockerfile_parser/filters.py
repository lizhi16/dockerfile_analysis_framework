import json

from collections import OrderedDict


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
