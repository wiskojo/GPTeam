# GPTeam
**GPTeam** is an experimental project that aims to coordinate multiple GPT agents asynchronously using subprocess and ZeroMQ. Drawing inspiration from recent works like Auto-GPT and babyagi, the goal of the project is to explore the possibilities of self-organizing and dynamically generated teams of GPT agents that collaborate together and with the user.

## Demo
https://twitter.com/wiskojo/status/1644535707279712257

## Features
- Asynchronous coordination of multiple GPT agents
- Dynamic generation of GPT agent teams

## Installation
To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt
```

## Usage
Start the main server:
```bash
python main.py
```

Monitor agent activity written to logs:
```bash
python watch_logs.py
```

## ❗Disclaimer
Please note that this project is still highly experimental and unfinished. It is important to exercise extreme caution if you want to run it. As task delegation is recursive, multiple agents may operate and use up token credits simultaneously which could end up being very expensive. Please do not run it if you don't know what you're doing. 
