IMAGE = kanboard/python-api-client
TAG = latest

docker-image:
	@ docker build -t $(IMAGE):$(TAG) .

docker-push:
	@ docker push $(IMAGE):$(TAG)

docker-destroy:
	@ docker rmi $(IMAGE):$(TAG)

all:
	docker-destroy docker-image docker-push
