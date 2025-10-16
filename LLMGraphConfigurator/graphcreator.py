import pygame
import sys
import json
from collections import defaultdict
import os
import random  # Added for random color generation
import tkinter as tk
from tkinter import filedialog

# Initialize pygame
pygame.init()

# Constants - WHITE AND DARK BLUE THEME
WIDTH, HEIGHT = 1000, 700
TOOLBAR_HEIGHT = 60
NODE_WIDTH, NODE_HEIGHT = 120, 80
CONNECTOR_RADIUS = 8
BG_COLOR = (255, 255, 255)  # White background
TOOLBAR_COLOR = (240, 240, 245)  # Light gray toolbar
NODE_COLOR = (30, 60, 120)  # Dark blue
NODE_SELECTED_COLOR = (50, 100, 180)  # Lighter blue for selection
CONNECTOR_COLORS = ((70, 130, 180), (0, 191, 255))  # SteelBlue and DeepSkyBlue
CONNECTOR_HOVER_COLOR = (180, 220, 255)  # Light blue for hover
BUTTON_COLORS = [
    (50, 180, 100),  # MediumSeaGreen - retrieval
    (70, 130, 180),  # SteelBlue - input
    (220, 180, 60),  # GoldenRod - query
    (220, 100, 100),  # IndianRed - output
    (180, 100, 220),  # MediumOrchid - condition
    (100, 180, 180)  # Teal - memory (new color)
]
BUTTON_TYPES = ["input", "retrieval", "query", "output", "memory", "condition"]
TEXT_COLOR = (20, 20, 30)  # Almost black for text
LINE_COLOR = (30, 100, 200)  # Blue for connections - This will be replaced with random colors
CONFIG_WINDOW_COLOR = (245, 245, 250)  # Very light gray
CONFIG_WINDOW_BORDER = (180, 180, 200)  # Light gray border
TEXT_INPUT_BG = (255, 255, 255)  # White
TEXT_INPUT_BORDER = (100, 130, 180)  # Blue border
DROP_ZONE_COLOR = (220, 230, 240)  # Very light blue
DROP_ZONE_HOVER = (200, 220, 240)  # Slightly darker blue
SCROLLBAR_COLOR = (180, 200, 220)  # Light blue for scrollbar
SCROLLBAR_HOVER = (150, 180, 210)  # Slightly darker for hover

# Configuration field descriptions
CONFIG_FIELDS = {
    "retrieval": ["Retrieval Document"],
    "query": ["Behaviour"],
    "condition": ["Trigger"],
    "memory": ["Registry Name"]
    # Add more node types as needed
}

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LLMTSup Configurator")
font = pygame.font.SysFont(None, 24)
title_font = pygame.font.SysFont(None, 32)
text_font = pygame.font.SysFont(None, 22)


def point_to_segment_distance(p1, p2, p):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p
    px = x2 - x1
    py = y2 - y1
    if px == 0 and py == 0:
        return ((x3 - x1)**2 + (y3 - y1)**2)**0.5
    u = ((x3 - x1) * px + (y3 - y1) * py) / (px**2 + py**2)
    if u > 1:
        u = 1
    elif u < 0:
        u = 0
    x = x1 + u * px
    y = y1 + u * py
    dx = x - x3
    dy = y - y3
    return (dx**2 + dy**2)**0.5


