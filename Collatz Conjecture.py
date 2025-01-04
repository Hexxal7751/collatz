import tkinter as tk
from tkinter import filedialog, messagebox
import time
from decimal import Decimal
import sys
from tkinter.ttk import Progressbar
import threading
import os

sys.set_int_max_str_digits(2147483647) # Set the max integer digits to the maximum value of a 32-bit signed integer

# Generate a Collatz sequence for a positive integer 'n'.
def generate_sequence_with_check(n):
    if not (isinstance(n, int) and n > 0):
        raise ValueError("Input must be a positive integer")

    seq = []  # To store the sequence.
    visited = set()  # To track visited terms.

    while n != 1:
        if n in visited:
            return seq  # Return the sequence up to the point of repetition.
        visited.add(n)
        seq.append(n)

        # Generate the next term in the sequence.
        n = n // 2 if n % 2 == 0 else 3 * n + 1

    seq.append(1)  # Ensure the sequence ends in 1.
    return seq

# Save the sequence to file
def save_to_file(sequence, computation_time, root, entry, time_text):
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text Files", "*.txt")],
                                             title="Save Collatz Sequence")
    if file_path:
        # Flag to check if progress window is open
        progress_window_open = tk.BooleanVar(value=True)

        def file_write_task():
            try:
                chunk_size = 1000  # Number of terms to write at a time
                total_chunks = (len(sequence) + chunk_size - 1) // chunk_size

                # Start time for file writing
                start_time = time.time()

                with open(file_path, "w") as file:
                    # Write computation time first
                    file.write(f"Computation Time: {computation_time:.6f} seconds\n\n")
                    
                    # Write file write time placeholder (we'll update this later)
                    file.write("File Write Time: Calculating...\n\n")

                    # Write the number of terms placeholder
                    file.write(f"Total terms in the sequence: {len(sequence)}\n\n")

                    # Write the Collatz sequence in chunks
                    file.write("Collatz Sequence:\n\n")

                    for i in range(total_chunks):
                        if not progress_window_open.get():  # Stop updates if the window is closed
                            return

                        chunk = sequence[i * chunk_size:(i + 1) * chunk_size]
                        file.write(" -> ".join(map(str, chunk)) + "\n")

                        # Update progress bar and estimated time remaining
                        progress_bar["value"] = i + 1
                        elapsed_time = time.time() - start_time
                        avg_time_per_chunk = elapsed_time / (i + 1)
                        remaining_chunks = total_chunks - (i + 1)
                        estimated_remaining_time = remaining_chunks * avg_time_per_chunk

                        progress_window.after(0, lambda: remaining_time_label.config(
                            text=f"Time remaining: {estimated_remaining_time:.2f} seconds"
                        ))
                        progress_window.after(0, progress_bar.update)

                # Calculate time spent on file writing
                file_write_time = time.time() - start_time

                # Reopen the file to update the File Write Time
                with open(file_path, "r+") as file:
                    lines = file.readlines()
                    lines[1] = f"File Write Time: {file_write_time:.6f} seconds\n\n"  # Update file write time
                    file.seek(0)  # Go back to the beginning of the file
                    file.writelines(lines)  # Write back the updated content

                # Show the file write time in the progress window (excluding computation time)
                if progress_window_open.get():
                    progress_window.after(0, lambda: progress_label.config(
                        text=f"File written successfully in {file_write_time:.6f} seconds"
                    ))

                if progress_window_open.get():
                    progress_window.after(0, lambda: messagebox.showinfo("Success", f"The sequence has been written to '{file_path}'"))
                    progress_window.after(0, lambda: entry.delete(0, tk.END))
                    progress_window.after(0, lambda: time_text.set(''))
                    progress_window.after(0, progress_window.destroy)

            except Exception as e:
                if progress_window_open.get():
                    # Capture 'e' correctly using a default argument in the lambda
                    progress_window.after(0, lambda e=e: messagebox.showerror("Error", f"Error saving file: {e}"))
            finally:
                if progress_window_open.get():
                    progress_window_open.set(False)
                    root.after(0, lambda: root.attributes("-disabled", False))

        def on_progress_window_close():
            """Handle the progress window closure gracefully."""
            progress_window_open.set(False)  # Mark the window as closed
            progress_window.destroy()  # Destroy the progress window
            root.attributes("-disabled", False)  # Re-enable the main window

            # Notify the user if the file was not completely saved
            if os.path.exists(file_path):
                keep_file = messagebox.askyesno(
                    "Saving Stopped", 
                    f"The saving process was stopped midway. The output in the file may be partial. Do you want to keep the file at '{file_path}'?"
                )

                if not keep_file:
                    try:
                        os.remove(file_path)
                        messagebox.showinfo("File Deleted", f"The partial file at '{file_path}' has been deleted.")
                    except Exception as delete_error:
                        messagebox.showerror("Error", f"Error deleting file: {delete_error}")

        # Create a modal progress window
        progress_window = tk.Toplevel(root)
        progress_window.title("Saving Progress")
        progress_window.geometry("400x150")
        progress_window.config(bg="#f0f0f0")
        progress_window.transient(root)
        progress_window.grab_set()

        # Handle progress window closure
        progress_window.protocol("WM_DELETE_WINDOW", on_progress_window_close)

        # Disable the main window while saving
        root.attributes("-disabled", True)

        # Add progress UI elements
        progress_label = tk.Label(progress_window, text="Writing to file...", font=("Helvetica", 12), bg="#f0f0f0")
        progress_label.pack(pady=10)

        progress_bar = Progressbar(progress_window, orient="horizontal", length=300, mode="determinate")
        progress_bar.pack(pady=10)

        remaining_time_label = tk.Label(progress_window, text="Time remaining: Calculating...", font=("Helvetica", 12), bg="#f0f0f0")
        remaining_time_label.pack(pady=10)

        progress_bar["maximum"] = (len(sequence) + 999) // 1000

        # Start the file write operation in a separate thread
        threading.Thread(target=file_write_task, daemon=True).start()
    else:
        messagebox.showinfo("Canceled", "File saving canceled.")
        time_text.set('')



