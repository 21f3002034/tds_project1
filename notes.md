# GIT STARTING
```bash
git config --global user.name "21f3002034"

git config --global user.email "21f3002034@ds.study.iitm.ac.in"

git remote add tds_project1 https://github.com/21f3002034/tds_project1.git
```
# PODMAN
```powershell
# building new docker image
podman build -t tds_project .
podman images
# running the image with image id b0aaad927709
podman run -p 5000:8000 1452c59bcedb 
podman run -p  5000:8000 -e AIPROXY_TOKEN="eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIxZjMwMDIwMzRAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.KEQjxQbjAIHY8_0l-WpiOL_KrBslnPTFZnexib9N6qc" 4c1cbcb0a96d

podman rmi 1452c59bcedb

# looking for running containers with container id
podman ps
podman ps -a  
# starting or stopping or logs of container with container id
podman stop <container id>
podman start <container id>
podman logs <container id>

podman stop b4e55529fe1b
podman rm b4e55529fe1b

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
```

export AIPROXY_TOKEN="eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIxZjMwMDIwMzRAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.KEQjxQbjAIHY8_0l-WpiOL_KrBslnPTFZnexib9N6qc"
