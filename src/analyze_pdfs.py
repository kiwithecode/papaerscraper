import openai
import json
import os
from PyPDF2 import PdfReader
import time
import io

# Configura tu clave de API
openai.api_key = 'sk-proj-g0HTtGvSh1FIv0lRJcx6T3BlbkFJ8kMdjIRlxM6VxbA9dXu9'

# Lista de preguntas específicas
questions = [
    "¿Cuáles son las características soft-biométricas y de descripción visual general de una persona que utiliza este artículo?",
    "¿Cuáles son las características biométricas que utiliza este artículo?",
    "¿Qué técnicas de preprocesamiento de imágenes se utilizan para mejorar la calidad de la imagen y cuáles son estas técnicas?",
    "¿Qué técnicas de visión por computadora se utilizan para la extracción de características y cuáles son estas técnicas?",
    "¿Cuáles son los modelos y/o algoritmos de aprendizaje automático re-identifica a personas y cuáles son estos modelos y/o algoritmos?",
    "¿Cuáles son los modelos y/o algoritmos de aprendizaje profundo re-identifica a personas y cuáles son estos modelos y/o algoritmos?",
    "¿A cuál de estos enfoques se refiere el artículo, dígame el que mejor se ajuste: 'Búsqueda de personas desaparecidas o sospechosas, Seguimiento y recuento de personas, Notificación de movimientos inusuales o sospechosos, Integración con bases de datos externas, Elaboración de informes y análisis de patrones, Identificación y seguimiento de grupos de personas, Detección de cambios de aspecto, Seguimiento a gran escala, Identificación de múltiples personas, Mayor precisión en entornos abarrotados, Identificación de personas en movimiento, Detección de objetos abandonados, Detección de personas desaparecidas, Identificación de movimientos sospechosos o inusuales' o existen otros?",
    "¿A cuál de estos enfoques se alinea más este modelo?",
    "¿Cuál es el datasets utilizado en este paper?",
    "Dime cuál es el propósito de este paper científico.",
    "¿Este trabajo utiliza CPUs y/o GPUs?",
    "Dime cuáles son las métricas de evaluación aplicadas en este trabajo y cuáles son los valores de precisión alcanzados.",
    "Dime si se han realizado los experimentos en un circuito cerrado de cámaras y cuántas se utilizaron.",
    "Por favor, indícame la metodología aplicada en la re-identificación de personas utilizando técnicas de preprocesamiento, las técnicas de visión por computador y modelos y algoritmos de machine learning o deep learning."
]

def split_content(content, max_length=1500):
    paragraphs = content.split('\n')
    chunks = []
    chunk = ""

    for paragraph in paragraphs:
        if len(chunk) + len(paragraph) + 1 <= max_length:
            chunk += paragraph + "\n"
        else:
            chunks.append(chunk)
            chunk = paragraph + "\n"
    
    if chunk:
        chunks.append(chunk)
    
    return chunks

def extract_criteria(content):
    chunks = split_content(content)
    criteria = {
        "Enfoque": "",
        "Datasets": "",
        "Descriptores": "",
        "Clasificadores": "",
        "Precisión": ""
    }
    for chunk in chunks:
        prompt = f"Extrae los siguientes criterios del texto de manera directa y concisa:\nEnfoque, Datasets, Descriptores, Clasificadores, Precisión.\n\nTexto: {chunk}\n\nRespuesta:"
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            response_text = response['choices'][0]['message']['content'].strip()
            for line in response_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    if key in criteria and criteria[key] == "":
                        criteria[key] = value.strip()
        except Exception as e:
            print(f"Error al extraer criterios: {e}")
    return criteria

def extract_detailed_questions(content):
    chunks = split_content(content)
    responses = {question: "" for question in questions}
    for chunk in chunks:
        for question in questions:
            prompt = f"Responde de manera directa y concisa a la siguiente pregunta:\n{question}\n\nTexto: {chunk}\n\nRespuesta:"
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                response_text = response['choices'][0]['message']['content'].strip()
                if responses[question] == "":
                    responses[question] = response_text
            except Exception as e:
                print(f"Error al extraer la respuesta para la pregunta '{question}': {e}")
    return responses

def analyze_pdfs(directory):
    papers = []
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(directory, filename)
            try:
                with open(pdf_path, 'rb') as f:
                    reader = PdfReader(f)
                    content = ""
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            content += text
                
                criteria = extract_criteria(content)
                detailed_questions = extract_detailed_questions(content)
                papers.append({
                    "title": filename,
                    "criteria": criteria,
                    "questions": detailed_questions
                })
                time.sleep(10)  # Espera de 10 segundos antes de analizar el siguiente PDF
            except Exception as e:
                print(f"Error al analizar {filename}: {e}")
                papers.append({
                    "title": filename,
                    "criteria": {
                        "Enfoque": "",
                        "Datasets": "",
                        "Descriptores": "",
                        "Clasificadores": "",
                        "Precisión": ""
                    },
                    "questions": {question: "Error al extraer la respuesta." for question in questions}
                })
    return papers

if __name__ == "__main__":
    pdf_directory = r'C:\Users\KIWIRAZER\Desktop\ieee_scraper\data\pdfs'
    papers = analyze_pdfs(pdf_directory)
    with io.open(r'C:\Users\KIWIRAZER\Desktop\ieee_scraper\data\papers_with_criteria_and_questions.json', 'w', encoding='utf-8') as f:
        json.dump(papers, f, indent=4, ensure_ascii=False)
