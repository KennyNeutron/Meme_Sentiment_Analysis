
# Meme Sentiment Analysis

This project performs sentiment analysis on images using a combination of **EasyOCR**, **BLIP**, **VADER**, and **DeepAI**. The goal is to extract text from images (including memes), generate captions, analyze sentiments, and visualize the results. The project provides functionality to:
- Extract text from images.
- Translate extracted text to English (if necessary).
- Generate captions for images.
- Perform sentiment analysis on both the extracted text and image captions.
- Save results in an Excel file.
- Generate a sentiment distribution bar graph.

## Key Features:
- **Text Extraction**: Uses **EasyOCR** to extract text from images (supports multiple languages including Tagalog/Filipino).
- **Image Caption Generation**: Uses **BLIP** or **DeepAI API** to generate captions for images.
- **Sentiment Analysis**: Analyzes sentiment using **VADER Sentiment Analysis**.
- **Confidence Calculation**: Based on sentiment analysis scores, confidence levels are calculated and displayed.
- **Excel Output**: The results (image details, sentiment, confidence, etc.) are saved in an **Excel file**.
- **Graph Generation**: A **bar graph** showing sentiment distribution (positive, neutral, and negative) is generated and saved as an image.

## Installation

1. **Clone the repository**:
   ```
   git clone https://github.com/yourusername/meme-sentiment-analysis.git
   ```

2. **Navigate to the project directory**:
   ```
   cd meme-sentiment-analysis
   ```

3. **Set up the environment**:
   Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   ```

4. **Activate the virtual environment**:
   - For Windows:
     ```
     venv\Scriptsctivate
     ```
   - For macOS/Linux:
     ```
     source venv/bin/activate
     ```

5. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

   - The `requirements.txt` should include the following:
     ```
     easyocr
     googletrans==4.0.0-rc1
     requests
     pillow
     transformers
     torch
     vaderSentiment
     openpyxl
     matplotlib
     ```

## Usage

1. **Process a Folder of Images**:
   - You can process a folder of images to extract text, generate captions, and analyze sentiment.
   - Run the following command:
     ```
     python app.py
     ```
     - The program will prompt you to enter a **folder path** to process.
     - It will output results in an **Excel file** and generate a **bar graph** showing sentiment distribution.

2. **Process a Single Image**:
   - Alternatively, you can process a **single image**.
   - Run the following command:
     ```
     python app.py
     ```
     - Enter the **image file path** when prompted.
     - The result will be displayed in the terminal and saved in an **Excel file**.

3. **Folder Output**:
   - The processed images are categorized into two folders based on sentiment analysis:
     - **"with text"**: Images that contain valid, understandable text.
     - **"without text"**: Images with no text or non-understandable text.

4. **Excel Output**:
   - The results are saved in an **Excel file** that contains the following columns:
     - **File Name**: The name of the image file.
     - **Extracted Text**: Text extracted from the image.
     - **Translated Text**: Translated version of the extracted text (if applicable).
     - **Text Sentiment**: Sentiment of the extracted text (positive, neutral, or negative).
     - **Image Caption**: Caption generated for the image.
     - **Caption Sentiment**: Sentiment of the generated image caption.
     - **Overall Sentiment**: Overall sentiment based on the text and caption.
     - **Confidence**: Confidence level for the overall sentiment.

5. **Sentiment Distribution Graph**:
   - A **bar graph** is generated and saved, showing the distribution of **positive**, **neutral**, and **negative** sentiments based on the processed images.

## Example Output

1. **Excel File**:
   The Excel file contains columns like:
   | File Name      | Extracted Text  | Translated Text  | Text Sentiment | Image Caption  | Caption Sentiment | Overall Sentiment | Confidence |
   |----------------|-----------------|------------------|----------------|----------------|-------------------|-------------------|------------|
   | image1.jpg     | This is a meme   | This is a meme    | Positive       | A person laughing | Positive           | Positive           | 85.00%     |

2. **Graph**:
   - A **sentiment distribution bar graph** is generated and saved. This graph shows how many images are **positive**, **neutral**, or **negative** based on sentiment analysis.

## Troubleshooting

- **Error with DeepAI API**: Ensure you have a valid **API key** from DeepAI. Sign up for an account at [DeepAI](https://deepai.org/) to get your **API key** and replace `"your_deepai_api_key"` with your actual key.
- **File Access Issues**: If you encounter errors like **file access** issues during image processing, try running the script as **administrator** or **with elevated permissions**.
- **Performance Issues**: Running multiple image processing tasks (especially for large folders) might be resource-intensive. Consider running the script on a machine with better resources or optimizing the code for batch processing.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- **EasyOCR**: Open-source OCR tool used for extracting text from images.
- **VADER Sentiment Analysis**: Sentiment analysis tool used for analyzing extracted text and image captions.
- **BLIP**: Image captioning model used for generating captions for images.
- **DeepAI API**: Alternative image captioning API.

