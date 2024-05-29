#env

import os, requests, json, yaml
from pprint import pprint
from typing import TypedDict
from typing import List, Dict

import yaml, re



class PortainerRepos():
    def __init__(self) -> None:
        self.templates_folder_path = os.path.join("downloaded-collections", "templates")
        self.urls = [ 
            {"url": "https://raw.githubusercontent.com/portainer/templates/v3/templates.json", "filename": "portainer_templates.json", "source": "portainer"},
            {"url": "https://raw.githubusercontent.com/Lissy93/portainer-templates/main/templates.json", "filename": "lissy93_templates.json", "source": "lissy93"},
            ]

    def download(self):
        for url in self.urls:
            r = requests.get(url['url'])
            print(f"Save file: {self.templates_folder_path}/" + url['filename'])
            with open(self.templates_folder_path + url['filename'], 'w') as f:
                f.write(r.text)

    def repos(self) -> List[str]:
        ret = []
        for url in self.urls:
            r = {}
            r['name'] = url['source']
            path = self.templates_folder_path + url['filename']
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
        
        
def cookbook_swarms():
    ret = []
    folder_path = os.path.join("cookbook", "swarm")
    # list all folders
    folders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
    # check if in each folder exis a info.yaml
    for folder in folders:
        path = os.path.join(folder_path, folder, "info.yaml")
        data = {}
        if os.path.exists(path):
            # read info.yaml
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
        # if inside data not exist title... then setup based on folder name
        if 'title' not in data:
            # This field must consist of lower-case alphanumeric characters, '_' or '-'
            data['title'] = folder.replace(' ', '_').lower()
            
        if 'repository' not in data:
            data['repository'] = {}
            data['repository']['url'] = "https://github.com/azdolinski/docker-swarm-cookbook"
            data['repository']['stackfile'] = f"cookbook/swarm/{folder}/docker-stack.yml"
        
        if 'type' not in data:
            data['type'] = 2

        if 'platform' not in data:
            data['platform'] = 'linux'
            
        if 'logo' not in data:
            data['logo'] = ''
            
        if 'description' not in data:
            data['description'] = folder.replace("_", " ")
        
        if 'source' in data:
            del data['source']
        
        data['title'] = re.sub(r'\w(?<![-_a-z0-9])', '', data['title'].lower())
       
        ret.append(data)
    return ret
        
        
if __name__ == "__main__":
    featch = PortainerRepos()
    featch.download()
    ext_repos = featch.repos()
    print(ext_repos)
    
    repo = {"version": "3", "templates": []}
    id = 0
    for ext_repo in ext_repos:
        data = featch.decompress_template(ext_repo['file'])
        for template in data['templates']:
            template['id'] = id
            template['title'] = f"{template['title']} ({ext_repo['name']})"
            repo['templates'].append(template)
            id = id + 1

    cbook_swarm = cookbook_swarms()
    for cbook in cbook_swarm:
        cbook['id'] = id
        repo['templates'].append(cbook)
        id = id + 1

    # write to file
    with open('templates.json', 'w') as f:
        json.dump(repo, f, indent=4)
