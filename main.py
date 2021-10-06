import json

variables_file = 'variables.json'
private_variables_file = 'private_variables.json'

with open(private_variables_file, 'r') as pv:
    token = json.load(pv)


def main():
    print('Hello world')


if __name__ == '__main__':
    main()
