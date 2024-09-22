# Use public AWS Lambda Python image
FROM public.ecr.aws/lambda/python:3.10

WORKDIR ${LAMBDA_TASK_ROOT}

COPY ./ .

# Install any needed packages specified in requirements.txt
RUN pip install -r setup/requirements.txt

# Grab the zappa handler.py and put it in the working directory
RUN ZAPPA_HANDLER_PATH=$( \
    python -c "from zappa import handler; print (handler.__file__)" \
    ) \
    && echo $ZAPPA_HANDLER_PATH \
    && cp $ZAPPA_HANDLER_PATH .

CMD [ "handler.lambda_handler" ]

# test lambda locally: 
    # docker run --platform linux/amd64 -p 9000:8080 falcon_api:falcon_api
    # linux : 
    # PowerShell: Invoke-WebRequest -Uri "http://localhost:9000/2015-03-31/functions/function/invocations" -Method Post -Body '{}' -ContentType "application/json"

# zappa: zappa save-python-settings-file lambda_docker_falcon -o zappa_settings.py
# build: docker build -t falcon_api:falcon_api .
# test: docker run -p 9000:8080 falcon_api:falcon_api  
# call: curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"path": "/api/health-check/ping", "httpMethod": "GET", "requestContext": {}, "body": null}'
# login ecr: aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin XXXXX.dkr.ecr.us-east-2.amazonaws.com
# tag: docker tag falcon_api:falcon_api XXXXX.dkr.ecr.us-east-2.amazonaws.com/{{ECR_NAME}}:falcon_api
# push: docker push XXXXX.dkr.ecr.us-east-2.amazonaws.com/{{ECR_NAME}}:falcon_api
# deploy zappa: zappa deploy lambda_docker_falcon -d XXXXX.dkr.ecr.us-east-2.amazonaws.com/{{ECR_NAME}}:falcon_api
# update zappa: zappa update lambda_docker_falcon -d XXXXX.dkr.ecr.us-east-2.amazonaws.com/{{ECR_NAME}}:falcon_api