# gui.py

import os
import pandas as pd
import gradio as gr
import matplotlib.pyplot as plt
import requests
from dotenv import load_dotenv
from sku_mapper import fuzzy_map_skus, load_file
import openai
import pandas as pd
import matplotlib.pyplot as plt
import io
import os

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


# Load Airtable credentials from .env

AIRTABLE_PAT = os.getenv("AIRTABLE_PAT")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME", "Sales")
AIRTABLE_PRODUCT_TABLE_NAME = "Products"    

def get_msku_record_id(msku_value):
    """Fetch the record ID from the Products table where MSKU == msku_value"""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_PRODUCT_TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_PAT}"
    }

    params = {
        "filterByFormula": f"MSKU='{msku_value}'",
        "maxRecords": 1
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            records = response.json().get("records", [])
            if records:
                return records[0]["id"]
        else:
            print(f"Lookup failed for MSKU '{msku_value}':", response.json())
    except Exception as e:
        print(f"Exception in get_msku_record_id for MSKU '{msku_value}':", e)

    return None

# -----------------------------
# Upload Mapped Rows to Airtable
# -----------------------------
def upload_to_airtable(mapped_df):
    if mapped_df.empty:
        return "⚠️ No data to upload. Please run mapping first."

    headers = {
        "Authorization": f"Bearer {AIRTABLE_PAT}",
        "Content-Type": "application/json"
    }

    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    uploaded = 0
    skipped = 0
    failed = 0

    for _, row in mapped_df.iterrows():
        msku = row.get("MSKU", "")
        if msku == "UNMAPPED" or not msku:
            skipped += 1
            continue

        msku_id = get_msku_record_id(msku)
        if not msku_id:
            print(f"⚠️ MSKU '{msku}' not found in product table. Skipping.")
            skipped += 1
            continue

        VALID_EVENT_TYPES = {
            "sale": "Sale",
            "return": "Return",
            "adjustment": "Adjustment",
            "other": "Other"
        }

        event_type_raw = str(row.get("Event Type", "")).strip().lower()
        event_type = VALID_EVENT_TYPES.get(event_type_raw)

        fields = {
            "Date": str(row.get("Date", "")),
            "Quantity": int(row.get("Quantity", 0)),
            "MSKU": [msku_id]
        }

        if event_type:
            fields["Event Type"] = event_type

        record = {"fields": fields}


        try:
            response = requests.post(url, json=record, headers=headers)
            if response.status_code in [200, 201]:
                uploaded += 1
            else:
                failed += 1
                print("❌ Upload error:", response.json())
        except Exception as e:
            failed += 1
            print("❌ Python exception during upload:", e)

    return f"✅ Uploaded: {uploaded}, ⚠️ Skipped (unmapped or missing MSKU): {skipped}, ❌ Failed: {failed}"



def execute_query_with_openai(prompt, df):
    system_msg = (
        "You are a data analyst. Convert user instructions into Python Pandas code to run on a DataFrame named df. "
        "Only output the code (no explanation). If the user asks for a chart, use matplotlib to show it. "
        "DO NOT define the dataframe — assume it's already loaded."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # fallback model
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )
        code = response.choices[0].message['content'].strip("`").replace("python", "")

        # Safe execution context
        local_env = {'df': df, 'pd': pd, 'plt': plt, 'io': io}
        exec(code, {}, local_env)

        if "plt" in code:
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            plt.clf()
            return gr.Image(value=buf, format="png"), None
        else:
            result = local_env.get('result', None)
            if result is not None:
                return None, str(result)
            return None, "✅ Code ran successfully but no result was returned."
    except Exception as e:
        return None, f"❌ Error: {str(e)}"



# -----------------------------
#  Process + Map SKUs
# -----------------------------
def process_files(msku_file, sales_file):
    try:
        msku_df = load_file(msku_file.name)
        sales_df = load_file(sales_file.name)

        if "SKU" not in sales_df.columns:
            return pd.DataFrame(), pd.DataFrame(), "⚠️ 'SKU' column missing in sales file."

        mapped_df = fuzzy_map_skus(sales_df.copy(), msku_df)
        unmapped_df = mapped_df[mapped_df['MSKU'] == 'UNMAPPED']
        return mapped_df, unmapped_df, "✅ Mapping complete!"
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame(), f"❌ Error: {str(e)}"

# -----------------------------
#  Plotting
# -----------------------------
def plot_top_mskus(df):
    if "MSKU" not in df.columns:
        return None
    
    filtered = df[df["MSKU"] != "UNMAPPED"]
    if filtered.empty:
        return None

    top = filtered["MSKU"].value_counts().head(10)
    if top.empty:
        return None

    fig, ax = plt.subplots()
    top.plot(kind="bar", ax=ax, title="Top 10 MSKUs")
    ax.set_ylabel("Order Count")
    return fig


def plot_marketplace(df):
    if "Marketplace" not in df.columns:
        return None
    
    counts = df["Marketplace"].dropna().value_counts()
    if counts.empty:
        return None

    fig, ax = plt.subplots()
    counts.plot(kind="pie", ax=ax, autopct="%1.1f%%", title="Marketplace Share")
    return fig


# -----------------------------
#  Gradio Interface
# -----------------------------
with gr.Blocks() as app:
    gr.Markdown("## 📦 Warehouse Management System (WMS)\nUpload sales + MSKU master to begin")

    with gr.Row():
        msku_file = gr.File(label="📘 MSKU Master File (.csv)", file_types=[".csv"])
        sales_file = gr.File(label="🛒 Sales File (.csv or .xlsx)", file_types=[".csv", ".xlsx"])

    run_button = gr.Button("🔄 Clean & Map SKUs")
    output_status = gr.Textbox(label="Status Message")

    mapped_output = gr.Dataframe(label="✅ Mapped Sales Data")
    unmapped_output = gr.Dataframe(label="⚠️ Unmapped SKUs")

    with gr.Tab("🔍 AI Insights"):
        query_input = gr.Textbox(label="Ask a question about the data")
        ask_btn = gr.Button("Ask AI")
        ai_plot_output = gr.Image()
        ai_text_output = gr.Textbox()

        ask_btn.click(fn=execute_query_with_openai,
                    inputs=[query_input, mapped_output],
                    outputs=[ai_plot_output, ai_text_output])



    with gr.Row():
        top_mskus_plot = gr.Plot(label="📊 Top Selling MSKUs")
        marketplace_plot = gr.Plot(label="🛍️ Marketplace Share")

    with gr.Row():
        upload_btn = gr.Button("☁️ Upload to Airtable")
        upload_status = gr.Textbox(label="Upload Status", interactive=False)

    upload_btn.click(fn=upload_to_airtable, inputs=[mapped_output], outputs=[upload_status])


    def full_pipeline(msku_file, sales_file):
        mapped, unmapped, msg = process_files(msku_file, sales_file)
        return mapped, unmapped, msg, plot_top_mskus(mapped), plot_marketplace(mapped)

    run_button.click(fn=full_pipeline,
                     inputs=[msku_file, sales_file],
                     outputs=[mapped_output, unmapped_output, output_status, top_mskus_plot, marketplace_plot])

    upload_btn.click(
        fn=upload_to_airtable,
        inputs=[mapped_output],
        outputs=[output_status]
)
    
    output_status = gr.Textbox(label="Status Message")


app.launch()
