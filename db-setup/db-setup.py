import json


def main():
    json_data = None
    try:
        with open('/home/config.json', 'r') as f:
            json_data = json.load(f)
    except IOError:
        print("Error: no config file found")


if __name__ == "__main__":
    main()
