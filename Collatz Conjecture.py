import customtkinter as ctk
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import os
import webbrowser
from CTkMessagebox import CTkMessagebox
import networkx as nx
import threading
import time

class CollatzVisualizer:
    def __init__(self):
        self.setup_ui()
        self.current_theme = "dark"
        
    def setup_ui(self):
        # Configure appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Main window setup
        self.window = ctk.CTk()
        self.window.title("Collatz Conjecture Visualizer")
        self.window.geometry("1000x250")
        self.window.resizable(False, False)
        
        # Create main container
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            self.main_frame,
            text="Collatz Conjecture Visualizer",
            font=("Helvetica", 24, "bold")
        )
        title.pack(pady=20)
        
        # Input frame
        input_frame = ctk.CTkFrame(self.main_frame)
        input_frame.pack(fill="x", padx=20, pady=10)
        
        # Number input
        self.number_var = ctk.StringVar(value="")
        number_label = ctk.CTkLabel(
            input_frame,
            text="Enter a positive integer:",
            font=("Helvetica", 14)
        )
        number_label.pack(side="left", padx=10)
        
        self.number_entry = ctk.CTkEntry(
            input_frame,
            textvariable=self.number_var,
            width=700,
            font=("Helvetica", 14)
        )
        self.number_entry.pack(side="left", padx=10)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(self.main_frame)
        buttons_frame.pack(fill="x", padx=20, pady=10)
        
        # Generate buttons
        generate_btn = ctk.CTkButton(
            buttons_frame,
            text="Generate Sequence",
            command=self.generate_visualizations_starter,
            font=("Helvetica", 14)
        )
        generate_btn.pack(side="left", padx=10)
        
        generate_tree_btn = ctk.CTkButton(
            buttons_frame,
            text="Generate Tree",
            command=self.generate_tree_starter,
            font=("Helvetica", 14)
        )
        generate_tree_btn.pack(side="left", padx=10)
        
        generate_growth_btn = ctk.CTkButton(
            buttons_frame,
            text="Compare Growth Rates",
            command=self.compare_growth_rates_starter,
            font=("Helvetica", 14)
        )
        generate_growth_btn.pack(side="left", padx=10)
        
        # Theme toggle
        theme_btn = ctk.CTkButton(
            buttons_frame,
            text="Toggle Theme",
            command=self.toggle_theme,
            width=100,
            font=("Helvetica", 14)
        )
        theme_btn.pack(side="right", padx=10)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=("Helvetica", 12)
        )
        self.status_label.pack(pady=5)

    def start_threaded_task(self, task_function, title, *args):
        # Starts a task in a separate thread with a progress window.
        # Create the progress window
        progress_window, progress_bar, time_label = self.create_progress_window(title)

        def threaded_task():
            # Estimate task duration and start the progress bar update
            task_duration = 5  # Estimate task duration (adjust based on your needs)
            progress_thread = threading.Thread(target=self.update_progress, args=(progress_bar, time_label, task_duration))
            progress_thread.start()

            # Execute the main task
            task_function(*args)

            # Wait for the progress thread to complete
            progress_thread.join()

            # Close the progress window
            progress_window.destroy()

        # Start the task thread
        threading.Thread(target=threaded_task).start()

    def create_progress_window(self, title):
        # Creates a progress window for displaying task progress.
        progress_window = ctk.CTkToplevel(self.window)
        progress_window.title(title)
        progress_window.geometry("300x150")
        progress_window.resizable(False, False)

        # Ensure the progress window stays on top of the main window
        progress_window.lift()
        progress_window.attributes('-topmost', True)

        label = ctk.CTkLabel(progress_window, text="Processing...", font=("Helvetica", 14))
        label.pack(pady=10)

        progress_bar = ctk.CTkProgressBar(progress_window, orientation="horizontal", width=250)
        progress_bar.pack(pady=20)
        progress_bar.set(0)

        time_label = ctk.CTkLabel(progress_window, text="Estimated time: Calculating...", font=("Helvetica", 12))
        time_label.pack(pady=5)

        # Allow the main window to regain focus when the progress window is closed
        progress_window.protocol("WM_DELETE_WINDOW", lambda: None)

        return progress_window, progress_bar, time_label

    def update_progress(self, progress_bar, time_label, task_duration, interval=0.1):
        # Updates the progress bar based on task duration.
        start_time = time.time()
        while (elapsed := time.time() - start_time) < task_duration:
            progress = min(elapsed / task_duration, 1.0)
            progress_bar.set(progress)
            remaining = max(task_duration - elapsed, 0)
            time_label.configure(text=f"Estimated time: {remaining:.1f}s remaining")
            time.sleep(interval)

        # Set the progress bar to complete
        progress_bar.set(1.0)
        time_label.configure(text="Task completed!")
    
        
    def generate_sequence(self, n):
        try:
            n = int(n)
            if n <= 0:
                raise ValueError("Please enter a positive integer")
                
            sequence = [n]
            while n != 1:
                if n % 2 == 0:
                    n = n // 2
                else:
                    n = 3 * n + 1
                sequence.append(n)
            return sequence
        except ValueError as e:
            CTkMessagebox(title="Error", message=str(e), icon="warning")
            return None
            
    def calculate_even_odd_density(self, sequence):
        even_count = sum(1 for x in sequence if x % 2 == 0)
        odd_count = len(sequence) - even_count
        return even_count, odd_count

    def generate_visualizations_starter(self):
        self.start_threaded_task(self.generate_visualizations, "Generating Visualizations")
        
    def generate_visualizations(self):
        sequence = self.generate_sequence(self.number_var.get())
        if not sequence:
            return

        # Save sequence to a .txt file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        txt_filename = f"collatz_sequence_{timestamp}.txt"
        if not os.path.exists("visualizations"):
            os.makedirs("visualizations")
        txt_filepath = os.path.join("visualizations", txt_filename)

        try:
            with open(txt_filepath, "w") as f:
                f.write("Collatz Sequence\n")
                f.write(f"Start Number: {sequence[0]}\n")
                f.write(f"Steps: {len(sequence) - 1}\n")
                f.write("Sequence:\n")
                f.write(", ".join(map(str, sequence)))
            self.status_label.configure(
                text=f"Sequence saved as {txt_filename}",
                text_color="green"
            )
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Failed to save sequence: {str(e)}", icon="warning")
            return

        # Visualization generation continues as before...
        fig = make_subplots(
            rows=2, cols=2,
            specs=[
                [{"type": "xy"}, {"type": "domain"}],
                [{"type": "xy"}, {"type": "xy"}]
            ],
            subplot_titles=(
                'Sequence Progression',
                'Even/Odd Distribution',
                'Step Size Changes',
                'Value Distribution'
            )
        )

        # Sequence progression
        fig.add_trace(
            go.Scatter(
                x=list(range(len(sequence))),
                y=sequence,
                mode='lines+markers',
                name='Sequence',
                line=dict(color='#00bfff'),
                marker=dict(size=6)
            ),
            row=1, col=1
        )

        # Even/Odd density
        even_count, odd_count = self.calculate_even_odd_density(sequence)
        fig.add_trace(
            go.Pie(
                labels=['Even', 'Odd'],
                values=[even_count, odd_count],
                hole=.3,
                marker_colors=['#00bfff', '#ff69b4']
            ),
            row=1, col=2
        )

        # Step size changes
        step_sizes = [abs(sequence[i] - sequence[i-1]) for i in range(1, len(sequence))]
        fig.add_trace(
            go.Scatter(
                x=list(range(len(step_sizes))),
                y=step_sizes,
                mode='lines',
                name='Step Sizes',
                line=dict(color='#32cd32')
            ),
            row=2, col=1
        )

        # Value distribution
        fig.add_trace(
            go.Histogram(
                x=sequence,
                nbinsx=30,
                name='Value Distribution',
                marker_color='#ffa500'
            ),
            row=2, col=2
        )

        # Update layout
        fig.update_layout(
            height=800,
            showlegend=False,
            template='plotly_dark' if self.current_theme == "dark" else 'plotly_white',
            title_text=f"Collatz Sequence Analysis for {sequence[0]}",
            title_x=0.5
        )

        # Save and open in browser
        html_filename = f"collatz_visualization_{timestamp}.html"
        html_filepath = os.path.join("visualizations", html_filename)
        fig.write_html(html_filepath)
        webbrowser.open(f'file://{os.path.abspath(html_filepath)}')

        self.status_label.configure(
            text=f"Visualization saved as {html_filename}",
            text_color="green"
        )


    def generate_tree_starter(self):
        self.start_threaded_task(self.generate_tree, "Generating Tree Visualization")

    def generate_tree(self):
        try:
            center_num = int(self.number_var.get())
            if center_num <= 0:
                raise ValueError("Please enter a positive integer")
            
            # Create directed graph
            G = nx.DiGraph()
            
            # Generate tree for numbers up to the input number
            for n in range(1, center_num + 1):
                current = n
                while current != 1:
                    next_num = current // 2 if current % 2 == 0 else 3 * current + 1
                    G.add_edge(current, next_num)
                    current = next_num
            
            # Create the tree visualization using plotly
            pos = nx.spring_layout(G, k=1, iterations=50)
            
            # Create edges trace
            edge_x = []
            edge_y = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
            
            edges_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=0.5, color='#888'),
                hoverinfo='none',
                mode='lines'
            )
            
            # Create nodes trace
            node_x = []
            node_y = []
            node_text = []
            node_size = []
            node_color = []
            
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_text.append(str(node))
                # Highlight input number and special numbers
                if node == center_num:
                    node_size.append(20)
                    node_color.append('#ff0000')  # Red for input number
                elif node == 1:
                    node_size.append(15)
                    node_color.append('#00ff00')  # Green for terminal node (1)
                else:
                    node_size.append(10)
                    node_color.append('#1f77b4')  # Default blue
            
            nodes_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=node_text,
                textposition="top center",
                marker=dict(
                    showscale=False,
                    size=node_size,
                    color=node_color,
                    line_width=2
                )
            )
            
            # Create figure
            fig = go.Figure(
                data=[edges_trace, nodes_trace],
                layout=go.Layout(
                    title=f'Collatz Tree Visualization for n≤{center_num}',
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    annotations=[
                        dict(
                            text="Red: Input number<br>Green: Terminal node (1)<br>Blue: Other numbers",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0, y=-0.1
                        )
                    ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    template='plotly_dark' if self.current_theme == "dark" else 'plotly_white'
                )
            )
            
            # Save and open in browser
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"collatz_tree_{timestamp}.html"
            
            if not os.path.exists("visualizations"):
                os.makedirs("visualizations")
                
            filepath = os.path.join("visualizations", filename)
            fig.write_html(filepath)
            webbrowser.open(f'file://{os.path.abspath(filepath)}')
            
            self.status_label.configure(
                text=f"Tree visualization saved as {filename}",
                text_color="green"
            )
            
        except ValueError as e:
            CTkMessagebox(title="Error", message=str(e), icon="warning")

    def compare_growth_rates_starter(self):
        self.start_threaded_task(self.compare_growth_rates, "Comparing Growth Rates")

    def compare_growth_rates(self):
        try:
            center_num = int(self.number_var.get())
            if center_num <= 0:
                raise ValueError("Please enter a positive integer")
            
            # Generate sequences for numbers around the center number
            start_num = max(1, center_num - 5)
            end_num = center_num + 5
            sequences = {}
            
            for n in range(start_num, end_num + 1):
                sequences[n] = self.generate_sequence(n)
            
            # Create figure for growth rate comparison
            fig = go.Figure()
            
            # Add traces for each sequence
            for n, sequence in sequences.items():
                color = '#ff0000' if n == center_num else '#1f77b4'
                width = 3 if n == center_num else 1
                
                fig.add_trace(
                    go.Scatter(
                        y=sequence,
                        mode='lines',
                        name=f'n={n}',
                        line=dict(
                            color=color,
                            width=width
                        )
                    )
                )
            
            # Update layout
            fig.update_layout(
                title=f'Growth Rate Comparison (n±5 around {center_num})',
                xaxis_title='Steps',
                yaxis_title='Value',
                yaxis_type='log',  # Use log scale for better visualization
                showlegend=True,
                template='plotly_dark' if self.current_theme == "dark" else 'plotly_white',
                height=800
            )
            
            # Save and open in browser
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"collatz_growth_comparison_{timestamp}.html"
            
            if not os.path.exists("visualizations"):
                os.makedirs("visualizations")
                
            filepath = os.path.join("visualizations", filename)
            fig.write_html(filepath)
            webbrowser.open(f'file://{os.path.abspath(filepath)}')
            
            self.status_label.configure(
                text=f"Growth rate comparison saved as {filename}",
                text_color="green"
            )
            
        except ValueError as e:
            CTkMessagebox(title="Error", message=str(e), icon="warning")
        
    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        ctk.set_appearance_mode(self.current_theme)
        
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = CollatzVisualizer()
    app.run()
