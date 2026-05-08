# WasteWise Vision Pipeline

An AI-powered waste classification system that combines traditional Computer Vision (OpenCV-like) feature extraction with state-of-the-art LLM Vision models to classify and analyze waste materials for circular economy datasets.

## 🚀 Features

- **Multi-Modal Analysis**: Extracts 59 visual features (Color, Texture, Shape, Edges) using JavaScript pixel analysis.
- **AI Vision Integration**: Proxies requests through a Flask backend to Anthropic's Claude 3.5 Sonnet for precise item identification.
- **Premium UI**: Modern dark-mode interface with glassmorphism, micro-animations, and real-time canvas overlays.
- **Real-time Capture**: Supports both file uploads and live camera capture.
- **Dataset Export**: Export your analysis results directly to JSON or CSV formats.
- **Recycling Guide**: Provides context-aware disposal instructions for every detected item.

## 🛠️ Technology Stack

- **Frontend**: HTML5, Vanilla CSS, Vanilla JavaScript.
- **Backend**: Python, Flask, Flask-CORS.
- **API**: Anthropic Claude 3.5 Vision API.

## 📦 Installation & Setup

1. **Clone the repository**:
   ```bash
   # Navigate to your project folder
   cd Hackathon
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Environment Variable (Optional)**:
   You can set your Anthropic API key in the environment or enter it directly in the UI.
   ```bash
   # Windows (PowerShell)
   $env:ANTHROPIC_API_KEY="your_key_here"
   ```

4. **Run the Application**:
   ```bash
   python app.py
   ```

5. **Access the UI**:
   Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser.

## 📁 Project Structure

- `app.py`: Flask backend serving the API and static files.
- `index.html`: Main application entry point.
- `static/`:
  - `css/styles.css`: Premium design system.
  - `js/main.js`: Core vision pipeline logic.
- `requirements.txt`: Python package dependencies.
- `README.md`: Project documentation.

## 🛡️ License

MIT License - feel free to use for hackathons and educational purposes!
