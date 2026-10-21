# AGROVISION AI - Research Sources

## 1. Plant Disease Detection IEEE Paper (Referenced in PPT)
* **Title:** Plant Disease Identification Using Deep Learning
* **Source:** 2023 4th International Conference for Emerging Technology (INCET), IEEE Xplore
* **URL:** https://ieeexplore.ieee.org/document/10170463/
* **Problem Addressed:** Identifying crop leaf diseases automatically from images to reduce crop loss.
* **Dataset Used:** Typically PlantVillage or similar datasets optimized for neural networks via data augmentation.
* **Methodology:** The system involves a training phase (preprocessing, data cleaning, feature extraction with data augmentation) and a testing phase for prediction.
* **Algorithms/Models:** ResNet50, MobileNet, and Inception V3.
* **Limitations:** Often trained on lab-condition images which may not generalize well to field images.
* **Our Project Changes:** We will focus on extremely lightweight models (MobileNet) suitable for CPU inference, combining PlantVillage with field datasets (like PlantDoc), and adding a comprehensive dashboard.
* **Our Project Improves:** Real-world field accuracy estimation (via PlantDoc), offline PWA capabilities, and an integrated pipeline (disease + yield + market).

## 2. PlantVillage Dataset
* **Authors:** Sharada P. Mohanty, David P. Hughes, Marcel Salathé (2016)
* **Title:** Using Deep Learning for Image-Based Plant Disease Detection
* **Source:** Frontiers in Plant Science
* **Details:** 54,306 images of healthy and diseased leaves covering 14 crops and 26 diseases. Achieves up to 99.35% accuracy in lab conditions but drops significantly (~31%) on real-world images.
* **Relevance:** Provides the baseline dataset for our disease detection model.

## 3. PlantDoc Dataset
* **Authors:** Davinder Singh, et al. (2020)
* **Title:** PlantDoc: A Dataset for Visual Plant Disease Detection
* **Source:** 7th ACM IKDD CoDS and 25th COMAD
* **Details:** 2,569 images covering 13 plant species and 30 classes, captured in non-laboratory, real-field conditions.
* **Relevance:** Used to evaluate and improve our model's performance on real-world farmer photographs (domain gap reduction).

## 4. Government Open Agricultural Data
* **Source:** data.gov.in / AGMARKNET
* **Details:** Historical yield data and market prices for various commodities across Indian states and districts.
* **Relevance:** Baseline for yield prediction and market intelligence modules.
