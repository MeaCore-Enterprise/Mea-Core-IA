import logging
import signal
from contextlib import contextmanager
from pdfminer.high_level import extract_text

class TimeoutError(Exception):
    pass

@contextmanager
def timeout_handler(seconds):
    def timeout_signal(signum, frame):
        raise TimeoutError(f"PDF processing timed out after {seconds} seconds")
    
    # Set the signal handler and a timeout alarm
    old_handler = signal.signal(signal.SIGALRM, timeout_signal)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        # Reset the alarm and signal handler
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)

def pdf_to_text(path: str, timeout: int = 30) -> str:
    """Extract text from PDF with timeout protection"""
    try:
        # Disable verbose logging from pdfminer
        logging.getLogger('pdfminer').setLevel(logging.WARNING)
        
        with timeout_handler(timeout):
            text = extract_text(path, maxpages=50, page_numbers=None, password="", 
                              caching=True, check_extractable=False)
            return text or ""
            
    except TimeoutError as e:
        logging.warning(f"PDF processing timed out: {e}")
        return f"[PDF processing timed out - file may be too large or complex: {path}]"
    except Exception as e:
        logging.error(f"Error extracting text from PDF {path}: {e}")
        return f"[Error processing PDF: {str(e)}]"
