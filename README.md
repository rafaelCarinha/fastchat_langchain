First, launch the controller

```
$ python3 -m fastchat.serve.controller
```

LangChain uses OpenAI model names by default, so we need to assign some faux OpenAI model names to our local model. Here, we use Vicuna as an example and use it for three endpoints: chat completion, completion, and embedding. --model-path can be a local folder or a Hugging Face repo name

```
$ python3 -m fastchat.serve.model_worker --model-names "gpt-3.5-turbo" --model-path lmsys/vicuna-7b-v1.3 --num-gpus 4
```

Launch the RESTful API server

```
$ python3 -m fastchat.serve.openai_api_server --host localhost --port 8000
```

Set OpenAI base url

```
$ export OPENAI_API_BASE=http://localhost:8000/v1
```

Set OpenAI API key

```
$ export OPENAI_API_KEY=EMPTY
```

### Run the APP 
```
chainlit run app.py -w --port 8080 # -w flag is for restarting app after each change!
```