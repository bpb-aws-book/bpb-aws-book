docker build -t inquisitivebookwormclubsiteimage .
docker image ls
docker run --name inquisitivebookwormclubsitecontainer -p 80:80 -d inquisitivebookwormclubsiteimage
curl localhost
docker tag inquisitivebookwormclubsiteimage:latest 111111111111.dkr.ecr.AWSREGION.amazonaws.com/bpbbook/inquisitivebookwormclubrepo 
aws ecr get-login-password --region AWSREGION | docker login --username AWS --password-stdin 111111111111.dkr.ecr. AWSREGION.amazonaws.com
docker push 111111111111.dkr.ecr. AWSREGION.amazonaws.com/bpbbook/inquisitivebookwormclubrepo
