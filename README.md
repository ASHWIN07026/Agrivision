
# 🌱 AgriVision — AI-Based Precision Agriculture Platform

### 🌿 Crop Disease Detection | 🌾 Crop Yield Prediction | 📈 Market Intelligence

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/React-Vite-61DAFB?logo=react" alt="React"/>
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Machine%20Learning-AI-orange" alt="AI"/>
  <img src="https://img.shields.io/badge/Docker-Deployment-2496ED?logo=docker" alt="Docker"/>
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License"/>
</p>

<p align="center">
  <strong>An AI-powered agricultural decision-support platform integrating Computer Vision, Machine Learning, and Market Intelligence.</strong>
</p>

<p align="center">
  <a href="https://agrivision-6o2f.onrender.com">🌐 Live Demo</a> |
  <a href="https://github.com/ASHWIN07026/Agrivision">💻 GitHub Repository</a>
</p>

---

## 📖 1. Abstract

Agriculture faces several challenges, including crop diseases, unpredictable crop yields, changing weather conditions, and fluctuating market prices.

Traditional agricultural practices often rely on manual disease identification, historical experience, and limited market information. These challenges can result in delayed decisions, reduced crop productivity, and financial losses.

**AgriVision — AI-Based Precision Agriculture Platform** is designed to integrate three major agricultural decision-support capabilities into a unified web application:

1. Crop Disease Detection using Computer Vision and Deep Learning.
2. Crop Yield Estimation using Machine Learning.
3. Agricultural Market Intelligence for crop price analysis.

The platform aims to support farmers by providing accessible, data-driven agricultural information.

The current prototype implements leaf disease classification and historical crop-yield estimation. Live market data integration and additional advanced agricultural features are planned for future development.

---

## 🎯 2. Project Objectives

- Detect supported crop diseases from uploaded leaf images.
- Reduce delays in identifying potential plant diseases.
- Estimate crop yields using machine learning.
- Support agricultural planning through historical crop data.
- Provide a unified platform for disease detection, yield estimation, and market information.
- Improve the accessibility of AI-based agricultural decision-support tools.
- Explore integration with real-time agricultural information services.

---

## 🚀 3. Key Features

### 🌿 3.1 Crop Disease Detection

The Crop Disease Detection module uses computer vision and deep learning to identify supported diseases from plant leaf images.

**Features:**
- Leaf image upload.
- AI-based image classification.
- Identification of supported plant disease categories.
- Prediction results displayed in the dashboard.
- MobileNetV2-based disease classification.
- LiteRT inference in the deployed application.

**Current support:** 15 PlantVillage disease/healthy categories.

The model does not currently support every agricultural crop or disease.

### 🌾 3.2 Crop Yield Estimation

The Crop Yield Estimation module uses machine learning to estimate agricultural yield from historical records.

**Features:**
- Crop selection.
- Country or region selection.
- Historical year selection.
- Random Forest-based yield estimation.
- Yield results displayed in kg/ha.

**Current supported years:** 2012–2016.

The current implementation provides historical yield estimates rather than validated future-season forecasts.

### 📈 3.3 Market Intelligence

The Market Intelligence module is intended to help farmers understand agricultural commodity prices and market trends.

**Proposed features:**
- Crop-wise market prices.
- Market price comparison.
- Agricultural commodity trends.
- Government agricultural data integration.
- Price and demand analysis.
- Market decision support.

**Current status:** The market information interface is available, but live market API integration remains pending.

### 💡 3.4 Agricultural Recommendations

Future versions aim to provide additional guidance, including:

- Crop disease prevention.
- Natural disease management practices.
- Integrated pest management.
- Agricultural treatment recommendations.
- Crop management guidance.

These features require verified agricultural information and further implementation.

---

## 🏗️ 4. System Architecture

```text
                   +----------------------+
                   |    FARMER / USER     |
                   +----------+-----------+
                              |
                              v
                   +----------------------+
                   |   REACT + VITE UI    |
                   |  AGRIVISION DASHBOARD|
                   +----------+-----------+
                              |
                              v
                   +----------------------+
                   |    FASTAPI BACKEND   |
                   |     PYTHON REST API  |
                   +----------+-----------+
                              |
             +----------------+----------------+
             |                |                |
             v                v                v
    +----------------+ +----------------+ +----------------+
    | CROP DISEASE   | | CROP YIELD     | | MARKET         |
    | DETECTION      | | ESTIMATION     | | INTELLIGENCE   |
    +----------------+ +----------------+ +----------------+
             |                |                |
             v                v                v
    +----------------+ +----------------+ +----------------+
    | MobileNetV2    | | Random Forest  | | Market API     |
    | LiteRT         | | Regressor      | | Integration    |
    +----------------+ +----------------+ | (Planned)      |
             |                |           +----------------+
             v                v
    +----------------+ +----------------+
    | PlantVillage   | | FAOSTAT        |
    | Dataset        | | Dataset        |
    +----------------+ +----------------+
```

