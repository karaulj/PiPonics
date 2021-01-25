import json


def main():

    from os import listdir
    from os.path import isfile, join
    mypath = "/home"
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    print(onlyfiles)

    json_data = None
    try:
        with open('/home/config.json', 'r') as f:
            json_data = json.load(f)
            print(json_data)
    except IOError:
        print("Error: no config file found")

    try:
        with open('/sql/db-init-test.sql', 'x') as f:
            f.write("test content")
    except FileExistsError:
        print("Error: db-init file already exists")

if __name__ == "__main__":
    main()
