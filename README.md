# STT+SER with GPU on Google Cloud Run

## Overview
This project shows an example API, which performs Speech Emotion Recognition (SER)
and Speech To Text (STT) in parallel with GPUs. This is useful if you want to 
translate speech to text and analyze the emotional tone of the speaker at the 
same time. 

This API is simple in the sense, that all it does is just call two other APIs, 
joins there responses, and returns them as one response. 

This project builds on top of two previous ones, which are:
- Whisper STT on GPU: https://github.com/fentresspaul61B/Deploy-Whisper-On-GCP
- SER on GPU: https://github.com/fentresspaul61B/SER-with-GPU

How it works:

1. Takes in a single audio file as an argument to the API.
2. Generates a GCP tokens from within the GCP Cloud Run Server. 
3. Use Async Gather method to call both APIs at the same with their respective 
tokens. 
4. Join and return the responses. 

## Running the API
The steps to run the API are exactly the same for this API as they are
for the SER and STT APIs. The instructions to run the API locally without docker, locally with docker, as well as the the deployed API are outlined in detail here: 

### FOLLOW STEPS OUTLINE HERE:
https://github.com/fentresspaul61B/SER-with-GPU

Caveat: One caveat here is that if you would like to run the API locally use the ```translate_local``` endpoint instead of the ```translate``` endpoint. The reason there are two separate endpoints, is because generating tokens locally and when inside a GCP environment require different processes. 

If you fail to generate valid tokens locally, you likely are not authenticated with the correct GCP service account locally. 

You can use these docs to figure out how to authenticate locally:
https://cloud.google.com/docs/authentication/gcloud


## Challenges 
The biggest challenge that I ran into, was how to call a GCP API from inside
another GCP API. I tried 3 ways of solving this, but only one worked. 

1. ⚠️ Passing the token from the orchestrator API to the two sub APIs: Failed due 
to permissions issues. 
2. ⚠️ Downloading and invoking the GCP CLI. This failed as well, as I struggled to download and utilize the CLI tool from within
the GCP env. This was also likely redundant as the GCP env is already authenticated with a service account, which is required for deployment.
3. ✅ Use the Google Auth Python Package: Worked! There is a specific function 
created for generating tokens while inside a GCP cloud environment. The docs 
are here: https://googleapis.dev/python/google-auth/latest/user-guide.html#identity-tokens 

    ```python
    def generate_token_in_gcp_env(url: str):
        """This function generates a token while inside GCP cloud run."""
        auth_req = google.auth.transport.requests.Request()
        id_token = google.oauth2.id_token.fetch_id_token(auth_req, url)
        return id_token


    ```

I am glad that I found this specific token method, as I always struggled with this problem of figuring out how to orchestrate GCP APIs and dealing with 
permissions issues in the different environments, but this solves that 
issue. Using this method also avoids needing to upload any auth secrets required for service accounts, which can be headache and bad for security purposes. 

