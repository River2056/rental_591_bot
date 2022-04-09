import yaml
import os

def main():
    with open(os.path.join('./config', 'config.yaml')) as file:
        config = yaml.safe_load(file.read())
        print(config)
        print(config['element-count'])

if __name__ == '__main__':
    main()
