import sys
import os
import re
import json
import hashlib
from typing import Dict, Any, List
import time  # Added for timing
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Import our custom modules
from llmclient import get_llm_client, LLMClient, initialize_api_keys, APIConfig

# --- Initialize Configuration ---
config = initialize_api_keys()

# --- LLM and Embeddings Initialization ---
llm_client = get_llm_client("google", model_name="gemini-2.0-flash-lite")
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
script_dir = os.path.dirname(os.path.abspath(__file__))

# --- Graph Data Structures ---
class Node:
    def __init__(self, node_id: int, node_type: str, content=None):
        self.id = node_id
        self.type = node_type
        self.content = content or []

class Connection:
    def __init__(self, from_node: Node, to_node: Node, output_type="output"):
        self.from_node = from_node
        self.to_node = to_node
        self.output_type = output_type

class Graph:
    def __init__(self):
        self.nodes = []
        self.connections = []
        self.next_node_id = 1

    def get_node_by_id(self, node_id: int) -> Node:
        return next((n for n in self.nodes if n.id == node_id), None)

    def get_inp_node(self):
        for n in self.nodes:
            if n.type == 'input':
                return n
        return None

    def get_incoming_edge_nodes(self, node: Node):
        return [c.from_node for c in self.connections if c.to_node == node]

    def get_outgoing_edge_nodes(self, node: Node):
        return [c.to_node for c in self.connections if c.from_node == node]

    def add_node(self, node_type: str, content=None) -> Node:
        node = Node(self.next_node_id, node_type, content)
        self.nodes.append(node)
        self.next_node_id += 1
        return node

    def add_connection(self, from_node: Node, to_node: Node, output_type="output"):
        for connection in self.connections:
            if (connection.from_node == from_node and
                    connection.to_node == to_node and
                    connection.output_type == output_type):
                return
        new_connection = Connection(from_node, to_node, output_type)
        self.connections.append(new_connection)

    def remove_node(self, node: Node):
        self.connections = [c for c in self.connections if c.from_node != node and c.to_node != node]
        self.nodes.remove(node)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [{"id": n.id, "type": n.type, "content": n.content} for n in self.nodes],
            "connections": [{"from": c.from_node.id, "to": c.to_node.id, "output_type": c.output_type} for c in
                            self.connections]
        }

    def from_dict(self, graph_dict):
        self.nodes = []
        self.connections = []
        node_id_map = {}
        for node_data in graph_dict["nodes"]:
            node = Node(node_data["id"], node_data["type"])
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

    def topological_sort(self) -> List[int]:
        indegree = {n.id: 0 for n in self.nodes}
        for c in self.connections:
            indegree[c.to_node.id] += 1
        queue = [n.id for n in self.nodes if indegree[n.id] == 0]
        order = []
        while queue:
            nid = queue.pop(0)
            order.append(nid)
            for c in self.connections:
                if c.from_node.id == nid:
                    indegree[c.to_node.id] -= 1
                    if indegree[c.to_node.id] == 0:
                        queue.append(c.to_node.id)
        if len(order) != len(self.nodes):
            raise ValueError("Cycle detected in the graph; cannot proceed.")
        return order

