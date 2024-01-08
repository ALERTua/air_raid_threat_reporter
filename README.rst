Air Raid Threat Reporter
---------------------

Filters Telegram air raid threats channels by sending each message to Ollama AI for it to evaluate,
whether the message contains an actual threat to a city.
Redirects the filtered messages to a Telegram chat.


Preparation
^^^^^^^^

- Deploy https://hub.docker.com/r/ollama/ollama
- Optionally: Deploy https://github.com/ollama-webui/ollama-webui/pkgs/container/ollama-webui
- Read through `Modelfile` and use it to create a model via GUI or via CLI, or import it from Ollama Hub https://ollamahub.com/m/alert/ukraine-safety-assistant:latest
  (You can replace the city name and the base model, obviously.)
- Fill `.env` from `.env.example`


Deploy
^^^^^^
- Deploy Dockerfile (or image from `ghcr.io/alertua/air_raid_threat_reporter:latest`) with volume `/data`, put yout `.env` there. Alternatively, fill the Environment Variables.
- The first launch must be interactive (`-it`), to authenticate and create .session files in the volume folder.


Github
^^^^^^^^
https://github.com/ALERTua/threat_reporter
