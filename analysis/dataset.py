import os

docPath = "../results/"

def build_dataset():
    data = []
    label = []
    images = read_raw_data()
    for image in images:
        words = ""
        for command in images[image]:
            words = words + " " + clean_data(command)
        data.append(words)
        label.append(image)

    return data, label


# TODO: it is a test version
def clean_data(words_list):
    doc = ""

    # pass parametes
    for word in words_list:
        if "apt-get" == word or "apt" == word or "install" == word or "yum" == word or "git" == word:
            continue
            
        if not word.startswith("-") and len(word) < 15:
            try:
                tmp = int(word)
            except:
                doc = doc + " " + word
    
    return doc

def read_raw_data():
    paths = []
    files = os.walk(docPath)  
    for path, dirs, files in files:  
        for file in files:
            paths.append(os.path.join(path, file))

    images = {}
    for path in paths:
        with open(path, "r") as log:
            lines = log.readlines()
            for info in lines:
                info = info.strip()
                try:
                    image = info.split("; ", 1)[0]
                    cmds = []
                    # commands
                    for items in info.split("; ", 1)[1].strip("[]").split("], ["):
                        cmd = []
                        # words and paras
                        for item in items.split(", "):
                            cmd.append(item.strip("'"))
                        cmds.append(cmd)
                    images[image] = cmds
                except:
                    continue

    return images

#print(len(read_data()))