# The Red Agent

## Authors

- [@Mathias](https://github.com/MathiasKrarup)
- [@Andreas](https://github.com/AndreasBerthelsen)
- [@Jens](https://github.com/JensIssa)


## Introduction
The Red Agent helps users analyze the stock market with real-time data and expert insights. It uses large language models (LLMs), a vector database, and the Financial Modeling Prep (FMP) API to deliver quick and accurate market analysis.

Features

- Real-Time Data: Fetches live stock prices and market trends using the FMP API.

- Retrieval-Augmented Generation (RAG): Combines LLM capabilities with a vector database containing financial trading knowledge for more accurate, context-aware responses.

- Multi-Agent System: Automates tasks through coordinated agents powered by AutoGen.

- User-Friendly UI: Interactive interface built with the Panel Framework.
### Prerequisites
The Prerequisites assume you have [Docker](https://www.docker.com/) running

#### We recommend to first create a virtual enviroment, where the Python version have to be between Python 10 - Python 11.

To be able to run the application, first install Ollama from the [Ollama website](https://ollama.com/).

Then create a .env file with the following properties:
```
MODEL="THE MODEL YOU WANT FROM OLLAMA"
API_TYPE="ollama"
CLIENT_HOST="http://localhost:11434/"
API_FINANCIAL_KEY="GET THE FMP API KEY FROM https://site.financialmodelingprep.com/"
```

### Depedencies
- qdrant_client
- ollama
- logging
- pdfplumber
- llama_index
- pathlib
- requests
- llama_index
- llama_index.vector_stores.qdrant
- autogen
- fix-busted-json
- asyncio
- panel

### How to run the application

Navigate to root folder, then run the following:
```
pip install requirements.txt -r
```
Then navigate to the src folder, and then TheRedAgent folder

If you want to utilize the vector database, you have to create the vector for the data:
To create embeddings of our data:
```
python vectorstore.py
```
When that is done, one is able to run the UI with the agents running with the following command:
```
panel serve redagent.py
```

# Showcase of the application

## Can you get the top stock gainers:

![image](https://github.com/user-attachments/assets/7293fbd6-3cc7-4773-a33c-dc4fc8d2e232)

![image](https://github.com/user-attachments/assets/f8be9adc-3f89-4f30-820c-9b3af1924f37)

![image](https://github.com/user-attachments/assets/a73c64ed-cd4d-4cba-9e2f-1e85005ff8c9)

![image](https://github.com/user-attachments/assets/a4847097-6cd5-43eb-81c6-2eec7cf15b9e)

![image](https://github.com/user-attachments/assets/b330ad24-a5c7-45d4-a2d9-7e134a5135d1)

## Can you provide me with the top 5 losing stocks in the market today, along with any relevant insigts on why they might be underperforming

![image](https://github.com/user-attachments/assets/6f69e8dc-c6da-44a5-9bf1-66976bbc1470)

![image](https://github.com/user-attachments/assets/aeabaa6a-5571-407b-bf86-a41e2fdf631c)

![image](https://github.com/user-attachments/assets/9d274cc4-cd19-4253-8ee4-5ebfd9804490)

## Can you provide top stock gainers, along with relevant advice

![image](https://github.com/user-attachments/assets/46efa462-9d1d-4c70-b8ad-23d31babbb57)

![image](https://github.com/user-attachments/assets/991d9ff3-966b-4499-aaea-ea14c863f1ae)

![image](https://github.com/user-attachments/assets/c3ce1685-964a-42a2-92a9-bf96e36dd9a2)

![image](https://github.com/user-attachments/assets/99bc3590-b042-4bfe-bf36-c62dbd6d5531)

![image](https://github.com/user-attachments/assets/f69e7659-693a-45e9-906a-8cbcc8571b03)

![image](https://github.com/user-attachments/assets/96abf98a-c271-4f3f-a04a-7fa5199e5747)

