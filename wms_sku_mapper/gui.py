# gui.py

import pandas as pd
import gradio as gr
import matplotlib.pyplot as plt
from airtable import Airtable
from sku_mapper import fuzzy_map_skus, load_file

# Airtable credentials (replace with your actual values)
AIRTABLE_BASE_ID = "your_base_id_here"
AIRTABLE_API_KEY = "your_airtable_api_key_here"
AIRTABLE_TABLE_NAME = "Sales"

airtable = Airtable(AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME, AIRTABLE_API_KEY)

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

def plot_top_mskus(df):
    top = df[df['MSKU'] != 'UNMAPPED']['MSKU'].value_counts().head(10)
    fig, ax = plt.subplots()
    top.plot(kind='bar', ax=ax, title='Top 10 MSKUs')
    ax.set_ylabel("Order Count")
    return fig

def plot_marketplace(df):
    if 'Marketplace' not in df.columns:
        return None
    counts = df['Marketplace'].value_counts()
    fig, ax = plt.subplots()
    counts.plot(kind='pie', ax=ax, autopct='%1.1f%%', title="Marketplace Share")
    return fig

def upload_to_airtable(mapped_df):
    uploaded = 0
    for _, row in mapped_df.iterrows():
        if row['MSKU'] == 'UNMAPPED':
            continue
        try:
            record = {
                "Order ID": str(row.get("Order ID", "")),
                "SKU": str(row.get("SKU", "")),
                "MSKU": str(row.get("MSKU", "")),
                "Quantity": int(row.get("Quantity", 0)),
                "Marketplace": row.get("Marketplace", ""),
                "Date": str(row.get("Date", ""))
            }
            airtable.insert(record)
            uploaded += 1
        except Exception as e:
            print("Error uploading row:", e)
    return f"✅ Uploaded {uploaded} records to Airtable."

# Gradio UI
with gr.Blocks() as app:
    gr.Markdown("## 📦 Warehouse Management System (WMS)\nUpload sales + MSKU master to begin")

    with gr.Row():
        msku_file = gr.File(label="📘 MSKU Master File (.csv)", file_types=[".csv"])
        sales_file = gr.File(label="🛒 Sales File (.csv or .xlsx)", file_types=[".csv", ".xlsx"])

    run_button = gr.Button("🔄 Clean & Map SKUs")
    output_status = gr.Textbox(label="Status Message")

    mapped_output = gr.Dataframe(label="✅ Mapped Sales Data")
    unmapped_output = gr.Dataframe(label="⚠️ Unmapped SKUs")

    with gr.Row():
        top_mskus_plot = gr.Plot(label="📊 Top Selling MSKUs")
        marketplace_plot = gr.Plot(label="🛍️ Marketplace Share")

    upload_btn = gr.Button("☁️ Upload to Airtable")

    def full_pipeline(msku_file, sales_file):
        mapped, unmapped, msg = process_files(msku_file, sales_file)
        return mapped, unmapped, msg, plot_top_mskus(mapped), plot_marketplace(mapped)

    run_button.click(fn=full_pipeline,
                     inputs=[msku_file, sales_file],
                     outputs=[mapped_output, unmapped_output, output_status, top_mskus_plot, marketplace_plot])

    upload_btn.click(fn=upload_to_airtable,
                     inputs=[mapped_output],
                     outputs=[output_status])

app.launch()
