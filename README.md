# Food_Nutrition_cmp

> **Searches up a specified food name to display a graph on its nutritional info.**

![License](https://img.shields.io/badge/license-MIT-green) ![Version](https://img.shields.io/badge/version-1.0.0-blue) ![Language](https://img.shields.io/badge/language-Python-yellow) ![Framework](https://img.shields.io/badge/framework-Streamlit-orange) ![GitHub](https://img.shields.io/badge/GitHub-Benoit--347%2FFood__Nutrition__cmp-black?logo=github) ![Build Status](https://img.shields.io/github/actions/workflow/status/Benoit-347/Food_Nutrition_cmp/ci.yml?branch=main)

## ℹ️ Project Information

- **👤 Author:** Benoit-347
- **📦 Version:** 1.0.0
- **📄 License:** MIT
- **📂 Repository:** [https://github.com/Benoit-347/Food_Nutrition_cmp/](https://github.com/Benoit-347/Food_Nutrition_cmp/)

---

## 📖 About The Project

**Food_Nutrition_cmp** is a Python-based tool designed to help users deeply understand and compare the nutritional content of common foods. Built with a focus on personal utility and ease of use, this application leverages the **Streamlit** framework to move beyond clunky terminal interfaces, offering a clean, interactive UI.

The application fetches data from the **USDA API** (a reputed food information source) to generate side-by-side comparisons of two different foods using dynamic **Matplotlib** bar graphs.

### ✨ Key Features

* **Dual Food Comparison:** Input two food names to fetch and compare their nutritional data instantly.
* **Customizable Data:** Users can select exactly which nutrients they want to see on the graph.
* **Categorized Visualization:**
    * Separate graphs for "Desired" nutrients.
    * Toggleable display for "Un-desired" nutrients.
* **Smart Caching System:** Automatically manages a local JSON file to store search results.
    * *Benefit:* Reduces search times from **~2s to ~0.2s**.
    * *Benefit:* Conserves API calls (staying well within the 1000 calls/hr free limit).
    * **Session Management:** Includes a manual **"Save"** button to store all session search results to the local json file. Which reduces frequent write when implementing caching system. (This is the very timplementation of the caching system; and is a Upgrade to the alternative of writing to file every time user runs the food search.)
* **Smart Search:** Users can filter foods by a minimum nutrient value. If no exact match is found, the program intelligently provides the closest match.

---

## ⚙️ Technical Architecture & Design Decisions

This project was built with specific design choices to optimize performance and user experience:

### 1. From Terminal to UI (Streamlit)
Initially, the project relied on terminal input. However, features like selecting specific nutrients from a list or visualizing data became complex to implement in a CLI environment.
* **Decision:** Switched to **Streamlit**. It handles the frontend heavy lifting, allowing for features like dropdowns and toggles without complex nested loops.

### 2. Data Visualization (Matplotlib)
Raw numbers are difficult to compare quickly.
* **Decision:** Integrated **Matplotlib** to render bar graphs.
* **Handling Missing Data:** Some API responses yield `None` types for specific nutrients. The system automatically sanitizes these to `0` (int) to ensure the graph plots successfully without crashing.

### 3. Optimization (Memoization & JSON)
One of the main challenges was the API Response Time caused by requests to the USDA API for each Food Search.
* **Decision:** Implemented **Memoization**. The program checks a local dictionary loaded from a JSON file before making an API call.
* **I/O Strategy:** To avoid the performance cost of writing to the disk after *every* single search, the app uses a **Batch Save** approach. New searches are held in memory during the session and only when the user clicks the **Save** button, the searches are written to the `json` file .

---

## 🚀 Getting Started

### Prerequisites

* Python 3.x
* A USDA API Key (Get one for free [here](https://fdc.nal.usda.gov/api-key-signup.html))

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Benoit-347/Food_Nutrition_cmp.git](https://github.com/Benoit-347/Food_Nutrition_cmp.git)
    cd Food_Nutrition_cmp
    ```

2.  **Install dependencies:**
    ```bash
    pip install streamlit matplotlib requests
    ```

3.  **Run the application:**
    ```bash
    streamlit run your_script_name.py
    ```
    *(Note: Replace `your_script_name.py` with the actual name of your python file)*

---

## 💡 Usage Guide

1.  **Enter API Key:** Ensure your USDA API key is configured (check code for input method or environment variable setup).
2.  **Input Foods:** Type the names of the two foods you wish to compare.
3.  **Select Nutrients:** Use the multi-select tool to choose which vitamins or macros to display.
4.  **Analyze:** View the generated bar graphs. Toggle the "Un-desired" graph if needed.
5.  **Save Progress:** Before closing, click the **Save** button to store your search results locally for faster access next time.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
