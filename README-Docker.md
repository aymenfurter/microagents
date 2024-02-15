#  Docker instructions


## How to build the Docker image

```bash	
docker build -t microagents:latest .
```


## How to run the Docker container

1. Create the persistance directory
    ```bash	
    mkdir -p persistance
    # optionally copy agents.db to persistance
    cp agents.db persistance/
    ```
1. Run the Docker container
    - In case you want to use Open AI API:
        ```sh
        docker run -it --rm \
              -e OPENAI_KEY='your_api_key_here' \
              -v "$(pwd)/persistance:/usr/src/app/persistance" \
              -p "7860:7860" \
              microagents:latest
        ```
    - In case you want to use Azure Open AI with api key:
        ```sh
        docker run -it --rm \
              -e AZURE_OPENAI_API_KEY='your_api_key_here' \
              -e AZURE_OPENAI_ENDPOINT='https://my_endpoint_name_here.openai.azure.com/' \
              -e OPENAI_EMBEDDING='text-embedding-ada-002' \
              -e OPENAI_MODEL='gpt-4-1106-preview' \
              -v "$(pwd)/persistance:/usr/src/app/persistance" \
              -p "7860:7860" \
              microagents:latest
        ```
    - In case you want to use Azure Open AI with Entra ID (AAD):
        ```sh
        docker run -it --rm \
              -e AZURE_OPENAI_USE_AAD='true' \
              -e AZURE_OPENAI_AD_TOKEN="$(az account get-access-token --scope "https://cognitiveservices.azure.com/.default" --query 'accessToken' -o tsv)" \
              -e AZURE_OPENAI_ENDPOINT='https://my_endpoint_name_here.openai.azure.com/' \
              -e OPENAI_EMBEDDING='text-embedding-ada-002' \
              -e OPENAI_MODEL='gpt-4-1106-preview' \
              -v "$(pwd)/persistance:/usr/src/app/persistance" \
              -p "7860:7860" \
              microagents:latest
        ```


