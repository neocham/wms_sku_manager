# gui.py
import gradio as gr
import pandas as pd
from sku_mapper import SKUMapper

mapper = SKUMapper("data/mapping.csv")

def process_sales(file):
    if file is None:
        return pd.DataFrame(), pd.DataFrame(), None

    try:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file.name)
        elif file.name.endswith(".xlsx") or file.name.endswith(".xls"):
            df = pd.read_excel(file.name)
        else:
            return pd.DataFrame(), pd.DataFrame(), None  # Unsupported file

        mapped_df = mapper.map_skus(df)
        unmapped_df = mapper.get_unmapped(mapped_df)

        output_path = "mapped_output.csv"
        mapped_df.to_csv(output_path, index=False)

        return mapped_df, unmapped_df, output_path

    except Exception as e:
        print("Error in process_sales:", e)
        return pd.DataFrame(), pd.DataFrame(), None


with gr.Blocks() as demo:
    gr.Markdown("### 📦 SKU → MSKU Mapper Tool")

    file_input = gr.File(label="Upload Sales File (CSV or Excel)")
    mapped_output = gr.Dataframe(label="Mapped Sales Data")
    unmapped_output = gr.Dataframe(label="Unmapped SKUs")
    csv_output = gr.File(label="Download Mapped CSV", interactive=True)


    file_input.change(
    process_sales,
    inputs=file_input,
    outputs=[mapped_output, unmapped_output, csv_output]
)
    

demo.launch()
