"""
File format converters for EPUB and PDF files.
Uses markitdown to convert various formats to markdown/text.
"""
import tempfile
import os
from typing import Optional
import streamlit as st

try:
    from markitdown import MarkItDown
    MARKITDOWN_AVAILABLE = True
except ImportError:
    MARKITDOWN_AVAILABLE = False


def convert_file_to_text(uploaded_file) -> Optional[str]:
    """
    Convert uploaded file (EPUB, PDF, etc.) to text using markitdown.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        str: Converted text content, or None if conversion fails
    """
    if not MARKITDOWN_AVAILABLE:
        st.error("❌ markitdown library is not installed. Please install it with: `pip install markitdown`")
        st.info("💡 After installation, restart the Streamlit app.")
        return None
    
    try:
        # Save uploaded file to temporary location
        file_ext = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            # Use markitdown to convert file
            md = MarkItDown()
            result = md.convert(tmp_path)
            
            # Extract text from result - markitdown returns different types
            text_content = None
            
            if isinstance(result, str):
                text_content = result
            elif hasattr(result, 'text_content'):
                text_content = result.text_content
            elif hasattr(result, 'text'):
                text_content = result.text
            elif hasattr(result, 'markdown'):
                text_content = result.markdown
            elif hasattr(result, 'content'):
                text_content = result.content
            
            if not text_content:
                st.error("Could not extract text from file. The file format might not be supported.")
                return None
            
            # Clean up any extra whitespace
            text_content = text_content.strip()
            
            if not text_content:
                st.warning("The converted file appears to be empty.")
                return None
                
            return text_content
                
        finally:
            # Clean up temporary file
            try:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            except Exception:
                pass
                
    except Exception as e:
        st.error(f"Error converting file: {str(e)}")
        # Note: st.debug doesn't exist in Streamlit, using error message instead
        return None


def is_supported_file_type(filename: str) -> bool:
    """
    Check if file type is supported for conversion.
    
    Args:
        filename: Name of the file
        
    Returns:
        bool: True if file type is supported
    """
    supported_extensions = ['.txt', '.md', '.epub', '.pdf', '.docx', '.doc']
    return any(filename.lower().endswith(ext) for ext in supported_extensions)


def get_file_type_description() -> str:
    """Get description of supported file types."""
    return "Supported formats: Text (.txt), Markdown (.md), EPUB (.epub), PDF (.pdf), Word (.docx, .doc)"

