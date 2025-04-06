# Changelog Transcript Search

Search all [Changelog](https://changelog.com/) transcripts at once.


### Dev

Install and start the [Typesense](https://typesense.org/) server:
```shell
> typesense-server --config=./typesense-server.ini
```

Import transcript data:
```shell
# clone the transcripts
> cd ..
> git clone https://github.com/thechangelog/transcripts.git
> cd ./changelog-transcript-search

# install dependencies
> python3 -m venv .venv
> source .venv/bin/activate
> pip install typesense

# import transcripts to typesense
> python import.py
```

Start the web UI:
```shell
> npm i
> npm run dev
```
