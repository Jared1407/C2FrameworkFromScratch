import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import pprint
import json
import threading

class C2ClientGUI:
    """
    A tkinter GUI for the command-and-control client with a configurable server address.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("C2 Client")
        self.root.geometry("700x600") # Increased height for the new section

        # --- Main Frame ---
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Configuration Frame ---
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(config_frame, text="Server Address:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.server_addr_entry = ttk.Entry(config_frame, width=40)
        self.server_addr_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.server_addr_entry.insert(0, "http://127.0.0.1:5000") # Default value
        config_frame.grid_columnconfigure(1, weight=1) # Makes the entry widget expand

        # --- Control Frame (for buttons and inputs) ---
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.pack(fill=tk.X, pady=5)

        # --- GET Requests Frame ---
        get_frame = ttk.Frame(control_frame)
        get_frame.pack(fill=tk.X, pady=5)

        ttk.Button(get_frame, text="List Tasks", command=self.list_tasks).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(get_frame, text="List Results", command=self.list_results).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(get_frame, text="List History", command=self.list_history).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        # --- POST Request Frame (Add Task) ---
        post_frame = ttk.Frame(control_frame)
        post_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(post_frame, text="Task Type:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.task_type_entry = ttk.Entry(post_frame, width=30)
        self.task_type_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(post_frame, text="Options (key1=val1,key2=val2):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.options_entry = ttk.Entry(post_frame, width=30)
        self.options_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        post_frame.grid_columnconfigure(1, weight=1)

        self.add_task_button = ttk.Button(post_frame, text="Add Task", command=self.add_tasks)
        self.add_task_button.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

        # --- Output Frame ---
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True)

        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, height=15, width=80)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.configure(state='disabled')

    # --- Helper Functions (API Requests) ---
    def _get_server_addr(self):
        """Safely gets the server address from the entry widget."""
        addr = self.server_addr_entry.get().strip()
        if not addr:
            messagebox.showwarning("Configuration Error", "Server Address cannot be empty.")
            return None
        return addr

    def api_get_request(self, endpoint):
        """Performs a GET request using the address from the GUI."""
        server_addr = self._get_server_addr()
        if not server_addr: return # Stop if address is invalid
        response_raw = requests.get(server_addr + endpoint).text
        return json.loads(response_raw)

    def api_post_request(self, endpoint, payload):
        """Performs a POST request using the address from the GUI."""
        server_addr = self._get_server_addr()
        if not server_addr: return # Stop if address is invalid
        response_raw = requests.post(server_addr + endpoint, json=payload).text
        return json.loads(response_raw)
        
    def _execute_in_thread(self, target_func, *args):
        """Runs a function in a separate thread to keep the GUI responsive."""
        thread = threading.Thread(target=target_func, args=args)
        thread.daemon = True
        thread.start()

    # --- GUI Logic ---
    def _display_output(self, content, title=""):
        """Clears the output box and displays new formatted content."""
        if content is None: return # Don't display if the request was aborted
        self.output_text.configure(state='normal')
        self.output_text.delete('1.0', tk.END)
        header = f"--- {title} ---\n\n" if title else ""
        formatted_content = pprint.pformat(content, indent=4)
        self.output_text.insert(tk.END, header + formatted_content)
        self.output_text.configure(state='disabled')

    def _handle_request(self, api_call, title):
        """A generic handler for making API calls and displaying results or errors."""
        try:
            # The server address is retrieved inside the api_call function
            result = api_call()
            self.root.after(0, self._display_output, result, title)
        except requests.exceptions.ConnectionError:
            server_addr = self.server_addr_entry.get().strip()
            error_msg = f"Connection Error: Could not connect to {server_addr}.\n\nPlease check the address and ensure the server is running."
            self.root.after(0, messagebox.showerror, "Connection Error", error_msg)
        except Exception as e:
            error_msg = f"An unexpected error occurred:\n{str(e)}"
            self.root.after(0, messagebox.showerror, "Error", error_msg)

    def list_tasks(self):
        """Handles the 'List Tasks' button click."""
        self._execute_in_thread(self._handle_request, lambda: self.api_get_request("/tasks"), "Available Tasks")

    def list_results(self):
        """Handles the 'List Results' button click."""
        self._execute_in_thread(self._handle_request, lambda: self.api_get_request("/results"), "Implant Results")

    def list_history(self):
        """Handles the 'List History' button click."""
        self._execute_in_thread(self._handle_request, lambda: self.api_get_request("/history"), "Task History")

    def add_tasks(self):
        """Handles the 'Add Task' button click, parsing input and making a POST request."""
        task_type = self.task_type_entry.get().strip()
        
        if not task_type:
            messagebox.showwarning("Input Required", "Task Type cannot be empty.")
            return

        payload_dict = {"task_type": task_type}
        options_str = self.options_entry.get().strip()
        
        if options_str:
            try:
                task_options_pairs = options_str.split(",")
                for option in task_options_pairs:
                    if "=" not in option:
                        raise ValueError(f"Invalid option format: '{option}'. Expected 'key=value'.")
                    key, value = option.split("=", 1)
                    payload_dict[key.strip()] = value.strip()
            except Exception as e:
                messagebox.showerror("Invalid Options", f"Error parsing options: {e}")
                return

        request_payload = [payload_dict]
        
        self._execute_in_thread(
            self._handle_request, 
            lambda: self.api_post_request("/tasks", request_payload), 
            "Task Added"
        )

if __name__ == '__main__':
    root = tk.Tk()
    app = C2ClientGUI(root)
    root.mainloop()