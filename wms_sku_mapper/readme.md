
## 📦 Warehouse Management System (WMS)

A complete AI-assisted WMS MVP built with **Python**, **Gradio**, **Pandas**, and **Airtable**, enabling:

* 📥 Sales data preprocessing
* 🔗 SKU-to-MSKU mapping (with combo SKU support)
* 📊 Upload to Airtable with linked records
* 🧠 AI-powered analytics using PandasAI
* 📈 Chart generation from user queries
* 🌐 Web GUI deployable on Replit or locally

---

## 🚀 Features

| Module | Description                                                                |
| ------ | -------------------------------------------------------------------------- |
| Part 1 | GUI for SKU → MSKU mapping with support for Excel, combo SKUs, and logging |
| Part 2 | Relational DB & dashboard via Airtable (Sales ↔ Products ↔ Returns)        |
| Part 3 | Unified Gradio-based web interface with file drag-drop & Airtable sync     |
| Part 4 | AI (via PandasAI) for natural language queries, computed fields, charts    |

---

## 🔧 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/wms-ai.git
cd wms-ai
```

### 2. Install Requirements

```bash
pip install -r requirements.txt
```

### 3. Set Your Environment Variables

Create a `.env` file in the root directory with the following:

```ini
AIRTABLE_PAT=your_airtable_token
AIRTABLE_BASE_ID=your_base_id
AIRTABLE_TABLE_NAME=Sales
AIRTABLE_PRODUCT_TABLE_NAME=Products
OPENAI_API_KEY=your_openai_key
```

> 💡 You can also set these via Replit's Secrets tab if deploying there.

---

## ▶️ Running the App Locally

```bash
python gui.py
```

This will launch the Gradio app at `http://localhost:7860`.

---

## 🌐 Deploying on Replit

1. Create a new Replit with **Python**
2. Upload the code files
3. Add your secrets (e.g., `AIRTABLE_PAT`, `OPENAI_API_KEY`) via Secrets Manager
4. Run `gui.py`
5. You’ll get a public link like `https://wms-sku.replit.app`

---

## 🧠 AI Query Examples

You can ask the system:

* `"Show total sales by MSKU"`
* `"Plot a chart of top 5 selling products"`
* `"Add a column for revenue = price * quantity"`
* `"Show average sales per week"`

AI will process your CSV data using **PandasAI** and return results or graphs.

---

## 📁 Project Structure

```
wms-ai/
├── gui.py                 # Gradio UI + Upload to Airtable
├── sku_mapper.py         # SKU → MSKU mapping logic
├── requirements.txt       # Dependencies
├── .env                  # Your API keys (excluded from Git)
├── assets/               # Sample CSVs (optional)
└── README.md
```

---

## ✅ Dependencies

* `gradio`
* `pandas`
* `openai`
* `pandasai`
* `requests`
* `matplotlib` (optional for charts)

Install with:

```bash
pip install -r requirements.txt
```

---

## 🧪 Sample Data Files

Upload CSVs like:

* `Orders_*.csv`
* `Cste FK.csv` (Master MSKU file)
* `Returns_*.csv` (optional)

All files can be dropped into the GUI or read directly via `pandas`.

---

## 🤝 Contributing

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/awesome`)
3. Commit your changes
4. Push and open a PR

---

## 📬 Contact

Feel free to connect with me on [LinkedIn](https://www.linkedin.com/in/nitin-chamoli/) or email me at `nitin.chamoli99@gmail.com`.

---


