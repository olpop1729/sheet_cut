# test_tkhtmlview.py
import tkinter as tk
from tkhtmlview import HTMLLabel

try:
    root = tk.Tk()
    root.title("tkhtmlview Test")
    root.geometry("400x300")

    html_content = "<h1>Hello World</h1><p>This should be <b>rendered</b> HTML.</p><p>If you see HTML tags like &lt;h1&gt;, then tkhtmlview is not rendering HTML correctly.</p>"
    
    html_label = HTMLLabel(root, html=html_content)
    html_label.pack(pady=10, padx=10, fill="both", expand=True)
    
    tk.Label(root, text="^^^ HTMLLabel above ^^^ | vvv Normal Label below vvv").pack(pady=5)
    
    normal_label = tk.Label(root, text=html_content) # Displaying same content in normal label for comparison
    normal_label.pack(pady=10, padx=10, fill="both", expand=True)

    root.mainloop()

except ImportError:
    print("tkhtmlview is not installed. Please install it using: pip install tkhtmlview")
except Exception as e:
    print(f"An error occurred: {e}")

