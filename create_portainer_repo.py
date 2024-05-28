#env

import os, requests, json, yaml
from pprint import pprint
from typing import TypedDict
from typing import List, Dict

import yaml



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

    # write to file
    with open('templates.json', 'w') as f:
        json.dump(repo, f, indent=4)
