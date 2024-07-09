import pandas as pd
import json
import re

# Function to clean the text
def clean_text(text):
    # Remove invalid characters
    return re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

# Function to generate the matrix
def generate_matrix(papers):
    data = []
    for paper in papers:
        if isinstance(paper, dict):
            criteria = paper.get('criteria', {})
            questions = paper.get('questions', {})
            if isinstance(criteria, dict) and isinstance(questions, dict):
                title = clean_text(paper.get('title', 'No Title'))
                row = [
                    title,
                    clean_text(criteria.get('Enfoque', '')),
                    clean_text(criteria.get('Datasets', '')),
                    clean_text(criteria.get('Descriptores', '')),
                    clean_text(criteria.get('Clasificadores', '')),
                    clean_text(criteria.get('Precisión', ''))
                ]
                for question in questions:
                    row.append(clean_text(questions[question]))
                data.append(row)

    # Column names
    columns = ['Title', 'Enfoque', 'Datasets', 'Descriptores', 'Clasificadores', 'Precisión'] + [f'Question {i+1}' for i in range(len(papers[0].get('questions', {})))]

    # Create the DataFrame and save it to an Excel file
    df = pd.DataFrame(data, columns=columns)
    df.to_excel(r'C:\Users\KIWIRAZER\Desktop\ieee_scraper\data\matrix_extraction.xlsx', index=False)

if __name__ == "__main__":
    # Load papers data from JSON file
    with open(r'C:\Users\KIWIRAZER\Desktop\ieee_scraper\data\papers_with_criteria_and_questions.json', 'r', encoding='utf-8') as f:
        papers = json.load(f)
    
    # Generate the matrix and save it
    generate_matrix(papers)
    print("Matriz de extracción guardada en 'C:\\Users\\KIWIRAZER\\Desktop\\ieee_scraper\\data\\matrix_extraction.xlsx'")
