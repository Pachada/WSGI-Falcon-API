### Pasos para levantar un Lambda con Zappa

1. **Instalar AWS CLI**: [AWS CLI Installation Guide](https://aws.amazon.com/cli/)

2. **Configurar AWS CLI**:
   - Ejecutar el comando:
     ```sh
     aws configure
     ```

3. **Crear y configurar el entorno de Python**:
   - Crear una carpeta para el proyecto y navegar a ella.
   - Ejecutar los siguientes comandos:
     ```sh
     pipenv --python python3
     pipenv shell
     pipenv install -r requirements.txt
     ```

4. **Inicializar y desplegar con Zappa**:
   - Ejecutar el comando para inicializar Zappa y seguir las instrucciones:
     ```sh
     zappa init
     ```
   - Desplegar o actualizar el proyecto:
     ```sh
     zappa deploy <name>
     zappa update <name>
     ```

5. **Configurar acceso a RDS**:
   - Dar acceso a la RDS desde la configuración en la Lambda.

### Zappa con Docker

1. **Guía de Zappa con Docker**: [Zappa Serverless Docker Guide](https://ianwhitestone.work/zappa-serverless-docker/)

2. **Ejemplo de Dockerfile para Zappa**:
   ```dockerfile
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
   ```

### Comandos adicionales para Docker y Zappa

- **Test Lambda localmente**:
  ```sh
  docker run --platform linux/amd64 -p 9000:8080 falcon_api:falcon_api
  ```

- **PowerShell**:
  ```sh
  Invoke-WebRequest -Uri "http://localhost:9000/2015-03-31/functions/function/invocations" -Method Post -Body '{}' -ContentType "application/json"
  ```

- **Zappa**:
  ```sh
  zappa save-python-settings-file lambda_docker_falcon -o zappa_settings.py
  ```

- **Build Docker image**:
  ```sh
  docker build -t falcon_api:falcon_api .
  ```

- **Test Docker image**:
  ```sh
  docker run -p 9000:8080 falcon_api:falcon_api
  ```

- **Call API**:
  ```sh
  curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"path": "/v1/health-check/ping", "httpMethod": "GET", "requestContext": {}, "body": null}'
  ```

- **Login to ECR**:
  ```sh
  aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin XXXXX.dkr.ecr.us-east-2.amazonaws.com
  ```

- **Tag Docker image**:
  ```sh
  docker tag falcon_api:falcon_api XXXXX.dkr.ecr.us-east-2.amazonaws.com/{{ECR_NAME}}:falcon_api
  ```

- **Push Docker image**:
  ```sh
  docker push XXXXX.dkr.ecr.us-east-2.amazonaws.com/{{ECR_NAME}}:falcon_api
  ```

- **Deploy Zappa**:
  ```sh
  zappa deploy lambda_docker_falcon -d XXXXX.dkr.ecr.us-east-2.amazonaws.com/{{ECR_NAME}}:falcon_api
  ```

- **Update Zappa**:
  ```sh
  zappa update lambda_docker_falcon -d XXXXX.dkr.ecr.us-east-2.amazonaws.com/{{ECR_NAME}}:falcon_api
  ```

### Quitar un entorno Pipenv actual
```sh
pipenv --rm
```