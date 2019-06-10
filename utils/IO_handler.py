import os

def readfiles(dir_name):
    documents = []
    for file_name in os.listdir(dir_name):
        try:
            with open(os.path.join(dir_name, file_name)) as file:
                text = file.read()
                documents.append([int(file_name.split('.')[0]), text])
        except Exception as e:
            print(e)
            print(file_name)
    return documents


