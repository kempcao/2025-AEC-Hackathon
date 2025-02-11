# 2025-AEC Hackathon

## Pattern Recognition with Graph Databases for Industrialized Construction

### Background
Implenia develops a system for the industrialized construction of housing projects. This system is based on a **Reference Design**: a flexible floorplan that can be stretched and adapted to different environments. The components of the system, known as the **Kit-of-Parts**, are predefined modular elements ("lego blocks") that can be combined to create a variety of configurations. These predefined components enable faster, more efficient construction while maintaining flexibility and adaptability.

### Problem
Let’s suppose we start from a random design that was not developed for industrialized construction. The challenge is: 

**How can we apply a kit-of-parts logic to any floorplan?**

This requires the ability to analyze, compare, and adapt arbitrary floorplans to align with the principles of industrialized construction, leveraging the Kit-of-Parts system.

### Envisioned Workflow
The envisioned workflow for addressing this challenge consists of three steps:

![Envisioned Workflow](images/workflow.png)

#### Step 1 (solved): Create Graph Representation of Generic Floorplan
A graph representation is generated for any generic floorplan, capturing spatial relationships and structural elements. This allows for a computational analysis of the design.

#### Step 2 (to be solved): Compare Graph to Reference Design
The graph representation of the generic floorplan is compared to a reference design, which serves as a standard case based on the Kit-of-Parts. The goal is to identify similarities and discrepancies, paving the way for alignment with industrialized construction principles.

#### Step 3 (to be solved): Populate Generic Floorplan with Fitting Elements of Kit-of-Parts
The generic floorplan is populated with compatible elements from the Kit-of-Parts, adapting it to meet the requirements of industrialized construction. This step ensures the design remains functional while adhering to predefined modular standards.

### Available Material

1.	JSON file, lists the bill of materials of the floor plan
2.	IFC file, shows the 3D geometry
3.	PDF file, shows the raw image 
4.	PNG file, indicates room information on the floorplan (which matches the information in the JSON and GraphML)
5.	GraphML file, reads the JSON file and represents the floor plan in a graph (which could be visualized in the free and open-source application Cytoscape https://cytoscape.org/.)

The JSON file contains the following hierarchy:

- **Panels**
  - Attributes (general metadata)
  - Items (detailed specifications for each panel)
    - Panel type
    - Start and end points
    - Height and thickness
    - Associated room and apartment
- **Spaces**
  - Room type
  - Apartment information
  - Coordinates defining the space boundaries

This structured data enables efficient processing and analysis of floorplans, forming the foundation for subsequent steps in the workflow.

## Solution

The solution leverages a collection of Python tools and algorithms to enable the transition from arbitrary designs to industrialized, modular construction systems. The key components are:
  - Graph Representation & Analysis:
    - Graph Creation: Tools parse JSON data to generate graphs (GraphML) that represent spatial relationships between rooms and panels.
    - Graph Comparison: Scripts compute metrics such as graph edit distance, SimRank similarity, and netLSD signatures to compare generic floorplans with a reference design.
    - Visualization: Both interactive (via PyVis) and static (using Matplotlib) visualizations are provided to analyze and validate the graphs.
  - Space Efficiency Analysis:
    - Convex Hull Ratio: Functions compute the ratio of the total area of relevant spaces (e.g., bathrooms, corridors, kitchens, bedrooms) to the area of their convex hull. This metric serves as a measure of spatial efficiency.
    - IoU Calculations: Algorithms assess the overlap between rooms and prefab parts to evaluate fit and fabricability.
  - Prefabricated Part Optimization:
    - Prefab Modeling: Classes define prefabricated parts (such as corridors, kitchens, bathrooms) with geometric and area constraints.
    - Floorplan Adaptation: An optimizer uses strategies (scaling, alignment, and translation) to modify room geometries so that prefab parts can be integrated into the design.
    - Visualization of Optimized Plans: The modified floorplans are rendered to help evaluate the success of the prefab integration.

These tools work together to allow the automated analysis and adaptation of a generic floorplan into one that meets the standards of industrialized construction. The overall goal is to enable a kit-of-parts logic that can be applied to any floorplan.

### Usage
Each script focuses on a specific aspect of the workflow. Here are some example usages:
- Graph Comparison and Visualization:
Run the graph comparison tool to visualize similarities between a generic design and the reference:

```
python compare_graphs.py /path/to/graphml_1 /path/to/graphml_2
```
The tool produces interactive HTML visualizations and static plots.

- IoU and Fabricability Checks:
To compute IoU metrics for room fitting:

```
python compute_iou.py /path/to/your/json_file.json
```
- Floorplan Optimization (Not Completed):
Optimize and visualize the integration of prefabricated parts into a floorplan:

```
python modify_plan.py
```
Ensure the JSON file paths and prefab parameters are correctly set within the script.

- Interactive Graph Visualization:

Open the provided HTML files (my_interactive_graph.html, my_interactive_graph_2.html) in your web browser to explore the spatial graphs interactively.

### Dependencies
Install dependencies via pip:
```
pip install numpy shapely networkx matplotlib pyvis netlsd descartes scikit-learn

```


### Team
- **Furio Sordini** / Implenia - Digital Design and Innovation Manager  
- **Jianpeng Cao** / HKU - Assistant Professor in the Department of Real Estate and Construction
- **Evangelos Pantazis** / ZHAW - Senior Researcher    
- **Konrad Graser** / ZHAW - Research/Program Manager  
- **Giulia Curletto** / Implenia - Digital Design and Innovation Manager

### Funding Partner
This project is supported by **Innosuisse - Swiss Innovation Agency Research Grant**: 108.408 IP-SBM.
