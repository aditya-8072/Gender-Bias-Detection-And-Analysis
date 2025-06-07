from flask import Flask, render_template, request, redirect, url_for, flash
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import threading
import webbrowser
#support vector machine(svm)
# Initialize Flask app
app = Flask(_name_)
app.config['UPLOAD_FOLDER'] = './uploads'
app.secret_key = 'your_secret_key'

# Track whether the browser has been ened
opened = False

# Function to open the browser only once
def open_browser():
    global opened
    if not opened:
        webbrowser.open("http://127.0.0.1:5000")
        opened = True

# Route to render the HTML page
@app.route('/')
def index():
    return render_template('index.html')

# Route to render description page
@app.route('/description')
def description():
    return render_template('description.html')

# Route to render hub page
@app.route('/hub')
def hub():
    return render_template('hub.html')

# Route to render the HTML page
@app.route('/scheme')
def scheme():
    return render_template('scheme.html')

# Route to render the HTML page
@app.route('/facts')
def facts():
    return render_template('facts.html')
                           


# Route to handle file uploads
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file:
        # Save the uploaded file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Analyze the uploaded file
        try:
            analysis_result = analyze_file(filepath)
            return analysis_result
        except Exception as e:
            return f"Error occurred: {e}"
def analyze_file(filepath):
    data = pd.read_csv(filepath)

    # Keywords for identifying relevant columns
    keywords = [
        'gender', 'male', 'female', 'country','region','ratio', 'equality', 'inequality', 'discrimination',
        'bias', 'diversity', 'inclusion', 'representation', 'pay', 'salary', 'wage',
        'participation', 'employment', 'occupation', 'stem', 'field', 'progress',
        'leadership', 'opportunity', 'education', 'advancement', 'representation', 'employment','science','technology','engineering','mathematics'
    ]

    # Detect columns containing keywords
    relevant_columns = [
        col for col in data.columns if any(keyword in col.lower() for keyword in keywords)
    ]

    if not relevant_columns:
        return "No relevant columns found in the dataset."

    # Create output directory
    output_dir = './static/output'
    os.makedirs(output_dir, exist_ok=True)

    # Store visualizations and descriptions
    visualizations = []
    descriptions = []

    for column in relevant_columns:
        print(f"Processing column: {column}")

        # For numeric columns
        if pd.api.types.is_numeric_dtype(data[column]):
            # Histogram
            plt.figure(figsize=(8, 4))
            sns.histplot(data[column], kde=False, color='red')
            plt.title(f'Histogram of {column}')
            plt.savefig(f'{output_dir}/{column}_histogram.png')
            visualizations.append(f'/static/output/{column}_histogram.png')
            descriptions.append(f"The histogram for '{column}' shows the distribution of numeric data.")
            plt.close()

            # Bar Graph
            plt.figure(figsize=(8, 4))
            data[column].value_counts().head(10).plot(kind='bar', color='green')
            plt.title(f'Bar Chart of {column}')
            plt.savefig(f'{output_dir}/{column}_barchart.png')
            visualizations.append(f'/static/output/{column}_barchart.png')
            descriptions.append(f"The bar chart for '{column}' summarizes the frequency of numeric values.")
            plt.close()

            # Pie Chart
            plt.figure(figsize=(8, 4))
            data[column].value_counts().head(5).plot(kind='pie', autopct='%1.1f%%', colors=['gold', 'skyblue', 'lightgreen'])
            plt.title(f'Pie Chart of {column}')
            plt.ylabel('')
            plt.savefig(f'{output_dir}/{column}_piechart.png')
            visualizations.append(f'/static/output/{column}_piechart.png')
            descriptions.append(f"The pie chart for '{column}' illustrates the percentage distribution of values.")
            plt.close()

        # For categorical columns
        #Random Forest
        elif pd.api.types.is_object_dtype(data[column]):
            # Bar Graph
            plt.figure(figsize=(8, 4))
            data[column].value_counts().head(10).plot(kind='bar', color='green')
            plt.title(f'Bar Chart of {column}')
            plt.savefig(f'{output_dir}/{column}_barchart.png')
            visualizations.append(f'/static/output/{column}_barchart.png')
            descriptions.append(f"The bar chart for '{column}' shows the frequency of each category.")
            plt.close()

            # Pie Chart
            plt.figure(figsize=(8, 4))
            data[column].value_counts().head(5).plot(kind='pie', autopct='%1.1f%%', colors=['gold', 'skyblue', 'lightgreen'])
            plt.title(f'Pie Chart of {column}')
            plt.ylabel('')
            plt.savefig(f'{output_dir}/{column}_piechart.png')
            visualizations.append(f'/static/output/{column}_piechart.png')
            descriptions.append(f"The pie chart for '{column}' shows the percentage distribution of categories.")
            plt.close()

    # Generate HTML with visualizations and descriptions
    results_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Analysis Results</title>
        <style>
            body {{
                background-image: url('/static/back.jpg');
                background-size: cover;
                background-position: center;
                font-family: Arial, sans-serif;
                color: white;
            }}
            h1 {{
                text-align: center;
                margin-top: 50px;
                color: black;
            }}
            h2 {{
                color: black;
                text-align:left;
                margin-left:10px;
            }}
             h3 {{
                color: black;
                text-align:center;
                
            }}
            p {{
                color: green;
                font-size: 20px;

            }}
            img {{
                display: block;
                margin: 20px auto;
                border: 2px solid black;
                width: 50%;
            }}
            ul{{
                color:blue;
                font-size:1.3em;
            }}
        </style>
    </head>
    <body>
        <h1>Analysis Results</h1>
        <h2>Relevant Columns Detected:</h2>
        <ul>
            {''.join([f'<li>{col}</li>' for col in relevant_columns])}
        </ul>
        <h3>Generated Graphs and Descriptions:</h3>
        {''.join([
            f"<div><img src='{vis}'><p>{desc}</p></div>" 
            for vis, desc in zip(visualizations, descriptions)
        ])}
    </body>
    </html>
    """
    return results_html

if _name_ == '_main_':
    # Run the Flask app in a separate thread
    threading.Thread(target=open_browser).start()
    app.run(debug=True)

def analyze_file(filepath):
    data = pd.read_csv(filepath)

    # Identify relevant columns based on keywords
    keywords = [
        'gender', 'male', 'female', 'ratio', 'equality', 'inequality', 'discrimination',
        'bias', 'diversity', 'inclusion', 'representation', 'pay', 'salary', 'wage',
        'participation', 'employment', 'occupation', 'stem', 'field', 'progress',
        'leadership', 'opportunity'
    ]

    relevant_columns = [
        col for col in data.columns if any(keyword in col.lower() for keyword in keywords)
    ]

    if not relevant_columns:
        return "No relevant columns found in the dataset."

    # Generate visualizations
    output_dir = './static/output'
    os.makedirs(output_dir, exist_ok=True)

    visualizations = []
    for column in relevant_columns:
        if pd.api.types.is_numeric_dtype(data[column]):
            # Histogram
            plt.figure(figsize=(8, 4))
            sns.histplot(data[column], kde=False, color='blue')
            plt.title(f'Histogram of {column}')
            plt.savefig(f'{output_dir}/{column}_histogram.png')
            visualizations.append(f'/static/output/{column}_histogram.png')
            plt.close()
        else:
            # Bar chart
            plt.figure(figsize=(8, 4))
            data[column].value_counts().plot(kind='bar', color='orange')
            plt.title(f'Bar Chart of {column}')
            plt.savefig(f'{output_dir}/{column}_barchart.png')
            visualizations.append(f'/static/output/{column}_barchart.png')
            plt.close()

    # Return results as an HTML page
    results_html = "<h1>Analysis Results</h1>"
    for vis in visualizations:
        results_html += f"<img src='{vis}' width='50%' style='margin: 20px;'>"
    return results_html

if __name__ == '__main__':
    # Run the Flask app in a separate thread
    threading.Thread(target=open_browser).start()
    app.run(debug=True)