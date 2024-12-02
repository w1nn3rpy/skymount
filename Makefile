build:
	docker build -t skymount_image .
run:
	docker run -it -d --env-file .env --restart=unless-stopped --name skymount_bot skymount_image
stop:
	docker stop skymount_bot
attach:
	docker attach skymount_bot
dell:
	docker rm skymount_bot
	docker image remove skymount_image
update:
	make stop
	make dell
	make build
	make run