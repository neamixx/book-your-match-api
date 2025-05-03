from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from ollama import AsyncClient
import subprocess
router = APIRouter(prefix="/ollama", tags=["ollama"])
'''
@router.get("/consulta")
async def consulta(query: str):
    try:
        # Usar la librería ollama para interactuar con el modelo `deepseek-r1`
        messages = [{'role': 'user','content': query}],
        client = AsyncClient()
        response = await client.chat('deepseek-r1', messages=messages)
        
        print(response['message']['content'])
        return {"consulta": query, "respuesta": response['message']['content']}
    
    except Exception as e:
        return {"error": str(e)}
 
'''
@router.get("/ask")
async def ask(query: str):
    try:
        client = AsyncClient()
        response = await client.generate(model='deepseek-r1', prompt=query)

        print(response['response'])

        return {"answer": response['response']}
    
    except Exception as e:
        return {"error": str(e)}
        