#################### filter keywords in dockerfile #################

# unwanted commands in docker build history
meaningless_words = [
    "set -ex",
    "set -eux",
    "exit 101",
]

# paras "wordsList" is a string
# paras "rule": and means all in, or means one in
def exsit(text, wordsList, rule):
    words = vars()[wordsList]

    if rule == "or":
        for word in words:
            if word in text:
                return True
        return False
    
    elif rule == "and":
        for word in words:
            if word not in text:
                return False
        return True