# Show credits
def show_credits():
    messagebox.showinfo("Credits", "Collatz Sequence Generator\n\nMathemaical Orgin: Lothar Collatz (1937)\n\nProject Prototype by: Vingardiumleviosa\nhttps://github.com/Vingardiumleviosa\n\nSuperCharged and Enhanced by: Hexxal7751\nhttps://github.com/Hexxal7751\n\nThank you for using the application!")

# GUI for the Collatz sequence generator
def create_ui():
    # Initialize the root window
    root = tk.Tk()
    root.title("Collatz Sequence Generator")
    root.geometry("400x200")
    root.resizable(False, False)
    root.config(bg="#f0f0f0")

    # Initialize time_text variable before passing it to other functions
    time_text = tk.StringVar()

    # Function to handle generation of the Collatz sequence, saving the file, and showing computation time
    def on_generate_and_save_click():
        try:
            input_value = entry.get()
            if not input_value.isdigit():
                raise ValueError("Input must be a positive integer.")
            
            n = int(input_value)  # Convert the validated input to an integer
            if n <= 0:
                raise ValueError("Please enter a positive integer.")


            # Check if the number exceeds the max allowed digits
            if len(str(n)) > sys.get_int_max_str_digits():
                raise ValueError("The number is too large to handle.\nThis program is limited to 2147483647 digits. (The maxiumum value of a 32-bit CPU.)")

            start_time = time.time()  # Start the timer
            sequence = generate_sequence_with_check(n)
            computation_time = time.time() - start_time  # Calculate computation time

            # Display computation time in the UI
            time_text.set(f"Computation Time: {computation_time:.6f} seconds")
            
            # Save the sequence to file (with computation time)
            save_to_file(sequence, computation_time, root, entry, time_text)
        
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            entry.delete(0, tk.END)
            time_text.set('')

    # Create input field for the number
    entry_label = tk.Label(root, text="Enter a positive integer:", font=("Helvetica", 12), bg="#f0f0f0")
    entry_label.pack(pady=10)
    
    entry = tk.Entry(root, font=("Helvetica", 12), width=40)
    entry.pack(pady=15)
    
    # Create a single button to generate the sequence and save it to a file
    generate_and_save_button = tk.Button(root, text="Generate and Save", font=("Helvetica", 12), bg="green", fg="white", command=on_generate_and_save_click)
    generate_and_save_button.pack(pady=20)

    # Create a label to display the computation time
    time_label = tk.Label(root, textvariable=time_text, font=("Helvetica", 12), bg="#f0f0f0")
    time_label.pack(pady=10)

    # Create the Credits button on the top left corner
    credits_button = tk.Button(root, text="Credits", font=("Helvetica", 10), bg="blue", fg="white", command=show_credits)
    credits_button.place(x=0, y=0)

    # Start the main GUI loop
    root.mainloop()


if __name__ == "__main__":
    create_ui()