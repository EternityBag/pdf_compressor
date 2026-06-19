import streamlit as st
import fitz  # PyMuPDF
import io

# Set up the web page
st.set_page_config(page_title="PDF Compressor", page_icon="📄")
st.title("📄 Quick PDF Compressor")
st.write("Upload a heavy PDF to strip out unused data and compress its size.")

# Create a file uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Show the "Compress" button only after a file is uploaded
    if st.button("Compress PDF"):
        with st.spinner("Compressing..."):
            try:
                # Read the uploaded file into memory
                pdf_bytes = uploaded_file.read()
                original_size = len(pdf_bytes)
                
                # Open the PDF using PyMuPDF from the memory stream
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                
                # Create a new memory stream for the output
                out_stream = io.BytesIO()
                
                # Compress and save to the new stream
                doc.save(
                    out_stream,
                    garbage=4,          # Eliminate all unused objects
                    deflate=True,       # Compress uncompressed streams
                    clean=True          # Clean and sanitize content streams
                )
                doc.close()
                
                # Get the new size and calculate reduction
                compressed_bytes = out_stream.getvalue()
                new_size = len(compressed_bytes)
                reduction = (1 - (new_size / original_size)) * 100
                
                # Display results
                st.success("Compression successful!")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Original Size", f"{original_size / (1024*1024):.2f} MB")
                col2.metric("New Size", f"{new_size / (1024*1024):.2f} MB")
                col3.metric("Reduction", f"{reduction:.1f}%")
                
                # Provide the download button
                st.download_button(
                    label="⬇️ Download Compressed PDF",
                    data=compressed_bytes,
                    file_name=f"compressed_{uploaded_file.name}",
                    mime="application/pdf"
                )
                
            except Exception as e:
                st.error(f"An error occurred: {e}")