# GIT STARTING
```bash
git config --global user.name "21f3002034"

git config --global user.email "21f3002034@ds.study.iitm.ac.in"

git remote add tds_project1 https://github.com/21f3002034/tds_project1.git
```
# PODMAN
```powershell
# building new docker image
podman build -t tds_project_final .
podman images
# running the image with image id b0aaad927709
podman run -p 5000:8000 1452c59bcedb 
podman run -p  5000:8000 -e AIPROXY_TOKEN="eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIxZjMwMDIwMzRAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.KEQjxQbjAIHY8_0l-WpiOL_KrBslnPTFZnexib9N6qc" f8564636db7c

podman rmi 1452c59bcedb

# looking for running containers with container id
podman ps
podman ps -a  
# starting or stopping or logs of container with container id
podman stop <container id>
podman start <container id>
podman logs <container id>

podman stop b679ecf5055a
podman rm b679ecf5055a

podman stop 661f5bf70fe0
podman rm 661f5bf70fe0
# container is like virtual machine that is isolated from local windows or other os

# pushing the image to docker hub website
docker push b0aaad927709 raghuvasanth/ds_project1_docker:tagname
podman pull raghuvasanth/ds_project1_docker:tagname
```
# running app with token
```powershell
uv run app.py AIPROXY_TOKEN='eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIxZjMwMDIwMzRAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.KEQjxQbjAIHY8_0l-WpiOL_KrBslnPTFZnexib9N6qc'
uv run app.py AIPROXY_TOKEN=$AIPROXY_TOKEN
uv run EVAL.py --email 21f3002034@ds.study.iitm.ac.in
```

export AIPROXY_TOKEN="eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIxZjMwMDIwMzRAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.KEQjxQbjAIHY8_0l-WpiOL_KrBslnPTFZnexib9N6qc"
uvicorn app:app --host localhost --port 8000 --reload AIPROXY_TOKEN=$AIPROXY_TOKEN

>https://github.com/21f3002034/tds_project1
>raghuvasanth/tds_project1_docker:v1


# Docker Hub
```powershell
podman login docker.io
podman tag <IMAGE_ID> docker.io/<YOUR_DOCKER_USERNAME>/<IMAGE_NAME>:<TAG>
podman push docker.io/<YOUR_DOCKER_USERNAME>/<IMAGE_NAME>:<TAG>
podman tag e43f066c0ba0 docker.io/raghuvasanth/tds_project1_docker:final
podman push docker.io/raghuvasanth/tds_project1_docker:final
```
git push --force origin main
