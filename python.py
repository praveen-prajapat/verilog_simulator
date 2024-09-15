# 1.The code will only works when verilog file is written in structural modelling (with no other instantiation than standered gates)
# 2.We have to change number of inputs in python file as per inputs in our verilog file (line: )
# 3.The design must have only one output
# 4.A tracefile will get generated (tracefile.txt) containing simulation results
# requirements - pyverilog, networkx, itertools, matplotlib

import pyverilog.vparser.ast as vast
from pyverilog.vparser.parser import parse
import networkx as nx
import matplotlib.pyplot as plt
import itertools

# parsing the verilog file and store node and function of logic gates as label to that nodes
def parse_verilog_to_graph(filename):
    ast, _ = parse([filename])
    G = nx.DiGraph()

    for module in ast.description.definitions:
        if isinstance(module, vast.ModuleDef):
            for item in module.items:
                if isinstance(item, vast.InstanceList):
                    for instance in item.instances:
                        gate_type = instance.module
                        output = instance.portlist[0].argname.name
                        inputs = [port.argname.name for port in instance.portlist[1:]]

                        G.add_node(output, label=gate_type)
                        for inp in inputs:
                            G.add_edge(inp, output)
    return G

# Traversing the graph to identify different level helps in clear visualization
def compute_levels(G):
    levels = {}
    for node in nx.topological_sort(G):
        in_edges = list(G.in_edges(node))
        if not in_edges:
            levels[node] = 0
        else:
            levels[node] = max(levels[u] for u, _ in in_edges) + 1
    return levels

# Showing an symmtric graph (center aligned and level wise)
def draw_center_aligned_graph(G):
    levels = compute_levels(G)
    level_nodes = {}

    for node, level in levels.items():
        if level not in level_nodes:
            level_nodes[level] = []
        level_nodes[level].append(node)

    pos = {}
    for level, nodes in level_nodes.items():
        num_nodes = len(nodes)
        spacing = 2.0
        start_x = -spacing * (num_nodes - 1) / 2
        for i, node in enumerate(nodes):
            pos[node] = (start_x + i * spacing, -level)

    node_labels = nx.get_node_attributes(G, 'label')
    nx.draw(G, pos, with_labels=True, labels=node_labels, node_size=2000, node_color="lightblue", font_size=10)
    plt.show()

# Defining some standered logic gates
def simulate_logic(gate_type, inputs):
    if gate_type == 'and':
        return int(all(inputs))
    elif gate_type == 'or':
        return int(any(inputs))
    elif gate_type == 'not':
        return int(not inputs[0])
    elif gate_type == 'nand':
        return int(not all(inputs))
    elif gate_type == 'nor':
        return int(not any(inputs))
    elif gate_type == 'xor':
        return int(sum(inputs) % 2)
    elif gate_type == 'xnor':
        return int(sum(inputs) % 2 == 0)
    else:
        raise ValueError(f"Gate not found")

# Simulating the graph for all possible combination of inputs
def simulate_verilog_graph(G, input_names):
    results = {}
    input_combinations = list(itertools.product([0, 1], repeat=len(input_names)))
    
    for input_combination in input_combinations:
        input_values = dict(zip(input_names, input_combination))
        node_values = {}
        
        for node in nx.topological_sort(G):
            if node in input_names:
                node_values[node] = input_values[node]
            else: 
                gate_type = G.nodes[node]['label']
                inputs = [node_values[pre_node] for pre_node, _ in G.in_edges(node)]
                node_values[node] = simulate_logic(gate_type, inputs)

        output_values = {node: value for node, value in node_values.items() if G.out_degree(node) == 0}
        results[input_combination] = output_values

    return results

# Making a tracefile containing outputs corresponding to different combination of outputs
def write_results_to_file(simulation_results, filename="tracefile.txt"):
    with open(filename, "w") as file:
        for inputs, outputs in simulation_results.items():
            input_str = ', '.join(f'{name}={value}' for name, value in zip(input_names, inputs))
            output_str = ', '.join(f'{name}={value}' for name, value in outputs.items())
            file.write(f"Inputs: {input_str} => Outputs: {output_str}\n")


# Main function
if __name__ == "__main__":
    filename = "Simulator_test.v"  
    graph = parse_verilog_to_graph(filename)
    draw_center_aligned_graph(graph)

    # We have to change no of inputs here according to inputs of module in verilog file
    input_names = ["a", "b","c","d","e"] 
    simulation_results = simulate_verilog_graph(graph, input_names)
    write_results_to_file(simulation_results)
