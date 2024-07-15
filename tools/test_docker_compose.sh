#/bin/bash


# THis script going to get list of folders which are in the cookbook directory
# check if each folder/or subfolder there is file named starts from "docker-compose"
# if file exist - then create array with the name of the folder
# then run docker-compose config in each of this folders to check if syntax of docker compose is correct
#


# get list of folders in cookbook directory
cookbooks=()
for d in cookbook/composeStacks/*; do
  if [ -d "$d" ]; then
    cookbooks+=("$d")
    #echo "Starting $d"
  fi
done


# Check if docker compose didn't return error
# if return error - then brake script with exit 1
count=0
for path in "${cookbooks[@]}"; do
    if [ -d "$path" ]; then
        if [ -f "$path/docker-compose.yml" ]; then
            echo "Exam path: $path"
            if ! docker-compose  -f "$path/docker-compose.yml" config > /dev/null; then
                echo "Error: docker-compose config failed in $path"
                exit 1
            fi
            # add counter +!
            count=$((count+1))
            echo "--------------------"
        fi
    fi
done
echo "* DONE -------------"
echo "* Total: $count"
exit 0