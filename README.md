# docker-swarm-cookbook
Docker Swarm Cookbook Collection












## Rules:

### Services
#### Always:
- Always add a name to container services
- Always add a container_name to container services (excluding swarmStacks which not allow this)
- Always conainer_name must include project name ie. <project>-<service>
- Always add a restart policy to container services
- Always use a volume to container services

#### Try:
- Try to add a healthcheck to container services
- Try to add traefik label to container services which should be access in public network
- Try to add a network to container services

### Volume
1) Create a volume always with a name
2) Use syntax naming convention for volume: <project>-<service>-<volume> ie. langflow-postgres-data