# --- DAG-Based RAG Workflow ---
class LLMWorkflow:
    def __init__(self, graph: Graph, llm_client: LLMClient, config: APIConfig = None):
        self.graph = graph
        self.llm_client = llm_client
        self.config = config or initialize_api_keys()
        self.node_funcs: Dict[int, Any] = {}
        self.exec_order: List[int] = []

    def get_graph(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.graph.from_dict(data)
            print("Graph loaded:")
            print(json.dumps(self.graph.to_dict(), indent=2))
        except FileNotFoundError:
            print(f"No saved graph at {path}")

    def clear_memory(self):
        memory_nodes = [node for node in self.graph.nodes if node.type == 'memory']
        for memory_node in memory_nodes:
            file_path = os.path.join(script_dir, f"memory_{memory_node.content[0]}.txt")
            with open(file_path, 'w', encoding='utf-8') as f:
                pass  # Clear the file

    def _get_faiss_index_path(self, node: Node) -> str:
        if not node.content:
            raise ValueError(f"Retrieval node {node.id} has no content specified")
        document_source = node.content[0]
        clean_name = os.path.splitext(document_source)[0]
        clean_name = re.sub(r'[^\w\-_]', '_', clean_name)
        index_name = f"faiss_{clean_name}"
        return os.path.join(script_dir, index_name)

    def _load_or_create_vector_store(self, node: Node):
        index_dir = self._get_faiss_index_path(node)
        document_source = node.content[0]
        if os.path.exists(index_dir):
            print(f"[Node {node.id}] Loading existing FAISS index from {index_dir} for document: {document_source}")
            return FAISS.load_local(index_dir, embeddings, allow_dangerous_deserialization=True)
        print(f"[Node {node.id}] Creating new FAISS index for document: {document_source}")
        file_path = os.path.join(script_dir, document_source)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                print(f"[Node {node.id}] Loaded document from {document_source} ({len(text)} chars)")
        except FileNotFoundError:
            raise FileNotFoundError(f"Document not found for retrieval node {node.id}: {file_path}")
        except Exception as e:
            raise Exception(f"Error loading document {file_path} for node {node.id}: {e}")
        doc = Document(
            page_content=text,
            metadata={"source": document_source}
        )
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=100,
            add_start_index=True,
            separators=["", "", ""]
        )
        chunks = splitter.split_documents([doc])
        print(f"[Node {node.id}] Created {len(chunks)} chunks from document: {document_source}")
        vector_store = FAISS.from_documents(chunks, embeddings)
        vector_store.save_local(index_dir)
        print(f"[Node {node.id}] Saved FAISS index to {index_dir}")
        return vector_store

    def _write_to_memory(self, file_path: str, data: Any):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                existing = f.read()
        except FileNotFoundError:
            existing = ""
        numbers = re.findall(r"--- START LOG #(\d+) ---", existing)
        next_num = max([int(n) for n in numbers] + [0]) + 1
        entry = f"--- START LOG #{next_num} ---\n{str(data)}\n--- END LOG #{next_num} ---\n\n"
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(entry)

    def build(self):
        start_node = self.graph.get_inp_node()
        reachable = [start_node]

        def reachable_nodes(node: Node):
            if node not in reachable:
                reachable.append(node)
            out = self.graph.get_outgoing_edge_nodes(node)
            for n in out:
                reachable_nodes(n)

        reachable_nodes(start_node)
        for n in self.graph.nodes[:]:
            if n not in reachable:
                self.graph.remove_node(n)

        def input_factory(node: Node):
            def fn(state: Dict[str, Any]) -> Dict[str, Any]:
                print(f"[Node {node.id} - INPUT] question='{state['question']}'")
                state["activation"][str(node.id)] = True
                state['data'][str(node.id)] = state['question']
                memory_targets = [c.to_node.id for c in self.graph.connections if
                                  c.from_node == node and c.to_node.type == 'memory']
                for memory_node_id in memory_targets:
                    memory_node = self.graph.get_node_by_id(memory_node_id)
                    file_path = os.path.join(script_dir, f"memory_{memory_node.content[0]}.txt")
                    try:
                        self._write_to_memory(file_path, state['data'][str(node.id)])
                    except (PermissionError, OSError) as e:
                        print(f"Error writing to {file_path}: {e}")
                return state
            return fn

        def retrieval_factory(node: Node):
            def fn(state: Dict[str, Any]) -> Dict[str, Any]:
                incoming = self.graph.get_incoming_edge_nodes(node)
                flag = True
                for i in incoming:
                    if i.type != "condition":
                        if str(i.id) in state['activation'].keys() and not state['activation'][str(i.id)]:
                            flag = False
                        elif str(i.id) not in state['activation'].keys():
                            flag = False
                    else:
                        if str(i.id) in state['data'].keys() and str(node.id) not in state["data"][str(i.id)]:
                            flag = False
                        elif str(i.id) not in state['data'].keys():
                            flag = False
                if flag:
                    print(f"[Node {node.id} - RETRIEVAL] Processing with sources: {node.content}")
                    try:
                        vector_store = self._load_or_create_vector_store(node)
                    except Exception as e:
                        print(f"[Node {node.id}] Error creating vector store: {e}")
                        state["activation"][str(node.id)] = False
                        return state
                    texts = [state['data'][str(i.id)] for i in incoming if i.type != "condition"]
                    print(f"[Node {node.id} - RETRIEVAL] inputs={texts}")
                    query_text = "".join(texts)
                    docs = vector_store.similarity_search(query_text, k=4)
                    retrieved_content = "\n\n".join(doc.page_content for doc in docs)
                    print(f"[Node {node.id}] Retrieved {len(docs)} documents:")
                    for i, doc in enumerate(docs):
                        source = doc.metadata.get('source', 'unknown')
                        preview = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
                        print(f"  Doc {i + 1} from {source}: {preview}")
                    state["data"][str(node.id)] = retrieved_content
                    state["activation"][str(node.id)] = True
                    memory_targets = [c.to_node.id for c in self.graph.connections if
                                      c.from_node == node and c.to_node.type == 'memory']
                    for memory_node_id in memory_targets:
                        memory_node = self.graph.get_node_by_id(memory_node_id)
                        file_path = os.path.join(script_dir, f"memory_{memory_node.content[0]}.txt")
                        try:
                            self._write_to_memory(file_path, state['data'][str(node.id)])
                        except (PermissionError, OSError) as e:
                            print(f"Error writing to {file_path}: {e}")
                else:
                    state["activation"][str(node.id)] = False
                return state
            return fn

        def condition_factory(node: Node):
            def fn(state: Dict[str, Any]) -> Dict[str, Any]:
                incoming = self.graph.get_incoming_edge_nodes(node)
                flag = True
                for i in incoming:
                    if i.type != "condition":
                        if str(i.id) in state['activation'].keys() and not state['activation'][str(i.id)]:
                            flag = False
                        elif str(i.id) not in state['activation'].keys():
                            flag = False
                    else:
                        if str(i.id) in state['data'].keys() and str(node.id) not in state["data"][str(i.id)]:
                            flag = False
                        elif str(i.id) not in state['data'].keys():
                            flag = False
                if flag:
                    state["activation"][str(node.id)] = True
                    texts = [str(state['data'][str(i.id)]) for i in incoming if i.type != "condition"]
                    if len(node.content) == 0:
                        raise ValueError(f"Condition node empty")
                    print(node.content[0])
                    print(''.join(texts))
                    if node.content[0] in ''.join(texts):
                        state['data'][str(node.id)] = [str(c.to_node.id) for c in self.graph.connections if
                                                       c.from_node == node and c.output_type == "true"]
                        print("True")
                    else:
                        state['data'][str(node.id)] = [str(c.to_node.id) for c in self.graph.connections if
                                                       c.from_node == node and c.output_type == "false"]
                        print("False")
                    memory_targets = [c.to_node.id for c in self.graph.connections if
                                      c.from_node == node and c.to_node.type == 'memory']
                    for memory_node_id in memory_targets:
                        memory_node = self.graph.get_node_by_id(memory_node_id)
                        file_path = os.path.join(script_dir, f"memory_{memory_node.content[0]}.txt")
                        try:
                            self._write_to_memory(file_path, state['data'][str(node.id)])
                        except (PermissionError, OSError) as e:
                            print(f"Error writing to {file_path}: {e}")
                else:
                    state["activation"][str(node.id)] = False
                return state
            return fn

        def query_factory(node: Node):
            def fn(state: Dict[str, Any]) -> Dict[str, Any]:
                incoming = self.graph.get_incoming_edge_nodes(node)
                flag = True
                for i in incoming:
                    if i.type != "condition":
                        if str(i.id) in state['activation'].keys() and not state['activation'][str(i.id)]:
                            flag = False
                        elif str(i.id) not in state['activation'].keys():
                            flag = False
                    else:
                        if str(i.id) in state['data'].keys() and str(node.id) not in state["data"][str(i.id)]:
                            flag = False
                        elif str(i.id) not in state['data'].keys():
                            flag = False
                if flag:
                    state["activation"][str(node.id)] = True
                    inputs = [str(state['data'][str(i.id)]) for i in incoming if i.type != "condition"]
                    print(f"[Node {node.id} - QUERY] prompt_parts={node.content + inputs}")
                    prompt = "".join(node.content) + "".join(inputs)
                    out = self.llm_client.invoke(prompt)
                    print(f"[Node {node.id}] LLM output='{out}'")
                    state['data'][str(node.id)] = out
                    memory_targets = [c.to_node.id for c in self.graph.connections if
                                      c.from_node == node and c.to_node.type == 'memory']
                    for memory_node_id in memory_targets:
                        memory_node = self.graph.get_node_by_id(memory_node_id)
                        file_path = os.path.join(script_dir, f"memory_{memory_node.content[0]}.txt")
                        try:
                            self._write_to_memory(file_path, state['data'][str(node.id)])
                        except (PermissionError, OSError) as e:
                            print(f"Error writing to {file_path}: {e}")
                else:
                    state["activation"][str(node.id)] = False
                return state
            return fn

        def memory_factory(node: Node):
            def fn(state: Dict[str, Any]) -> Dict[str, Any]:
                file_path = os.path.join(script_dir, f"memory_{node.content[0]}.txt")
                content = ""
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                    logs = re.findall(r"--- START LOG #(\d+) ---\n(.*?)\n--- END LOG #\d+ ---\n\n", text, re.DOTALL)
                    for num, data in logs:
                        content += f"History entry {num}: {data.strip()}\n\n"
                except FileNotFoundError:
                    content = ""
                state['data'][str(node.id)] = content
                state['activation'][str(node.id)] = True
                memory_targets = [c.to_node.id for c in self.graph.connections if
                                  c.from_node == node and c.to_node.type == 'memory']
                for memory_node_id in memory_targets:
                    memory_node = self.graph.get_node_by_id(memory_node_id)
                    file_path = os.path.join(script_dir, f"memory_{memory_node.content[0]}.txt")
                    try:
                        self._write_to_memory(file_path, state['data'][str(node.id)])
                    except (PermissionError, OSError) as e:
                        print(f"Error writing to {file_path}: {e}")
                return state
            return fn

        def output_factory(node: Node):
            def fn(state: Dict[str, Any]) -> Dict[str, Any]:
                incoming = self.graph.get_incoming_edge_nodes(node)
                parts = [state['data'][str(i.id)] for i in incoming if str(i.id) in state['data'].keys()]
                print("Test:", parts)
                print(f"[Node {node.id} - OUTPUT] parts={parts}")
                state['answer'] = "".join(parts)
                state['data'][str(node.id)] = state['answer']
                state["activation"][str(node.id)] = True
                memory_targets = [c.to_node.id for c in self.graph.connections if
                                  c.from_node == node and c.to_node.type == 'memory']
                for memory_node_id in memory_targets:
                    memory_node = self.graph.get_node_by_id(memory_node_id)
                    file_path = os.path.join(script_dir, f"memory_{memory_node.content[0]}.txt")
                    try:
                        self._write_to_memory(file_path, state['data'][str(node.id)])
                    except (PermissionError, OSError) as e:
                        print(f"Error writing to {file_path}: {e}")
                return state
            return fn

        for node in self.graph.nodes:
            if node.type == 'input':
                self.node_funcs[node.id] = input_factory(node)
            elif node.type == 'retrieval':
                self.node_funcs[node.id] = retrieval_factory(node)
            elif node.type == 'query':
                self.node_funcs[node.id] = query_factory(node)
            elif node.type == 'condition':
                self.node_funcs[node.id] = condition_factory(node)
            elif node.type == 'memory':
                self.node_funcs[node.id] = memory_factory(node)
            elif node.type == 'output':
                self.node_funcs[node.id] = output_factory(node)
            else:
                raise ValueError(f"Unsupported node type: {node.type}")

        self.exec_order = self.graph.topological_sort()

    def ask_question(self, question: str) -> str:
        state: Dict[str, Any] = {'question': question, 'data': {}, 'activation': {}, 'answer': ''}
        print(f"Starting workflow for question: '{question}'")
        start_time = time.time()  # Record start time
        for nid in self.exec_order:
            print(f"\n---> Executing node {nid} ({self.graph.get_node_by_id(nid).type})")
            state = self.node_funcs[nid](state)
        end_time = time.time()  # Record end time
        total_time = end_time - start_time  # Calculate total time
        print(f"\n[Workflow Completed] Total processing time: {total_time:.2f} seconds")
        return str(state['answer'])

    def cleanup_faiss_indexes(self):
        pattern = r'faiss_node_\d+_[a-f0-9]{8}'
        for item in os.listdir(script_dir):
            if re.match(pattern, item) and os.path.isdir(os.path.join(script_dir, item)):
                import shutil
                try:
                    shutil.rmtree(os.path.join(script_dir, item))
                    print(f"Deleted FAISS index directory: {item}")
                except Exception as e:
                    print(f"Failed to delete {item}: {e}")

def prompt(inp, provider="google", **llm_kwargs):
    config = initialize_api_keys()
    llm_client = get_llm_client(provider, **llm_kwargs)
    graph = Graph()
    workflow = LLMWorkflow(graph, llm_client, config)
    workflow.get_graph('graph.json')
    workflow.build()
    ans = workflow.ask_question(inp)
    return ans

def delete_memory():
    for filename in os.listdir('.'):
        if re.fullmatch(r'memory_.*\.txt', filename):
            print(filename)
            try:
                os.remove(filename)
                print(f"Deleted: {filename}")
            except Exception as e:
                print(f"Failed to delete {filename}: {e}")

def cleanup_all():
    delete_memory()
    graph = Graph()
    workflow = LLMWorkflow(graph, None)
    workflow.cleanup_faiss_indexes()

if __name__ == '__main__':
    cleanup_all()
    result1 = prompt("Reset the original state please")
    print("Res:", result1)