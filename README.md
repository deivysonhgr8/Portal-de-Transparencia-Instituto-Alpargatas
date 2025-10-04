# Instituto Alpargatas Transparency Portal

This project describes the development of a **Transparency Portal** for the **Alpargatas Institute**, a non-profit organization focused on improving public education in partner municipalities.

The initiative was created to **democratize access to information** about the Institute’s social impact, following a survey that revealed **75% of a 155-person sample were unaware of the organization and its work**.

---

## ✨ Key Features

### 1. Educational Quality Index (IQE)

At the core of the project is the creation of a new multidimensional metric, the **IQE**.

* the IQE is calculated using a **weighted average** of five variables:

  * **Student performance (SAEB)**
  * **School flow (IDEB)**
  * **School infrastructure (School Census)**
  * **Socioeconomic level (INSE)**
  * **Teacher training (AFD)**

* The weights for each variable were **objectively defined using Factor Analysis**.

---

### 2. Predictive Investment Model

A **machine learning model**, trained on simulated data, was developed to **estimate the return on investment (ROI)** in terms of IQE improvement.

➡️ This tool enables the Institute to make strategic decisions by identifying municipalities with the **highest potential for educational improvement**.

---

### 3. Interactive Web Portal

The portal consolidates all this information into an **interactive web platform**, which includes:

* **Interactive map** displaying IQE scores
* **Detailed municipal analyses**
* **Chat interface** allowing natural language queries about the data

---

### 4. Innovative Communication Strategy

The project proposes a communication strategy using **QR Codes on Alpargatas products**, such as Havaianas sandals.

➡️ By scanning the code, consumers are directed to the portal, directly linking their purchase to the educational transformation it supports.

---

## 📦 Dependencies

The project requires the following dependencies:

* requests
* pandas
* numpy
* matplotlib
* seaborn
* urllib3
* plotly
* openpyxl
* xlrd
* scikit-learn
* factor_analyzer
* soundfile
* torch
* kokoro
* urllib3
* lightgbm

### Installation

To install all dependencies, run the following command:

```bash
pip install -r requirements.txt
```


## How To use the Script
- To run the results of the project, you can just open our website: 
https://portalalpargatas.netlify.app 
Or open the index.html file in the 'site' Folder.
- To see How we Create the IQE, you can run the python scripts named 'extract.py' followed by 'transform.py', and then 'iqe.py', and after 'load.py', all in the 'src' folder.
- To see how we create the predicting model, you can run the script 'generate_simulated_data.py' and then 'investment.py' in the 'src' folder
---

## 👨‍💻 Developers

This project was developed by:

* Deivyson Gomes
* Ítalo Oliveira
* Matheus Belchior

---

## 📌 Note

This project was designed to **strengthen transparency, innovation, and social impact** of the Alpargatas Institute, bringing society and education closer together through technology.