class Node:
    def __init__(self, node_id, node_type, x, y):
        self.id = node_id
        self.type = node_type
        self.x = x
        self.y = y
        self.width = NODE_WIDTH
        self.height = NODE_HEIGHT
        self.input_connector = (x, y + self.height // 2)
        self.output_connector = (x + self.width, y + self.height // 2)
        # Additional outputs for condition node
        self.true_output = (x + self.width, y + self.height // 3) if node_type == "condition" else None
        self.false_output = (x + self.width, y + 2 * self.height // 3) if node_type == "condition" else None
        self.selected = False
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.content = []  # List to store configuration content

        # Configuration button for non-input/output nodes
        self.config_button = pygame.Rect(
            self.x + self.width - 25,
            self.y + 5,
            20, 20
        ) if self.type not in ["input", "output"] else None

    def draw(self, surface, camera_offset_x, camera_offset_y):
        # Convert world coordinates to screen coordinates
        screen_x = self.x - camera_offset_x
        screen_y = self.y - camera_offset_y

        # Get the fill color based on node type
        fill_color = BUTTON_COLORS[BUTTON_TYPES.index(self.type)]

        # Draw node body
        pygame.draw.rect(surface, fill_color,
                         (screen_x, screen_y, self.width, self.height), 0, 10)

        # Draw border - darker for selected nodes
        border_color = NODE_SELECTED_COLOR if self.selected else (max(0, fill_color[0] - 40),
                                                                  max(0, fill_color[1] - 40),
                                                                  max(0, fill_color[2] - 40))
        pygame.draw.rect(surface, border_color,
                         (screen_x, screen_y, self.width, self.height), 2, 10)

        # Draw connectors
        if self.type != "input":
            input_connector_screen = (self.input_connector[0] - camera_offset_x,
                                      self.input_connector[1] - camera_offset_y)
            pygame.draw.circle(surface, CONNECTOR_COLORS[0], input_connector_screen, CONNECTOR_RADIUS)
            pygame.draw.circle(surface, (30, 80, 140), input_connector_screen, CONNECTOR_RADIUS, 2)

        if self.type != "output":
            # For condition node, draw two outputs
            if self.type == "condition":
                true_output_screen = (self.true_output[0] - camera_offset_x,
                                      self.true_output[1] - camera_offset_y)
                false_output_screen = (self.false_output[0] - camera_offset_x,
                                       self.false_output[1] - camera_offset_y)

                pygame.draw.circle(surface, (0, 255, 0), true_output_screen, CONNECTOR_RADIUS)
                pygame.draw.circle(surface, (0, 140, 210), true_output_screen, CONNECTOR_RADIUS, 2)

                pygame.draw.circle(surface, (255, 0, 0), false_output_screen, CONNECTOR_RADIUS)
                pygame.draw.circle(surface, (0, 140, 210), false_output_screen, CONNECTOR_RADIUS, 2)
            else:
                output_connector_screen = (self.output_connector[0] - camera_offset_x,
                                           self.output_connector[1] - camera_offset_y)
                pygame.draw.circle(surface, CONNECTOR_COLORS[1], output_connector_screen, CONNECTOR_RADIUS)
                pygame.draw.circle(surface, (0, 140, 210), output_connector_screen, CONNECTOR_RADIUS, 2)

        # Draw node label
        type_text = font.render(self.type, True, TEXT_COLOR)
        surface.blit(type_text, (screen_x + 10, screen_y + self.height // 2 - 10))

        # Draw configuration button for non-input/output nodes
        if self.config_button:
            config_button_screen = pygame.Rect(
                self.config_button.x - camera_offset_x,
                self.config_button.y - camera_offset_y,
                self.config_button.width,
                self.config_button.height
            )
            pygame.draw.rect(surface, (100, 180, 255), config_button_screen, 0, 5)  # Light blue button
            config_text = font.render("C", True, TEXT_COLOR)
            surface.blit(config_text,
                         (config_button_screen.centerx - config_text.get_width() // 2,
                          config_button_screen.centery - config_text.get_height() // 2))

    def update_connectors(self):
        self.input_connector = (self.x, self.y + self.height // 2)
        self.output_connector = (self.x + self.width, self.y + self.height // 2)

        # Update condition node outputs
        if self.type == "condition":
            self.true_output = (self.x + self.width, self.y + self.height // 3)
            self.false_output = (self.x + self.width, self.y + 2 * self.height // 3)

        # Update config button position
        if self.config_button:
            self.config_button.x = self.x + self.width - 25
            self.config_button.y = self.y + 5

    def contains_point(self, point, camera_offset_x, camera_offset_y):
        # Convert world point to screen point for comparison
        screen_x = self.x - camera_offset_x
        screen_y = self.y - camera_offset_y
        return (screen_x <= point[0] <= screen_x + self.width and
                screen_y <= point[1] <= screen_y + self.height)

    def input_contains_point(self, point, camera_offset_x, camera_offset_y):
        input_connector_screen = (self.input_connector[0] - camera_offset_x,
                                  self.input_connector[1] - camera_offset_y)
        dx = point[0] - input_connector_screen[0]
        dy = point[1] - input_connector_screen[1]
        return dx * dx + dy * dy <= CONNECTOR_RADIUS * CONNECTOR_RADIUS

    def output_contains_point(self, point, camera_offset_x, camera_offset_y):
        # Check all outputs for condition node
        if self.type == "condition":
            true_output_screen = (self.true_output[0] - camera_offset_x,
                                  self.true_output[1] - camera_offset_y)
            false_output_screen = (self.false_output[0] - camera_offset_x,
                                   self.false_output[1] - camera_offset_y)

            dx1 = point[0] - true_output_screen[0]
            dy1 = point[1] - true_output_screen[1]
            dx2 = point[0] - false_output_screen[0]
            dy2 = point[1] - false_output_screen[1]
            return (dx1 * dx1 + dy1 * dy1 <= CONNECTOR_RADIUS * CONNECTOR_RADIUS or
                    dx2 * dx2 + dy2 * dy2 <= CONNECTOR_RADIUS * CONNECTOR_RADIUS)
        elif self.type != "output":
            output_connector_screen = (self.output_connector[0] - camera_offset_x,
                                       self.output_connector[1] - camera_offset_y)
            dx = point[0] - output_connector_screen[0]
            dy = point[1] - output_connector_screen[1]
            return dx * dx + dy * dy <= CONNECTOR_RADIUS * CONNECTOR_RADIUS
        return False

    def get_output_at_point(self, point, camera_offset_x, camera_offset_y):
        """Returns which output connector is at the point (for condition nodes)"""
        if self.type == "condition":
            true_output_screen = (self.true_output[0] - camera_offset_x,
                                  self.true_output[1] - camera_offset_y)
            false_output_screen = (self.false_output[0] - camera_offset_x,
                                   self.false_output[1] - camera_offset_y)

            dx1 = point[0] - true_output_screen[0]
            dy1 = point[1] - true_output_screen[1]
            if dx1 * dx1 + dy1 * dy1 <= CONNECTOR_RADIUS * CONNECTOR_RADIUS:
                return "true"

            dx2 = point[0] - false_output_screen[0]
            dy2 = point[1] - false_output_screen[1]
            if dx2 * dx2 + dy2 * dy2 <= CONNECTOR_RADIUS * CONNECTOR_RADIUS:
                return "false"
        elif self.type != "output":
            output_connector_screen = (self.output_connector[0] - camera_offset_x,
                                       self.output_connector[1] - camera_offset_y)
            dx = point[0] - output_connector_screen[0]
            dy = point[1] - output_connector_screen[1]
            if dx * dx + dy * dy <= CONNECTOR_RADIUS * CONNECTOR_RADIUS:
                return "output"
        return None

    def config_button_contains_point(self, point, camera_offset_x, camera_offset_y):
        if not self.config_button:
            return False
        config_button_screen = pygame.Rect(
            self.config_button.x - camera_offset_x,
            self.config_button.y - camera_offset_y,
            self.config_button.width,
            self.config_button.height
        )
        return config_button_screen.collidepoint(point)


class Connection:
    def __init__(self, from_node, to_node, output_type="output"):
        self.from_node = from_node
        self.to_node = to_node
        self.output_type = output_type  # For condition nodes: "true" or "false"
        # Generate a random color for this connection
        self.color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))

    def draw(self, surface, camera_offset_x, camera_offset_y):
        # Determine start position based on output type
        if self.from_node.type == "condition":
            if self.output_type == "true":
                start_pos = self.from_node.true_output
            else:  # "false"
                start_pos = self.from_node.false_output
        else:
            start_pos = self.from_node.output_connector

        end_pos = self.to_node.input_connector

        # Convert to screen coordinates
        start_pos = (start_pos[0] - camera_offset_x, start_pos[1] - camera_offset_y)
        end_pos = (end_pos[0] - camera_offset_x, end_pos[1] - camera_offset_y)

        # Draw a bezier curve for the connection line
        control_point1 = (start_pos[0] + 50, start_pos[1])
        control_point2 = (end_pos[0] - 50, end_pos[1])

        # Draw multiple segments to create a smooth curve
        for i in range(20):
            t1 = i / 20
            t2 = (i + 1) / 20

            # Calculate points on the curve
            x1 = (1 - t1) ** 3 * start_pos[0] + 3 * (1 - t1) ** 2 * t1 * control_point1[0] + 3 * (1 - t1) * t1 ** 2 * \
                 control_point2[0] + t1 ** 3 * end_pos[0]
            y1 = (1 - t1) ** 3 * start_pos[1] + 3 * (1 - t1) ** 2 * t1 * control_point1[1] + 3 * (1 - t1) * t1 ** 2 * \
                 control_point2[1] + t1 ** 3 * end_pos[1]

            x2 = (1 - t2) ** 3 * start_pos[0] + 3 * (1 - t2) ** 2 * t2 * control_point1[0] + 3 * (1 - t2) * t2 ** 2 * \
                 control_point2[0] + t2 ** 3 * end_pos[0]
            y2 = (1 - t2) ** 3 * start_pos[1] + 3 * (1 - t2) ** 2 * t2 * control_point1[1] + 3 * (1 - t2) * t2 ** 2 * \
                 control_point2[1] + t2 ** 3 * end_pos[1]

            pygame.draw.line(surface, self.color, (x1, y1), (x2, y2), 2)

        # Draw arrowhead at the end
        direction = pygame.math.Vector2(end_pos[0] - control_point2[0], end_pos[1] - control_point2[1])
        if direction.length() > 0:
            direction.scale_to_length(10)
            arrow_left = pygame.math.Vector2(-direction.y, direction.x) * 0.3
            arrow_right = pygame.math.Vector2(direction.y, -direction.x) * 0.3

            arrow_points = [
                end_pos,
                (end_pos[0] - direction.x + arrow_left.x, end_pos[1] - direction.y + arrow_left.y),
                (end_pos[0] - direction.x + arrow_right.x, end_pos[1] - direction.y + arrow_right.y)
            ]

            pygame.draw.polygon(surface, self.color, arrow_points)

    def contains_point(self, point, camera_offset_x, camera_offset_y):
        if self.from_node.type == "condition":
            if self.output_type == "true":
                start_pos = self.from_node.true_output
            else:
                start_pos = self.from_node.false_output
        else:
            start_pos = self.from_node.output_connector

        end_pos = self.to_node.input_connector

        start_pos = (start_pos[0] - camera_offset_x, start_pos[1] - camera_offset_y)
        end_pos = (end_pos[0] - camera_offset_x, end_pos[1] - camera_offset_y)

        control_point1 = (start_pos[0] + 50, start_pos[1])
        control_point2 = (end_pos[0] - 50, end_pos[1])

        prev_x, prev_y = start_pos
        for i in range(1, 21):
            t = i / 20.0
            x = (1 - t) ** 3 * start_pos[0] + 3 * (1 - t) ** 2 * t * control_point1[0] + 3 * (1 - t) * t ** 2 * control_point2[0] + t ** 3 * end_pos[0]
            y = (1 - t) ** 3 * start_pos[1] + 3 * (1 - t) ** 2 * t * control_point1[1] + 3 * (1 - t) * t ** 2 * control_point2[1] + t ** 3 * end_pos[1]

            if point_to_segment_distance((prev_x, prev_y), (x, y), point) < 5:
                return True

            prev_x, prev_y = x, y

        return False


class Graph:
    def __init__(self):
        self.nodes = []
        self.connections = []
        self.next_node_id = 1

    def add_node(self, node_type, x, y):
        new_node = Node(self.next_node_id, node_type, x - 23, y + 70)
        self.nodes.append(new_node)
        self.next_node_id += 1
        return new_node

    def add_connection(self, from_node, to_node, output_type="output"):
        # Check if connection already exists
        for connection in self.connections:
            if (connection.from_node == from_node and
                    connection.to_node == to_node and
                    connection.output_type == output_type):
                return

        new_connection = Connection(from_node, to_node, output_type)
        self.connections.append(new_connection)

    def remove_node(self, node):
        # Remove all connections involving this node
        self.connections = [conn for conn in self.connections
                            if conn.from_node != node and conn.to_node != node]
        self.nodes.remove(node)

    def get_node_at(self, pos, camera_offset_x, camera_offset_y):
        for node in reversed(self.nodes):  # Check from top (last drawn) to bottom
            if node.contains_point(pos, camera_offset_x, camera_offset_y):
                return node
        return None

    def get_input_connector_at(self, pos, camera_offset_x, camera_offset_y):
        for node in reversed(self.nodes):
            if node.input_contains_point(pos, camera_offset_x, camera_offset_y):
                return node
        return None

    def get_output_connector_at(self, pos, camera_offset_x, camera_offset_y):
        for node in reversed(self.nodes):
            if node.output_contains_point(pos, camera_offset_x, camera_offset_y):
                return node
        return None

    def get_connection_at(self, pos, camera_offset_x, camera_offset_y):
        for conn in reversed(self.connections):
            if conn.contains_point(pos, camera_offset_x, camera_offset_y):
                return conn
        return None

    def to_dict(self):
        """Convert the graph to a dictionary for serialization"""
        graph_dict = {
            "nodes": [],
            "connections": []
        }

        node_id_map = {}
        for i, node in enumerate(self.nodes):
            node_id_map[node] = node.id
            graph_dict["nodes"].append({
                "id": node.id,
                "type": node.type,
                "x": node.x,
                "y": node.y,
                "content": node.content
            })

        for conn in self.connections:
            graph_dict["connections"].append({
                "from": node_id_map[conn.from_node],
                "to": node_id_map[conn.to_node],
                "output_type": conn.output_type
            })

        return graph_dict

    def from_dict(self, graph_dict):
        """Load the graph from a dictionary"""
        self.nodes = []
        self.connections = []

        node_id_map = {}
        for node_data in graph_dict["nodes"]:
            node = Node(node_data["id"], node_data["type"], node_data["x"], node_data["y"])
            node.content = node_data.get("content", [])
            self.nodes.append(node)
            node_id_map[node_data["id"]] = node
            if node.id >= self.next_node_id:
                self.next_node_id = node.id + 1

        for conn_data in graph_dict["connections"]:
            from_node = node_id_map[conn_data["from"]]
            to_node = node_id_map[conn_data["to"]]
            output_type = conn_data.get("output_type", "output")
            self.add_connection(from_node, to_node, output_type)


class Button:
    def __init__(self, x, y, width, height, text, color, node_type=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.node_type = node_type
        self.hovered = False

    def draw(self, surface):
        color = self.color
        if self.hovered:
            # Lighten the color when hovered
            color = tuple(min(c + 40, 255) for c in self.color)

        pygame.draw.rect(surface, color, self.rect, 0, 8)
        pygame.draw.rect(surface, (180, 180, 200), self.rect, 2, 8)  # Light gray border

        text_surf = font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def contains_point(self, point):
        return self.rect.collidepoint(point)


def draw_toolbar(surface, buttons):
    pygame.draw.rect(surface, TOOLBAR_COLOR, (0, 0, WIDTH, TOOLBAR_HEIGHT))

    # Draw title
    title = title_font.render("LLMTSup", True, BUTTON_COLORS[1])
    surface.blit(title, (20, TOOLBAR_HEIGHT // 2 - title.get_height() // 2))

    # Draw buttons
    for button in buttons:
        button.draw(surface)


def draw_connection_preview(surface, start_pos, end_pos):
    # Generate a random color for the preview line too
    preview_color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
    pygame.draw.line(surface, preview_color, start_pos, end_pos, 2)

    # Draw temporary connectors
    pygame.draw.circle(surface, CONNECTOR_HOVER_COLOR, start_pos, CONNECTOR_RADIUS)
    pygame.draw.circle(surface, CONNECTOR_HOVER_COLOR, end_pos, CONNECTOR_RADIUS)


def draw_graph_info(surface, graph):
    info_text = [
        f"Nodes: {len(graph.nodes)}",
        f"Connections: {len(graph.connections)}"
    ]

    y_pos = TOOLBAR_HEIGHT + 10
    for text in info_text:
        text_surf = font.render(text, True, (50, 80, 120))  # Dark blue text
        surface.blit(text_surf, (WIDTH - text_surf.get_width() - 20, y_pos))
        y_pos += text_surf.get_height() + 5


def save_graph_screenshot(surface, file_path):
    """Save a screenshot of the graph area"""
    # Create a surface for the graph area (excluding toolbar and help text)
    graph_area = pygame.Rect(0, TOOLBAR_HEIGHT, WIDTH, HEIGHT - TOOLBAR_HEIGHT - 150)
    graph_surface = pygame.Surface((graph_area.width, graph_area.height))
    graph_surface.blit(surface, (0, 0), graph_area)

    # Save to file
    pygame.image.save(graph_surface, file_path)
    print(f"Graph image saved to {file_path}")


def open_tk_config(node, undo_stack, redo_stack):
    root = tk.Tk()
    root.title(f"Configure {node.type} Node")

    if node.type == "retrieval":
        frame = tk.Frame(root)
        frame.pack(pady=5)

        tk.Label(frame, text="Retrieval Document").pack(side=tk.LEFT, padx=5)

        current_path = node.content[0] if node.content else ""
        path_label = tk.Label(frame, text=current_path, relief=tk.SUNKEN, width=50)
        path_label.pack(side=tk.LEFT, padx=5)

        def load_file():
            file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if file_path:
                path_label.config(text=file_path)

        tk.Button(frame, text="Load Document", command=load_file).pack(side=tk.LEFT, padx=5)

        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        def save():
            undo_stack.append(graph.to_dict())
            redo_stack.clear()
            node.content = [path_label.cget("text")]
            root.destroy()

        tk.Button(button_frame, text="Save", command=save).pack(side=tk.LEFT, padx=10)

        def cancel():
            root.destroy()

        tk.Button(button_frame, text="Cancel", command=cancel).pack(side=tk.LEFT, padx=10)
    else:
        field_descriptions = CONFIG_FIELDS.get(node.type, [])

        texts = []
        for i, desc in enumerate(field_descriptions):
            frame = tk.Frame(root)
            frame.pack(pady=5)

            tk.Label(frame, text=desc).pack(side=tk.LEFT, padx=5)

            text = tk.Text(frame, height=10, width=50, undo=True)
            if i < len(node.content):
                text.insert(tk.END, node.content[i])
            text.pack(side=tk.LEFT, padx=5)

            def load_file(t=text):
                file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
                if file_path:
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                        t.insert(tk.END, content)
                    except Exception as e:
                        print(f"Error loading file: {e}")

            tk.Button(frame, text="Load .txt", command=load_file).pack(side=tk.LEFT, padx=5)

            texts.append(text)

        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        def save():
            # Save state before applying changes
            undo_stack.append(graph.to_dict())
            redo_stack.clear()
            node.content = [t.get("1.0", tk.END).strip() for t in texts]
            root.destroy()

        tk.Button(button_frame, text="Save", command=save).pack(side=tk.LEFT, padx=10)

        def cancel():
            root.destroy()

        tk.Button(button_frame, text="Cancel", command=cancel).pack(side=tk.LEFT, padx=10)

    root.mainloop()


def main():
    global graph
    graph = Graph()

    # Undo/Redo stacks
    undo_stack = []
    redo_stack = []

    # Camera offset for panning
    camera_offset_x = 0
    camera_offset_y = 0
    panning = False
    pan_start_x = 0
    pan_start_y = 0

    # Create toolbar buttons
    buttons = [
        Button(140, 10, 88, 40, "Input", BUTTON_COLORS[0], "input"),
        Button(230, 10, 88, 40, "Retrieval", BUTTON_COLORS[1], "retrieval"),
        Button(320, 10, 88, 40, "LLM-Query", BUTTON_COLORS[2], "query"),
        Button(410, 10, 88, 40, "Condition", BUTTON_COLORS[5], "condition"),
        Button(500, 10, 88, 40, "Memory", BUTTON_COLORS[4], "memory"),
        Button(590, 10, 88, 40, "Output", BUTTON_COLORS[3], "output"),
    ]

    # Create a save/load button
    save_button = Button(WIDTH - 250, 10, 110, 40, "Save Graph", BUTTON_COLORS[1])
    load_button = Button(WIDTH - 130, 10, 110, 40, "Load Graph", BUTTON_COLORS[1])
    buttons.extend([save_button, load_button])

    # State variables
    dragging_node = None
    connecting_start = None
    connecting_start_output = None
    connecting_end = None
    selected_node = None
    input_exists = False

    clock = pygame.time.Clock()

    def perform_undo():
        nonlocal input_exists
        if undo_stack:
            current_state = graph.to_dict()
            redo_stack.append(current_state)
            prev_state = undo_stack.pop()
            graph.from_dict(prev_state)
            input_exists = any(n.type == "input" for n in graph.nodes)

    def perform_redo():
        nonlocal input_exists
        if redo_stack:
            current_state = graph.to_dict()
            undo_stack.append(current_state)
            next_state = redo_stack.pop()
            graph.from_dict(next_state)
            input_exists = any(n.type == "input" for n in graph.nodes)

    while True:
        mouse_pos = pygame.mouse.get_pos()

        # Convert mouse position to world coordinates for graph interactions
        world_mouse_pos = (mouse_pos[0] + camera_offset_x, mouse_pos[1] + camera_offset_y)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if clicked on a toolbar button
                for button in buttons:
                    if button.contains_point(mouse_pos):
                        if button == save_button:
                            # Save graph to file
                            json_file = "graph.json"
                            with open(json_file, "w") as f:
                                json.dump(graph.to_dict(), f, indent=2)
                            print(f"Graph saved to {json_file}")

                            # Save screenshot
                            screenshot_file = os.path.splitext(json_file)[0] + ".png"
                            save_graph_screenshot(screen, screenshot_file)
                        elif button == load_button:
                            # Load graph from file
                            json_file = "graph.json"
                            try:
                                undo_stack.append(graph.to_dict())
                                redo_stack.clear()
                                with open(json_file, "r") as f:
                                    data = json.load(f)
                                graph.from_dict(data)
                                input_exists = any(n.type == "input" for n in graph.nodes)
                                print(f"Graph loaded from {json_file}")
                            except Exception as e:
                                print(f"Error loading graph: {str(e)}")
                        elif button.node_type:
                            # Create a new node
                            if not button.node_type == "input" or (button.node_type == "input" and not input_exists):
                                undo_stack.append(graph.to_dict())
                                redo_stack.clear()
                                new_node = graph.add_node(button.node_type, world_mouse_pos[0], world_mouse_pos[1])
                                selected_node = new_node
                                for node in graph.nodes:
                                    node.selected = (node == new_node)

                                if button.node_type == "input":
                                    input_exists = True
                        break
                else:
                    # Check if right-click on connection
                    if event.button == 3:  # Right mouse button
                        clicked_conn = graph.get_connection_at(mouse_pos, camera_offset_x, camera_offset_y)
                        if clicked_conn:
                            undo_stack.append(graph.to_dict())
                            redo_stack.clear()
                            graph.connections.remove(clicked_conn)
                            continue

                    # Check if clicked on background for panning
                    if not any(button.contains_point(mouse_pos) for button in buttons) and \
                            not graph.get_node_at(mouse_pos, camera_offset_x, camera_offset_y) and \
                            not connecting_start:
                        panning = True
                        pan_start_x = mouse_pos[0]
                        pan_start_y = mouse_pos[1]

                    # Check if clicked on a node's config button
                    for node in graph.nodes:
                        if node.config_button and node.config_button_contains_point(mouse_pos, camera_offset_x,
                                                                                    camera_offset_y):
                            # Open tk configuration window for this node
                            open_tk_config(node, undo_stack, redo_stack)
                            break

                    # Check if clicked on a node connector
                    output_node = graph.get_output_connector_at(mouse_pos, camera_offset_x, camera_offset_y)
                    if output_node:
                        connecting_start = output_node
                        connecting_start_output = output_node.get_output_at_point(mouse_pos, camera_offset_x,
                                                                                  camera_offset_y)
                        connecting_end = mouse_pos
                        continue

                    # Check if clicked on a node
                    clicked_node = graph.get_node_at(mouse_pos, camera_offset_x, camera_offset_y)
                    if event.button == 3:  # Right mouse button
                        if clicked_node:
                            # Handle right-click for deletion
                            undo_stack.append(graph.to_dict())
                            redo_stack.clear()
                            if clicked_node.type == "input":
                                input_exists = False
                            graph.remove_node(clicked_node)
                            if clicked_node == selected_node:
                                selected_node = None
                    elif clicked_node:
                        # Select node and start dragging
                        undo_stack.append(graph.to_dict())
                        redo_stack.clear()
                        dragging_node = clicked_node
                        dragging_node.dragging = True
                        dragging_node.drag_offset_x = world_mouse_pos[0] - dragging_node.x
                        dragging_node.drag_offset_y = world_mouse_pos[1] - dragging_node.y

                        # Deselect other nodes
                        for node in graph.nodes:
                            node.selected = (node == dragging_node)
                        selected_node = dragging_node
                    else:
                        # Clicked on empty space - deselect all
                        for node in graph.nodes:
                            node.selected = False
                        selected_node = None

            elif event.type == pygame.MOUSEBUTTONUP:
                if dragging_node:
                    dragging_node.dragging = False
                    dragging_node = None

                if connecting_start and connecting_end:
                    # Check if released on an input connector
                    input_node = graph.get_input_connector_at(mouse_pos, camera_offset_x, camera_offset_y)
                    if input_node and input_node != connecting_start and input_node.type != "input":
                        undo_stack.append(graph.to_dict())
                        redo_stack.clear()
                        graph.add_connection(connecting_start, input_node, connecting_start_output)

                    connecting_start = None
                    connecting_start_output = None
                    connecting_end = None

                if panning:
                    panning = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    perform_undo()
                elif event.key == pygame.K_y and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    perform_redo()
                elif event.key == pygame.K_DELETE and selected_node:
                    undo_stack.append(graph.to_dict())
                    redo_stack.clear()
                    graph.remove_node(selected_node)
                    selected_node = None

        # Handle dragging
        if dragging_node:
            dragging_node.x = world_mouse_pos[0] - dragging_node.drag_offset_x
            dragging_node.y = world_mouse_pos[1] - dragging_node.drag_offset_y
            dragging_node.update_connectors()

        # Handle panning
        if panning:
            dx = mouse_pos[0] - pan_start_x
            dy = mouse_pos[1] - pan_start_y
            camera_offset_x -= dx
            camera_offset_y -= dy
            pan_start_x = mouse_pos[0]
            pan_start_y = mouse_pos[1]

        # Update connection preview
        if connecting_start:
            connecting_end = mouse_pos

        # Update button hover states
        for button in buttons:
            button.hovered = button.contains_point(mouse_pos)

        # Draw everything
        screen.fill(BG_COLOR)

        # Draw connections
        for connection in graph.connections:
            connection.draw(screen, camera_offset_x, camera_offset_y)

        # Draw connection preview if in progress
        if connecting_start and connecting_end:
            # Determine start position based on output type
            if connecting_start.type == "condition":
                if connecting_start_output == "true":
                    start_pos = connecting_start.true_output
                else:  # "false"
                    start_pos = connecting_start.false_output
            else:
                start_pos = connecting_start.output_connector

            # Convert start position to screen coordinates
            start_pos_screen = (start_pos[0] - camera_offset_x, start_pos[1] - camera_offset_y)
            draw_connection_preview(screen, start_pos_screen, connecting_end)

        # Draw nodes
        for node in graph.nodes:
            node.draw(screen, camera_offset_x, camera_offset_y)

        # Draw toolbar
        draw_toolbar(screen, buttons)

        # Draw graph info
        draw_graph_info(screen, graph)

        # Draw help text
        help_text = [
            "Left-click: Select/Move nodes",
            "Right-click: Delete nodes or connections",
            "Drag from output to input: Create connection",
            "'C' button: Configure node",
            "In config window: Use Load .txt button",
            "Condition nodes have two outputs: true and false",
            "Click and drag background to pan",
            "Ctrl+Z: Undo, Ctrl+Y: Redo"
        ]

        y_pos = HEIGHT - 150
        for text in help_text:
            text_surf = font.render(text, True, (50, 80, 120))  # Dark blue text
            screen.blit(text_surf, (20, y_pos))
            y_pos += 25

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()