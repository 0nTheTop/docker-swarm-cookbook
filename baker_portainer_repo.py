#!/usr/bin/env python3

import sys
sys.dont_write_bytecode = True

import os, requests, json, yaml
from pprint import pprint
from typing import TypedDict
from typing import List, Dict
from config import ConfigReader

import yaml, re, random, string
from cryptography.fernet import Fernet

cr = ConfigReader()
GITHUB_URL = cr.read_config("github.yaml")['github_url']
GITHUB_URL_CONTENT = cr.read_config("github.yaml")['github_url_content']
REF_CATEGORIES = cr.read_config("categories.yaml")


def generate_key(key_type):
  if key_type == "-fernet-":
    return Fernet.generate_key().decode() 
  elif key_type == "-random-": 
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16)) 
  elif key_type.startswith("-random-") and key_type.endswith("-"):
    try:
      length = int(key_type[8:-1]) 
      return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
    except ValueError:
      return key_type 
  else:
    return key_type 

def read_config(file_path):
    # Check if file_path exist/if not - then check if it is just file name and if it exist in config folder
    if not os.path.exists(file_path):
        file_path = os.path.join("config", file_path)

    # read local json file and return as dict
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
        return data


def standardize_categories(categories):
  correct_categories = []
  for category in categories:
    found = False
    for correct_name, variations in REF_CATEGORIES.items():
      if category in variations:
        correct_categories.append(correct_name)
        found = True
        break
    if not found:
      correct_categories.append(category)
  return correct_categories


class PortainerRepos():
    def __init__(self) -> None:
        cr = ConfigReader()
        self.templates_folder_path = os.path.join("downloaded-collections", "templates")
        self.urls = cr.read_config("repos.yaml")['repos']
        
        
    def download(self):
        for url in self.urls:
            r = requests.get(url['url'])
            print(f"Save file: {self.templates_folder_path}/" + url['filename'])
            with open(os.path.join(self.templates_folder_path, url['filename']), 'w') as f:
                f.write(r.text)

    def repos(self) -> List[str]:
        ret = []
        for url in self.urls:
            r = {}
            r['name'] = url['source']
            path = os.path.join(self.templates_folder_path, url['filename'])
            # check if file exist
            if os.path.exists(path):
                r['file'] = path
            else:
                continue

            ret.append(r)
        return ret
            

    def decompress_template(self, file_path):
        #read local json file and return as dict
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data

def capitalize_first_letter(names):
  return [name.capitalize() for name in names] 
        
