import streamlit as st
import tempfile
import subprocess
import os

st.set_page_config(page_title="Deep PDF Compressor", page_icon="🗜️")
st.title("🗜️ Deep PDF Compressor")
st.write("This tool uses Ghostscript to downsample images and deeply compress your PDF.")

# Compression level selector
compression_level = st.radio(
    "Select Compression Level:",
    options=["Standard (/ebook - 150 DPI)", "Maximum (/screen - 72 DPI)"],
    index=0,
    help="Standard is best for reading. Maximum is best for strict file size limits (like email attachments), but images will lose quality."
)

uploaded_file = st.file_uploader("Choose a heavy PDF file", type="pdf")

if uploaded_file is not None:
    if st.button("Compress PDF"):
        with st.spinner("Deeply compressing... this might take a few seconds."):
            try:
                original_size = uploaded_file.size
                
                # Determine Ghostscript setting based on user choice
                pdf_settings = "/ebook" if "Standard" in compression_level else "/screen"

                # 1. Create secure temporary files
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_in:
                    temp_in.write(uploaded_file.read())
                    temp_in_path = temp_in.name

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_out:
                    temp_out_path = temp_out.name

                # 2. Build and run the Ghostscript command
                gs_command = [
                    "gs", 
                    "-sDEVICE=pdfwrite", 
                    "-dCompatibilityLevel=1.4",
                    f"-dPDFSETTINGS={pdf_settings}",
                    "-dNOPAUSE", 
                    "-dQUIET", 
                    "-dBATCH",
                    f"-sOutputFile={temp_out_path}", 
                    temp_in_path
                ]
                
                # Execute the command
                subprocess.run(gs_command, check=True)

                # 3. Read the compressed file back into memory
                with open(temp_out_path, "rb") as f:
                    compressed_bytes = f.read()
                    
                new_size = len(compressed_bytes)
                reduction = (1 - (new_size / original_size)) * 100

                # 4. Clean up (Delete the temp files from the server)
                os.remove(temp_in_path)
                os.remove(temp_out_path)

                # Display Results
                st.success("Compression successful!")
                col1, col2, col3 = st.columns(3)
                col1.metric("Original Size", f"{original_size / (1024*1024):.2f} MB")
                col2.metric("New Size", f"{new_size / (1024*1024):.2f} MB")
                col3.metric("Reduction", f"{reduction:.1f}%")
                
                st.download_button(
                    label="⬇️ Download Compressed PDF",
                    data=compressed_bytes,
                    file_name=f"compressed_{uploaded_file.name}",
                    mime="application/pdf"
                )
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
