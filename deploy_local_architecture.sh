docker build --push -t goterom/petconnect-be:develop .

ssh ec2-user@3.19.119.72 "cd /home/ec2-user/development; docker-compose down; docker-compose pull; docker-compose up -d"
