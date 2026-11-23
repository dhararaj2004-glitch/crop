# Multi-Plant Disease Detection & Severity Grader

One lightweight MobileNetV2 model trained on **many crops and many diseases** (whatever
Kaggle datasets you attach), an **Unknown / not-a-leaf** class so it can refuse images it
doesn't understand, and an OpenCV **severity grader** - all in a Streamlit app that runs on CPU.

```
crop-disease-detector/
├── app.py                       # Streamlit app
├── run_windows.bat / run_mac_linux.sh  # one-click setup + run
├── check_setup.py               # verifies Python, packages and model files
├── requirements.txt
├── make_sample_images.py        # fake leaves to test the severity grader
├── model/                       # <- put leaf_model.keras + class_names.json here
├── notebooks/kaggle_train.ipynb # trains on ALL attached datasets (no download to your PC)
├── utils/                       # preprocess, severity grader, model loader
└── tests/                       # severity + knowledge-base tests

Knowledge base: utils/knowledge.py (edit it to add diseases). Contacts/maps: utils/help_finder.py.
```

## Features

- **Diagnosis** with ranked possible diseases, probability chart, low-confidence and "not a leaf" handling
- **Severity grading** (OpenCV): % affected leaf area, grade and leaf-health score with an overlay
- **How to deal with it**: severity-aware action plan plus field practices, organic options, chemical options
  (with a safety note) and prevention for ~30 diseases/pests, with general fallbacks for others
- **Who to contact / nearest help**: pick your state and district; the app lists the Kisan Call Centre
  (1800-180-1551), KVK (Krishi Vigyan Kendra) portal and apps, agriculture office and university, and builds
  Google Maps search links for the nearest ones (other countries get generic extension-service links)
- **Disease library** you can browse without scanning (works even before the model is trained)
- **Printable report** (HTML -> Print -> Save as PDF) and **scan history** with CSV export

## Quick start (VS Code)

1. Unzip, then **File -> Open Folder** in VS Code.
2. Train the model once on Kaggle (Step 1 below) and put `leaf_model.keras` + `class_names.json` in `model/`.
3. Open the terminal and run **`run_windows.bat`** (Mac/Linux: `bash run_mac_linux.sh`).
   It creates the virtual environment, installs everything, checks your setup and starts the app.
   (VS Code shortcut: Terminal -> Run Task -> "Run Streamlit app".)

## Step 1 - Train on Kaggle (one time)

1. kaggle.com -> **Create -> New Notebook** -> **File -> Import Notebook** -> upload `notebooks/kaggle_train.ipynb`.
2. **Add Input** and attach several plant-disease datasets. Search for:
   `PlantVillage`, `New Plant Diseases Dataset`, `PlantDoc`, `rice leaf diseases`,
   `cassava leaf disease`, `wheat disease`, `apple / grape / cotton / sugarcane / maize leaf disease`.
   More datasets = more plants and diseases covered.
3. Settings: **Accelerator = GPU**, **Internet = On**.
4. **Run All.** The notebook finds every class folder in every dataset, merges classes with the
   same name, drops tiny classes, caps images per class, and trains. Edit the CONFIG cell to change
   `CROPS` (None = all), `MAX_PER_CLASS`, epochs.
5. From the **Output** tab download `leaf_model.keras` and `class_names.json`; put them in `model/`.

Tip: if the run is too slow, lower `MAX_PER_CLASS` (e.g. 600) or `EPOCHS_*`.

## Step 2 - Run locally in VS Code

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows   (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```

Python 3.10 - 3.12. App opens at http://localhost:8501. Without model files the app still runs
and the severity grader works. `python make_sample_images.py` creates test leaves.
Tests: `pip install pytest && pytest`.

## What "all plants" really means

The model can only recognise the plants and diseases present in the datasets you trained on
(shown in the app sidebar under "Supported"). Anything else is either flagged as **Unknown** or
shown with a low-confidence warning. Adjust the confidence slider in the sidebar.

## Limitations (state these in your report)

- Most public datasets are lab-style (plain background); field photos score lower.
- Different datasets use different labelling, so some classes may be weaker - check the
  "Weakest classes" printout in the notebook.
- Severity is a colour heuristic (HSV thresholds), not a learned model.
- Covers leaf diseases only, not pests or nutrient deficiencies. Not a replacement for expert diagnosis.

## Results (fill in after training)

| Metric | Value |
|---|---|
| Plants / conditions covered | _ / _ |
| Validation accuracy | _ |
| Model size (.keras / .tflite) | _ MB / _ MB |
