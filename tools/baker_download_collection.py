#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True

import os, requests, json, yaml
from pprint import pprint
from typing import TypedDict
from typing import List, Dict

import yaml
from config import ConfigReader

CURRENT_FILE_PATH = os.path.dirname(os.path.realpath(__file__))

cr = ConfigReader(os.path.join(CURRENT_FILE_PATH, "config"))
GITHUB_URL = cr.read_config("github.yaml")['github_url']
GITHUB_URL_CONTENT = cr.read_config("github.yaml")['github_url_content']
LOGOS = f"{GITHUB_URL_CONTENT}main/icons/"
DOWNLOADED_FOLDER = '../downloaded-collections'

class Volume(Dict[str, str]):
    container: str

class EnvVar(Dict[str, str]):
    name: str
    default: str
    preset: bool

class Repository:
    url: str
    stackfile: str
    
    
class PortainerContainer(TypedDict):
    id: int
    type: int = 1
    title: str
    description: str
    categories: List[str]
    platform: str
    logo: str
    image: str
    ports: List[str]
    volumes: List[Dict[str, str]]
    env: List[Dict[str, str]]
    command: str

class PortainerSwarmStack:
    id: int
    type: int = 2
    title: str
    name: str
    description: str
    note: str
    categories: List[str]
    platform: str
    logo: str
    repository: Repository

class PortainerComposeStack(TypedDict):
    id: int
    type: int = 3
    title: str
    description: str
    note: str
    categories: List[str]
    platform: str
    logo: str
    repository: Repository
    env: List[EnvVar]

class IconManager():
    def __init__(self) -> None:
        pass
    
    def download_logo(self, url: str, filename: str = None) -> None:
        if filename is None:
            filename = url.split("/")[-1]
        _, ext = os.path.splitext(filename)
        if ext.lower() not in [".png", ".jpg", ".jpeg"]:
            return
        
        icons_path = os.path.join(DOWNLOADED_FOLDER, "icons", filename.lower())
        # check if icons folder exists
        if not os.path.exists(os.path.dirname(icons_path)):
            os.makedirs(os.path.dirname(icons_path))

        # check if file already exists
        if os.path.exists(icons_path):
            print("File already exists:", icons_path)
            return
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(icons_path, 'wb') as f:
                    f.write(response.content)
        except Exception as e:
            print("Error downloading logo:", e)
            pass
        
            

