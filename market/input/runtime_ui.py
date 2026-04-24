import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from tkinter import ttk
import tkinter as tk
from typing import Optional

class InteractiveGraphDisplay:
    """Embed NetworkX graph in Tkinter with interactive node clicking"""
    
    def __init__(self, parent, graph: nx.DiGraph, pos: dict, node_data: dict = None):
        self.parent = parent
        self.graph = graph
        self.original_pos = pos
        self.node_data = node_data or {}
        
        # Track current selection
        self.selected_node = None
        self.node_collection = None  # Store reference to node collection for picking
        
        # Setup the figure
        self.fig = Figure(figsize=(10, 8), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.draw()
        
        # Add toolbar for pan/zoom
        self.toolbar = NavigationToolbar2Tk(self.canvas, parent, pack_toolbar=False)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Connect click event using pick_event
        self.cid = self.canvas.mpl_connect('pick_event', self.on_pick)
        
        # Create info frame with ttk
        self.info_frame = ttk.LabelFrame(parent, text="Node Information", padding=5)
        self.info_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        
        self.info_text = tk.Text(self.info_frame, width=30, height=20, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # ttk Scrollbar
        scrollbar = ttk.Scrollbar(self.info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.configure(yscrollcommand=scrollbar.set)
        
        # Button frame with ttk
        self.button_frame = ttk.Frame(parent)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        # Reset button (ttk)
        self.reset_button = ttk.Button(
            self.button_frame, 
            text="↺ Reset Selection", 
            command=self.reset_selection
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        # Export button
        self.export_button = ttk.Button(
            self.button_frame,
            text="📸 Export as PNG",
            command=self.export_graph
        )
        self.export_button.pack(side=tk.LEFT, padx=5)
        
        # Draw the initial graph
        self.draw_graph()
        
        # Pack canvas last
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    def draw_graph(self, highlight_node: Optional[str] = None):
        """Draw or redraw the graph with optional node highlighting"""
        self.ax.clear()
        
        # Draw nodes - capture the returned collection
        node_colors = 'lightblue' if not highlight_node else \
                       ['yellow' if node == highlight_node else 'lightblue' 
                        for node in self.graph.nodes()]
        
        node_sizes = 500 if not highlight_node else \
                      [800 if node == highlight_node else 500 
                       for node in self.graph.nodes()]
        
        # Draw nodes and store the collection
        self.node_collection = nx.draw_networkx_nodes(
            self.graph, self.original_pos,
            node_color=node_colors,
            node_size=node_sizes,
            ax=self.ax
        )
        
        # Enable picking on the node collection
        if self.node_collection is not None:
            self.node_collection.set_picker(True)
            self.node_collection.set_pickradius(5)
        
        # Draw edges with color coding based on selection
        if highlight_node and highlight_node in self.graph:
            incoming_edges = [(u, v) for u, v in self.graph.in_edges(highlight_node)]
            outgoing_edges = [(u, v) for u, v in self.graph.out_edges(highlight_node)]
            other_edges = [(u, v) for u, v in self.graph.edges() 
                          if u != highlight_node and v != highlight_node]
            
            if incoming_edges:
                nx.draw_networkx_edges(
                    self.graph, self.original_pos, 
                    edgelist=incoming_edges,
                    edge_color='blue', width=2.5, alpha=0.8,
                    arrows=True, arrowsize=20, ax=self.ax
                )
            
            if outgoing_edges:
                nx.draw_networkx_edges(
                    self.graph, self.original_pos,
                    edgelist=outgoing_edges,
                    edge_color='green', width=2.5, alpha=0.8,
                    arrows=True, arrowsize=20, ax=self.ax
                )
            
            if other_edges:
                nx.draw_networkx_edges(
                    self.graph, self.original_pos,
                    edgelist=other_edges,
                    edge_color='gray', width=1.0, alpha=0.5,
                    arrows=True, arrowsize=15, ax=self.ax
                )
        else:
            nx.draw_networkx_edges(
                self.graph, self.original_pos,
                edge_color='gray', width=1.5, alpha=0.7,
                arrows=True, arrowsize=15, ax=self.ax
            )
        
        # Draw labels
        nx.draw_networkx_labels(
            self.graph, self.original_pos,
            font_size=8, font_weight='bold', ax=self.ax
        )
        
        # Add title if node selected
        if highlight_node:
            self.ax.set_title(f"Graph - Selected: {highlight_node}", fontsize=14, fontweight='bold')
        else:
            self.ax.set_title("Product Layer Graph", fontsize=14)
        
        # Remove axes for cleaner look
        self.ax.set_axis_off()
        
        # Redraw canvas
        self.canvas.draw()
    
    def on_pick(self, event):
        """Handle node click events"""
        # Check if the picked artist is our node collection
        if event.artist == self.node_collection:
            # Get the indices of the picked nodes
            indices = event.ind
            if len(indices) > 0:
                # Get the node at that index
                nodes_list = list(self.graph.nodes())
                clicked_node = nodes_list[indices[0]]
                self.selected_node = clicked_node
                self.display_node_info(clicked_node)
                self.draw_graph(highlight_node=clicked_node)
    
    def display_node_info(self, node):
        """Display information about the clicked node"""
        self.info_text.delete(1.0, tk.END)
        
        # Basic node info
        info = f"=== {node} ===\n\n"
        
        # Add node attributes if available
        if node in self.graph.nodes:
            attrs = self.graph.nodes[node]
            if attrs:
                info += "Attributes:\n"
                for key, value in attrs.items():
                    info += f"  • {key}: {value}\n"
                info += "\n"
        
        # Add custom data from node_data dict
        if self.node_data and node in self.node_data:
            info += "Additional Info:\n"
            for key, value in self.node_data[node].items():
                info += f"  • {key}: {value}\n"
            info += "\n"
        
        # Connection information
        in_edges = list(self.graph.in_edges(node))
        out_edges = list(self.graph.out_edges(node))
        
        info += f"Connections:\n"
        info += f"  • Incoming: {len(in_edges)} edge(s)\n"
        if in_edges:
            info += f"    From: {', '.join([str(u) for u, v in in_edges])}\n"
        
        info += f"  • Outgoing: {len(out_edges)} edge(s)\n"
        if out_edges:
            info += f"    To: {', '.join([str(v) for u, v in out_edges])}\n"
        
        # Layer information (if available from position)
        if node in self.original_pos:
            y_pos = self.original_pos[node][1]
            info += f"\nLayer: {int(round(y_pos))}\n"
        
        self.info_text.insert(1.0, info)
    
    def reset_selection(self):
        """Reset to default view (no highlighted node)"""
        self.selected_node = None
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, "Click on any node to see its information here.")
        self.draw_graph(highlight_node=None)
    
    def export_graph(self):
        """Save current graph view as PNG"""
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filename:
            self.fig.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"Graph exported to {filename}")
    
    def cleanup(self):
        """Clean up matplotlib connections"""
        self.canvas.mpl_disconnect(self.cid)
        plt.close(self.fig)