The project presentation also proposes PostgreSQL for storing user information, prediction history, and results. Database integration is not yet verified in the deployed prototype.

---

## 🛠️ 5. Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend | React.js, Vite |
| Backend | Python, FastAPI |
| Deep Learning | MobileNetV2 |
| Deployed AI Inference | LiteRT |
| Machine Learning | Random Forest Regressor |
| ML Libraries | TensorFlow/Keras, scikit-learn |
| Disease Dataset | PlantVillage |
| Yield Dataset | FAOSTAT |
| Database (Proposed) | PostgreSQL |
| Containerization | Docker |
| Deployment | Render |
| API Architecture | REST API |

---

## 📂 6. Repository Structure

```text
Agrivision/
│
├── AgriVision_Render_Free.zip
│   └── Application source code,
│       trained model files,
│       and supporting project files
│
├── Dockerfile
│   └── Docker build configuration
│
├── .gitignore
│
├── LICENSE
│
└── README.md
```

The application source code and supporting files are packaged inside `AgriVision_Render_Free.zip`.

---

## 📊 7. Dataset Details

### PlantVillage Dataset

The PlantVillage dataset contains images of healthy and diseased plant leaves.

It is used for training and evaluating crop disease classification models.

**Application:**
- Leaf image classification.
- Healthy and diseased plant identification.
- Computer vision model development.

The project presentation highlights tomato, potato, and pepper leaf disease identification.

### FAOSTAT Dataset

FAOSTAT provides historical agricultural production and yield information.

**Application:**
- Historical crop yield analysis.
- Crop and region-based yield estimation.
- Machine learning model training.

### Future Data Sources

Additional datasets and APIs may include:

- Soil characteristics.
- Rainfall records.
- Temperature data.
- Government agricultural statistics.
- AGMARKNET-type market information.
- Data.gov.in agricultural datasets.

These additional data sources are proposed integrations and are not all part of the current deployed workflow.

---

## 🤖 8. Machine Learning Models

### 8.1 Disease Detection — MobileNetV2

MobileNetV2 is a convolutional neural network architecture designed for efficient image classification.

**Workflow:**

```text
Leaf Image
    |
    v
Image Preprocessing
    |
    v
MobileNetV2 Model
    |
    v
Disease Classification
    |
    v
Prediction Result
```

### Disease Model Evaluation

| Evaluation Metric | Result |
|-------------------|--------|
| Test Accuracy | 83.45% |
| Macro F1 Score | 83.47% |
| Test Images | 731 |
| Supported Categories | 15 |

These results refer to the original MobileNetV2 model.

The converted LiteRT model has been checked using three sample images. Full test-set evaluation of the converted model remains pending.

### 8.2 Yield Estimation — Random Forest

The Random Forest Regressor is used to estimate historical agricultural crop yield.

**Workflow:**

```text
Country / Region
       +
      Crop
       +
      Year
       |
       v
Data Preprocessing
       |
       v
Random Forest Regressor
       |
       v
Estimated Crop Yield
       |
       v
Result in kg/ha
```

### Yield Model Evaluation

| Evaluation Metric | Result |
|-------------------|--------|
| R² Score | 0.657 |
| MAE | 7,202.85 kg/ha |
| RMSE | 13,220.11 kg/ha |

**Example Output:**

```text
Country: India
Crop: Maize (corn)
Year: 2016

Estimated Yield: 5,949.99 kg/ha
```

The result represents a historical estimate, not a guaranteed future harvest.

---

## ⚙️ 9. Working Methodology

### Step 1: User Input

The user interacts with the AgriVision dashboard.

The user can:
- Upload a crop leaf image.
- Select a crop.
- Choose a country or region.
- Enter a supported historical year.

### Step 2: Backend Processing

The React frontend communicates with the Python FastAPI backend.

The backend routes requests to the appropriate machine learning model.

### Step 3: AI Prediction

For disease detection:

```text
Leaf Image → MobileNetV2 → Disease Classification
```

For yield estimation:

```text
Historical Crop Data → Random Forest → Yield Estimate
```

### Step 4: Result Display

The dashboard presents the corresponding prediction to the user.

### Step 5: Future Expansion

Future development can connect additional modules for:

- Live market prices.
- Weather information.
- Soil analysis.
- Crop treatment recommendations.
- Farmer accounts.
- Prediction history.

---

## 💻 10. Installation and Setup

### Prerequisites

- Git
- Docker
- Internet connection

### Step 1: Clone the Repository

```bash
git clone https://github.com/ASHWIN07026/Agrivision.git
```