class ExternalTemplate():
    def __init__(self) -> None:
        self.downloaded_folder = os.path.join(DOWNLOADED_FOLDER)
        self.templates_folder = os.path.join(DOWNLOADED_FOLDER, "templates")
        self.urls = [ 
            {"url": "https://raw.githubusercontent.com/portainer/templates/v3/templates.json", "filename": "portainer_templates.json", "source": "portainer"},
            {"url": "https://raw.githubusercontent.com/Lissy93/portainer-templates/main/templates.json", "filename": "lissy93_templates.json", "source": "lissy93"},
            {"url": "https://raw.githubusercontent.com/xneo1/portainer_templates/master/Template/template.json", "filename": "xneo1_templates.json", "source": "xneo1"},
            ]

    def download_files(self, urls=None, folder_name=None):
        if folder_name is None:
            folder_name = self.templates_folder
            
        if urls is None:
            urls = self.urls
        
        os.makedirs(folder_name, exist_ok=True)

        for repository in urls:
            url = repository['url']
            filename = repository['filename']
            file_path = os.path.join(folder_name, filename)

            r = requests.get(url)
            with open(file_path, 'wb') as f:
                f.write(r.content)

    def decompress_template(self, source_name):
        templates = []
        for repository in self.urls:
            if repository['source'] == source_name:
                url = repository['url']
                r = requests.get(url)
                if r.status_code == 200:
                    templates = r.json()['templates']
                else:
                    print(f"Failed to retrieve template from {url}. Status code: {r.status_code}")
        
        for template in templates:
            # Add source to keep trace of where the template came from
            template['source'] = source_name
            
            # Synthesize the title from the template name
            title = template['title'].replace(" ", "_").replace("(", "").replace(")", "")
            print(f"{source_name}\{title}")
            
            # Save the logo icons
            if template.get('logo'):
                im = IconManager()
                im.download_logo(url=template['logo'])
            
            full_title = f"{title} ({source_name})"
            # Save the template based on type
            if template['type'] == 1:
                self.save_container(template, full_title)
                
            elif template['type'] == 2:
                self.save_swarm(template, full_title)
                
            elif template['type'] == 3:
                self.save_compose(template, full_title)
                
           # create_template(template['path'])

    def save_container(self, template, title):            
        # Create the directory structure if it doesn't exist
        directory = os.path.join(self.downloaded_folder, "containers", title)
        os.makedirs(directory, exist_ok=True)

        # Save the template as info.yaml in YAML format
        with open(os.path.join(directory, "info.yaml"), "w") as f:
            yaml.dump(template, f, indent=4)
           
    def save_swarm(self, template, title):
        directory = os.path.join(self.downloaded_folder, "swarmStacks", title)
        os.makedirs(directory, exist_ok=True)

        with open(os.path.join(directory, "info.yaml"), "w") as f:
            yaml.dump(template, f, indent=4)
           
            if template.get('repository'):
                url = template['repository']['url'].replace("github.com", "raw.githubusercontent.com") + "/master/" + template['repository']['stackfile']
                r = requests.get(url)
                if r.status_code == 200:
                    print(url)
                    with open(os.path.join(directory, "docker-stack.yml"), 'wb') as f:
                        f.write(r.content)
                else:
                    print(f"Failed to retrieve template from {url}. Status code: {r.status_code}")
                    
                    
    def save_compose(self, template, title):
        directory = os.path.join(self.downloaded_folder, "composeStacks", title)
        os.makedirs(directory, exist_ok=True)
        
        with open(os.path.join(directory, "info.yaml"), "w") as f:
            yaml.dump(template, f, indent=4)
           
            if template.get('repository'):
                url = template['repository']['url'].replace("github.com", "raw.githubusercontent.com") + "/master/" + template['repository']['stackfile']
                r = requests.get(url)
                if r.status_code == 200:
                    print(url)
                    with open(os.path.join(directory, "docker-compose.yml"), 'wb') as f:
                        f.write(r.content)
                else:
                    print(f"Failed to retrieve template from {url}. Status code: {r.status_code}") 
    
def list_of_folders(path):
    folders = {}  # Initialize an empty dictionary to store folder data

    for item in os.listdir(path):
        item_path = os.path.join(path, item)  # Get the full path of the item
        folders[item] = {}
        
        
        if os.path.isdir(item_path):
            # If the item is a directory, get a list of files within that directory
            files_in_folder = [
                f for f in os.listdir(item_path) if os.path.isfile(os.path.join(item_path, f))
            ]
            folders[item]['files'] = files_in_folder  # Add the folder and its files to the dictionary

            if "info.yaml" in files_in_folder:
                folders[item]['info'] = read_info_yaml(os.path.join(item_path, "info.yaml"))

    return folders

def read_info_yaml(file="info.yaml"):
    with open(file, "r") as f:
        data = yaml.safe_load(f)
    return data

def search_logo_local(name):
    for d in os.listdir("logos"):
        if name in d:
            return os.path.join(LOGOS, d)

def create_template(file_path):
    template = {}
    template['version'] = 3
    template['templates'] = []
    
    with open(file_path, 'w') as f:
        json.dump(template, f, indent=4)
    
      
if __name__ == "__main__":
    featch = ExternalTemplate()
    featch.download_files()

    a = featch.decompress_template('portainer')
    print(a)
    a = featch.decompress_template('lissy93')
    print(a)
    exit()
    swarm_folders = list_of_folders("swarm")
    pprint(swarm_folders, indent=4, compact=True)
    
    create_template("templates/templates.json")