def cookbook(type_id):
    ret = []
    if type_id == 1:
        cookbook_folder = "containers"
        folder_path = os.path.join("cookbook", cookbook_folder)
        stack_file_name = None
    if type_id == 2:
        cookbook_folder = "swarmStacks"
        folder_path = os.path.join("cookbook", cookbook_folder)
        stack_file_name = "docker-stack.yml"
    if type_id == 3:
        cookbook_folder = "composeStacks"
        folder_path = os.path.join("cookbook", cookbook_folder)
        stack_file_name = "docker-compose.yml"
    
    # list all folders
    folders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
    # check if in each folder exis a info.yaml
    for project_folder in folders:
        path = os.path.join(folder_path, project_folder, "info.yaml")
        data = {}
        if os.path.exists(path):
            # read info.yaml
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                
        # Title
        # if inside data not exist title... then setup based on project_folder name
        if 'title' not in data:
            # This field must consist of lower-case alphanumeric characters, '_' or '-'
            data['title'] = '-'.join(word.capitalize() or '_' for word in project_folder.split('_|-')).replace('_', ' ').replace('-', ' ')
        else:
            data['title'] = str(data['title'])
            
        # Repository
        if 'repository' not in data:
            data['repository'] = {}
            data['repository']['url'] = GITHUB_URL
            data['repository']['stackfile'] = f"cookbook/{cookbook_folder}/{project_folder}/{stack_file_name}"
        
        # Name
        if 'name' not in data:
            data['name'] = str(data['title']).lower().replace(' ', '_').replace('_', '-')
        
        # Categories
        if 'categories' not in data:
            data['categories'] = []
        data['categories'] = standardize_categories(data['categories'])
        if 'Cookbook' not in data['categories']:
            data['categories'].append("Cookbook")

        
        # Type
        if 'type' not in data:
            data['type'] = int(type_id)

        # Platform
        if 'platform' not in data:
            data['platform'] = 'linux'
        
        # Logo
        if 'logo' not in data:
            if os.path.exists(os.path.join("icons", f"{project_folder}.png")):
                data['logo'] = f"{GITHUB_URL_CONTENT}main/icons/{project_folder}.png"
            else:
                data['logo'] = ''
        
        # Desription
        if 'description' not in data:
            data['description'] = project_folder.replace("_", " ")
        
        # Source
        if 'source' in data:
            del data['source']
            
        # Labels
        if 'labels' in data:
            for label_element in data.get('labels'):
                if 'value' in label_element and type(label_element['value']) == int:
                    label_element['value'] = str(label_element['value'])
                if 'value' in label_element and type(label_element['value']) == bool:
                    if label_element['value'] is True:
                        label_element['value'] = "true"
                    if label_element['value'] is False:
                        label_element['value'] = "false"
                    
        # Environment
        if 'env' not in data:
            data['env'] = []
        for env_element in data['env']:
            if 'default' in env_element and type(env_element['default']) == int:
                env_element['default'] = str(env_element['default'])
                
            if 'default' in env_element and type(env_element['default']) == bool:
                if env_element['default'] is True:
                    env_element['select'] = [{ "text": "True", "value": "true", "default": True }, { "text": "False", "value": "false" }]
                if env_element['default'] is False:
                    env_element['select'] = [{ "text": "True", "value": "true" }, { "text": "False", "value": "false", "default": True  }]
                del env_element['default']
            
            # if element contains | - then it is list where first element is default and rest are options
            if "default" in env_element and type(env_element['default']) == str and '|' in env_element['default']:
                list_elements = env_element['default'].split("|")
                del env_element['default']
                env_element['select'] = []
                for option in list_elements:
                    env_element['select'].append({ "text": option, "value": option })
                env_element['select'][0]['default'] = True
                if env_element.get('description'):
                    env_element['description'] = f"{env_element['description']} Default: {env_element['select'][0]['text']}"

            if env_element.get('default') and env_element.get('default').startswith("-") and env_element.get('default').endswith("-"):
                env_element['default'] = generate_key(env_element['default'])

            if 'label' not in env_element and not env_element.get('preset'):
                env_element['label'] = env_element['name']
                
            if env_element.get('name') == 'TZ' and env_element.get('label') == 'Time-Zone':
                if data.get('note'):
                    data['note'] = f"{data['note']} <br> <br> <a href=\"{GITHUB_URL_CONTENT}main/timezones.txt\" target=\"_blank\">timedatectl list-timezones</a> to see all timezones"
                else:
                    data['note'] = "<br><a href=\"{GITHUB_URL_CONTENT}main/timezones.txt\" target=\"_blank\">timedatectl list-timezones</a> to see all timezones"
        
        # Categories
        data['categories'] = capitalize_first_letter(data['categories'])
        
        # Title
        data['title'] = f"{data['title']} (Cookbook)"
        
        ret.append(data)
    return ret

def cookbook_containers():
    return cookbook(1)

def cookbook_swarmStack():
    return cookbook(2)

def cookbook_composeStack():
    return cookbook(3)
    
        
if __name__ == "__main__":
    featch = PortainerRepos()
    featch.download()
    ext_repos = featch.repos()

    repo = {"version": "3", "templates": []}
    id = 1
    for ext_repo in ext_repos:
        data = featch.decompress_template(ext_repo['file'])
        print(f"Repo: {ext_repo['name']} - {len(data['templates'])}")
        for template in data['templates']:
            template['id'] = id
            template['title'] = f"{template['title']} ({ext_repo['name']})"
            if 'categories' not in template:
                template['categories'] = []
            if "Cookbook" not in template['categories']:
                template['categories'].append(ext_repo['name'])
            template['categories'] = capitalize_first_letter(template['categories'])
            template['categories'] = standardize_categories(template['categories'])
            repo['templates'].append(template)
            id = id + 1

    cookbook_id_start = id
    # add cookbooks(1)
    cbook_containers = cookbook_containers()
    print(f"Cookbook: containers - {len(cbook_containers)}")
    for cbook in cbook_containers:
        cbook['id'] = id
        repo['templates'].append(cbook)
        id = id + 1


    # add cookbooks(2)
    cbook_swarm = cookbook_swarmStack()
    print(f"Cookbook: swarmStack - {len(cbook_swarm)}")
    for cbook in cbook_swarm:
        cbook['id'] = id
        repo['templates'].append(cbook)
        id = id + 1

    # add cookbooks(3)
    cbook_compose = cookbook_composeStack()
    print(f"Cookbook: composeStack - {len(cbook_compose)}")
    for cbook in cbook_compose:
        cbook['id'] = id
        repo['templates'].append(cbook)
        id = id + 1

    # write to file all repos
    with open('templates.json', 'w') as f:
        json.dump(repo, f, indent=4)

    # write to file only cookbooks records
    cookbook_repo = {"version": "3", "templates": []}
    cookbook_repo_id = 1
    for r in repo['templates']:
        if r['id'] >= cookbook_id_start:
            cbr = r
            cbr['id'] = cookbook_repo_id
            cookbook_repo['templates'].append(cbr)
            cookbook_repo_id+=1
            
    with open('templates_cookbook.json', 'w') as f:
        json.dump(cookbook_repo, f, indent=4)
        
    