### Step 2: Open the Project

```bash
cd Agrivision
```

### Step 3: Build the Docker Image

```bash
docker build -t agrivision .
```

### Step 4: Run the Application

Check the `Dockerfile` for the configured application port and required environment variables.

Then run the Docker image using the corresponding port mapping.

For local frontend or backend development, extract `AgriVision_Render_Free.zip` and follow the configuration and dependency files included inside the archive.

Do not expose API keys, database credentials, or service-role secrets in source code.

---

## 🌐 11. Live Demo

The project is deployed on Render.

### 🔗 Website

https://agrivision-6o2f.onrender.com

### 🔗 GitHub Repository

https://github.com/ASHWIN07026/Agrivision

**Note:** The deployed application requires an internet connection.

---

## 📈 12. Results and Discussion

The prototype demonstrates the integration of computer vision and machine learning with a web-based agricultural dashboard.

### Demonstrated Results

- Leaf disease classification using a MobileNetV2-based model.
- Historical crop-yield estimation using Random Forest.
- React frontend connected to a FastAPI backend.
- Container-based deployment using Docker.
- Web application hosted on Render.

### Observations

The project demonstrates how AI models can be integrated into a common agricultural interface.

However, model evaluation results should not be interpreted as guaranteed accuracy for field conditions.

The system requires additional real-world validation before use as a dependable agricultural advisory tool.

---

## ⚠️ 13. Current Limitations

- Disease classification is limited to 15 supported categories.
- Performance on real-world field photographs remains unverified.
- Yield estimation currently supports historical years 2012–2016.
- The yield model is not validated for future-season forecasting.
- Live market data integration is pending.
- Database connectivity and persistent prediction history are unverified.
- Full LiteRT model evaluation remains pending.
- Offline AI inference is not currently supported by the deployed website.
- Agricultural recommendations require further verification.

---

## 🔮 14. Future Enhancements

### Advanced Disease Detection

- Expand supported crop species and disease categories.
- Improve performance using field-collected images.
- Add disease severity estimation.
- Explore explainable AI for leaf disease classification.

### Improved Yield Prediction

- Integrate rainfall data.
- Include soil properties.
- Use temperature and seasonal information.
- Develop and validate future-season yield forecasting.

### Market Intelligence

- Integrate agricultural commodity price APIs.
- Display verified mandi prices.
- Compare market prices across locations.
- Provide historical price trends.

### Smart Farmer Assistance

- Tamil, English, and Hindi language support.
- Voice-based agricultural assistance.
- Mobile camera-based disease detection.
- Natural and integrated crop management recommendations.
- Weather-aware agricultural suggestions.

### Platform Improvements

- Secure farmer authentication.
- PostgreSQL/Supabase database integration.
- Prediction history.
- Mobile-first interface.
- Optional offline model inference.
- Improved accessibility.

These are planned enhancements rather than completed features.

---

## 📚 15. Research and References

### Research Areas

The project is informed by research into:

1. Plant leaf disease classification using fine-tuned convolutional neural networks.
2. Crop yield prediction using machine learning techniques.
3. Computer vision applications in precision agriculture.
4. Agricultural market intelligence and decision-support systems.

### Dataset and Information Sources

**PlantVillage Dataset**

https://www.kaggle.com/datasets?search=plantvillage

**FAOSTAT**

https://www.fao.org/faostat/en/

**Open Government Data Platform India**

https://www.data.gov.in/

**IEEE Xplore Digital Library**

https://ieeexplore.ieee.org/

---

## 👨‍💻 16. Project Team

### Department of Artificial Intelligence and Data Science

| Name | Register Number | Role |
|------|-----------------|------|
| NITYASREE | 732523AD035 | Team Leader |
| JANANI S | 732523AD019 | Team Member |
| ASHWIN S | 732523AD002 | Team Member |

**Project Guide:** S. SABITHA, AP/AI&DS

**Project Type:** Mini Project

**Course Code:** 23ADL72

**Project Title:** AI-Based Precision Agriculture Platform

---

## 📄 17. License

This project is distributed under the license included in the repository.

See the [LICENSE](LICENSE) file for details.

---

## 🙏 18. Acknowledgements

We express our gratitude to our project guide, faculty members, and the Department of Artificial Intelligence and Data Science for their guidance and support.

We also acknowledge the developers and maintainers of the open-source frameworks, datasets, and tools used in this project.

---

## ⭐ Support the Project

If you find AgriVision useful, consider giving the repository a star.

**GitHub:** https://github.com/ASHWIN07026/Agrivision

---

<p align="center">
  <strong>🌱 AgriVision — Detect • Estimate • Decide</strong>
</p>

<p align="center">
  Developed as an academic AI-Based Precision Agriculture Mini Project.
</p>
