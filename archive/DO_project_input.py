import pandas as pd
from gurobipy import Model, GRB
import gurobipy as gb
import numpy as np
import plotly.io as pio
import plotly.graph_objects as go
from collections import Counter
pio.renderers.default = 'browser'

def input_data():
    file_path = "Supply chain logisitcs problem.xlsx"
    
    
    ####cost_per_unit################################################################################################
    cost_per_unit = pd.read_excel(file_path, sheet_name='WhCosts', usecols=['WH', 'Cost/unit'])
    cost_per_unit.columns = ['Plant', 'UnitCost']  # Rename columns for easier reference
    cost_per_unit = cost_per_unit.sort_values(by='Plant').reset_index(drop=True)
    cost_per_unit['Plant'] = cost_per_unit['Plant'].replace({'PLANT': ''}, regex=True).astype(int)
    cost_per_unit = cost_per_unit[cost_per_unit['Plant'] != 19]
    #print(cost_per_unit)
    
    
    ####ID_quant_per_order################################################################################################
    ID_quant_per_order = pd.read_excel(file_path, sheet_name='OrderList', usecols=['Order ID', 'Unit quantity'])
    #print(ID_quant_per_order)
    
    
    ####weight_per_order################################################################################################
    weight_per_order = pd.read_excel(file_path, sheet_name='OrderList', usecols=['Weight'])
    #print(weight_per_order)
    
    
    ####ID_per_order###############################################################################################
    ID_per_order = pd.read_excel(file_path, sheet_name='OrderList', usecols=['Order ID'])
    #print(ID_per_order)
    
    
    ####product_per_order###############################################################################################
    product_per_order = pd.read_excel(file_path, sheet_name='OrderList', usecols=['Product ID'])
    #print(product_per_order)
    
    
    ####plant_product_capabilities###############################################################################################
    plant_product_capabilities = pd.read_excel(file_path, sheet_name='ProductsPerPlant', usecols=['Plant Code', 'Product ID'])
    plant_product_capabilities = plant_product_capabilities.groupby('Plant Code')['Product ID'].apply(list).reset_index()
    plant_product_capabilities = plant_product_capabilities[plant_product_capabilities['Plant Code'] != 'CND9']
    plant_product_capabilities.reset_index(drop=True, inplace=True)
    plant_product_capabilities.columns = ['Plant', 'ProductID']  # Rename columns for easier reference
    plant_product_capabilities = plant_product_capabilities.sort_values(by='Plant').reset_index(drop=True)
    plant_product_capabilities['Plant'] = plant_product_capabilities['Plant'].replace({'PLANT': ''}, regex=True).astype(int)
    #plant_product_capabilities = plant_product_capabilities[plant_product_capabilities['Plant'] != 19]
    #print(plant_product_capabilities)
    
    
    ####C##################################################################################################
    customer_per_order = pd.read_excel(file_path, sheet_name='OrderList', usecols=['Customer'])
    #print(customer_per_order)
    
    
    ####vmi_customers_per_plant################################################################################################
    vmi_customers_per_plant = pd.read_excel(file_path, sheet_name='VmiCustomers', usecols=['Plant Code', 'Customers'])
    
    # create a list of plants from PLANT01 to PLANT19
    plant_list = [f'PLANT{i:02}' for i in range(1, 20)]
    # creat a DataFrame with all Plants and an empty 'Customers' collumn
    all_plants = pd.DataFrame({'Plant Code': plant_list})
    
    vmi_customers_per_plant = vmi_customers_per_plant.groupby('Plant Code')['Customers'].apply(list).reset_index()
    
    #merge list from excel with list for all plants
    vmi_customers_per_plant = all_plants.merge(vmi_customers_per_plant, on='Plant Code', how='left')
    
    vmi_customers_per_plant.columns = ['Plant', 'Customers']  # Rename columns for easier reference
    vmi_customers_per_plant = vmi_customers_per_plant.sort_values(by='Plant').reset_index(drop=True)
    vmi_customers_per_plant['Customers'] = vmi_customers_per_plant['Customers'].apply(lambda d: d if isinstance(d, list) else [])
    vmi_customers_per_plant['Plant'] = vmi_customers_per_plant['Plant'].replace({'PLANT': ''}, regex=True).astype(int)
    vmi_customers_per_plant = vmi_customers_per_plant[vmi_customers_per_plant['Plant'] != 19]
    #print(vmi_customers_per_plant)
    
    
    ####daily_order_capacity_per_plant#################################################################################################
    daily_order_capacity_per_plant = pd.read_excel(file_path, sheet_name='WhCapacities', usecols=['Plant ID', 'Daily Capacity '])
    daily_order_capacity_per_plant.columns = ['Plant', 'Daily Capacity']  # Rename columns for easier reference
    daily_order_capacity_per_plant = daily_order_capacity_per_plant.sort_values(by='Plant').reset_index(drop=True)
    daily_order_capacity_per_plant['Plant'] = daily_order_capacity_per_plant['Plant'].replace({'PLANT': ''}, regex=True).astype(int)
    daily_order_capacity_per_plant = daily_order_capacity_per_plant[daily_order_capacity_per_plant['Plant'] != 19]
    #print(daily_order_capacity_per_plant)
    
    
    ####ports_per_plant#################################################################################################
    ports_per_plant = pd.read_excel(file_path, sheet_name='PlantPorts', usecols=['Plant Code', 'Port'])
    ports_per_plant.columns = ['Plant', 'Port']  # Rename columns for easier reference
    ports_per_plant = ports_per_plant.groupby('Plant')['Port'].apply(list).reset_index()
    
    # Rename PORT01, PORT02, etc. to 1, 2, etc.
    unique_ports = ports_per_plant['Port'].explode().unique()
    port_mapping = {port: str(i + 1) for i, port in enumerate(unique_ports)}
    ports_per_plant['Port'] = ports_per_plant['Port'].apply(lambda ports: [port_mapping[port] for port in ports])
    
    ports_per_plant = ports_per_plant.sort_values(by='Plant').reset_index(drop=True)
    ports_per_plant['Plant'] = ports_per_plant['Plant'].replace({'PLANT': ''}, regex=True).astype(int)
    ports_per_plant['Port'] = ports_per_plant['Port'].apply(lambda x: list(map(int,x)))
    ports_per_plant = ports_per_plant[ports_per_plant['Plant'] != 19]
    
    #print(ports_per_plant)
    
    ####costs_per_port################################################################################################
    costs_per_port = pd.read_excel(file_path, sheet_name='FreightRates', usecols=['orig_port_cd', 'minimum cost', 'rate'])
    costs_per_port.columns = ['Port', 'Fixed cost', 'Variable cost']  # Rename columns for easier reference
    # Convert 'Fixed cost' and 'Variable cost' to float
    costs_per_port['Fixed cost'] = costs_per_port['Fixed cost'].replace({'\$': '', ',': '.'}, regex=True).astype(float)
    costs_per_port['Variable cost'] = costs_per_port['Variable cost'].replace({'\$': '', ',': '.'}, regex=True).astype(float)
    
    costs_per_port = costs_per_port.groupby('Port').agg({'Fixed cost': 'mean', 'Variable cost': 'mean'}).reset_index()
    costs_per_port = costs_per_port.sort_values(by='Port').reset_index(drop=True)
    costs_per_port['Port'] = costs_per_port['Port'].replace({'PORT': ''}, regex=True).astype(int)
    
    # mean value for 'Fixed cost' and 'Variable cost'
    mean_fixed_cost = costs_per_port['Fixed cost'].mean()
    mean_variable_cost = costs_per_port['Variable cost'].mean()
    
    # new row for PORT01
    new_row = {'Port': 1, 'Fixed cost': mean_fixed_cost, 'Variable cost': mean_variable_cost}
    
    # insert new row in DataFrame
    costs_per_port = pd.concat([pd.DataFrame([new_row]), costs_per_port], ignore_index=True)
    
    #print(costs_per_port)
    
    
    
    
    ####DataFrame to numpy array####
    cost_per_unit = cost_per_unit.loc[:,'UnitCost'].values
    costs_per_port = costs_per_port.loc[:,['Fixed cost', 'Variable cost']].values
    customer_per_order = customer_per_order.loc[:,'Customer'].values
    daily_order_capacity_per_plant = daily_order_capacity_per_plant.loc[:,'Daily Capacity'].values
    ID_per_order = ID_per_order.loc[:,'Order ID'].values
    ID_quant_per_order = ID_quant_per_order.loc[:,['Order ID','Unit quantity']].values
    plant_product_capabilities = plant_product_capabilities.loc[:,'ProductID'].values
    ports_per_plant = ports_per_plant.loc[:,'Port'].values
    product_per_order = product_per_order.loc[:,'Product ID'].values
    vmi_customers_per_plant = vmi_customers_per_plant.loc[:,'Customers'].values
    weight_per_order = weight_per_order.loc[:,'Weight'].values


    return cost_per_unit,product_per_order,ID_quant_per_order,weight_per_order,ID_per_order,plant_product_capabilities,customer_per_order,vmi_customers_per_plant,daily_order_capacity_per_plant,ports_per_plant,costs_per_port

cost_per_unit,product_per_order,ID_quant_per_order,weight_per_order,ID_per_order,plant_product_capabilities,customer_per_order,vmi_customers_per_plant,daily_order_capacity_per_plant,ports_per_plant,costs_per_port = input_data()
    


model = Model('warehouse_problem')

number_of_orders = len(ID_per_order)        # index_order
number_of_plants = len(cost_per_unit)         # index_plant
number_of_ports = len(costs_per_port)          # index_port
number_of_days = 1                              # index_day

plant_alloc = model.addVars(number_of_orders, number_of_plants, number_of_days, vtype=GRB.BINARY,name="Plant Allocation")        # number of plant j producing order i
port_alloc = model.addVars(number_of_orders, number_of_ports, number_of_days, vtype=GRB.BINARY,name="Port Allocation")        # number of port k shipping order i
days_needed = model.addVar(vtype = GRB.INTEGER, name='Days that are needed', lb = 0)
    
    
cost_of_production = gb.quicksum(cost_per_unit[index_plant]*ID_quant_per_order[index_order,1]*plant_alloc[index_order,index_plant,index_day]
                for index_plant in range(number_of_plants) for index_order in range(number_of_orders) for index_day in range(number_of_days))
    
cost_of_shipping = gb.quicksum((costs_per_port[index_port,0]+costs_per_port[index_port,1]*weight_per_order[index_order])*port_alloc[index_order,index_port,index_day]
                                   for index_port in range(number_of_ports) for index_order in range(number_of_orders) for index_day in range(number_of_days))
    
cost_total = cost_of_production + cost_of_shipping + 1e10*days_needed
    

model.setObjective(cost_total, GRB.MINIMIZE)



# for index_order in range(number_of_orders):
#     for index_plant in range(number_of_plants):
#         if customer_per_order[index_order] in vmi_customers_per_plant[index_plant]:
#             for index_plant_2 in range(number_of_plants):
#                 if index_plant_2 != index_plant and customer_per_order[index_order] not in vmi_customers_per_plant[index_plant_2]:
#                     model.addConstr(gb.quicksum(plant_alloc[index_order,index_plant_2,index_day] for index_day in range(number_of_days)) == 0, name=f'VMI_order_{index_order}_plant_{index_plant}')
            
for index_order in range(number_of_orders):
    for index_plant in range(number_of_plants):
        if product_per_order[index_order] not in plant_product_capabilities[index_plant]:
            for index_day in range(number_of_days):
                model.addConstr(plant_alloc[index_order,index_plant,index_day] == 0, name=f'plant_{index_plant}_incapable_producing_order_{index_order}_')

for index_order in range(number_of_orders):
    tot = 0
    for index_day in range(number_of_days):
        tot += gb.quicksum(plant_alloc[index_order, index_plant, index_day] for index_plant in range(number_of_plants))
    model.addConstr(tot==1, name=f'order_{index_order}_to_ONE_plant')

for index_order in range(number_of_orders):
    tot = 0
    for index_day in range(number_of_days):
        tot += gb.quicksum(port_alloc[index_order, index_port, index_day] for index_port in range(number_of_ports))
    model.addConstr(tot==1, name=f'order_{index_order}_to_ONE_port')

for index_plants in range(number_of_plants):
    for index_day in range(number_of_days):
        model.addConstr(gb.quicksum(plant_alloc[index_orders, index_plants, index_day] for index_orders in range(number_of_orders)) <= days_needed*daily_order_capacity_per_plant[index_plants], name=f'plant_{index_plants}_order_limit')

for index_order in range(number_of_orders):
    for index_plant in range(number_of_plants):
        for index_port in range(number_of_ports):
            if index_port not in ports_per_plant[index_plant]:
                tot = 0
                for index_day in range(number_of_days):
                    tot += plant_alloc[index_order, index_plant, index_day] + port_alloc[index_order, index_port, index_day]
                model.addConstr(tot <= 1, name=f'order_{index_order}_plant_{index_plant}_not_conn_to_port_{index_port}')


 # Solve the first model
model.optimize()
# print(model.getVarByName('\n\n\n\n\nDays that are needed'))
# model.computeIIS()
# model.write('model.ilp')  


# print("Infeasible constraints and bounds:")
# for c in model.getConstrs():
#     if c.IISConstr:
#         print(f"Constraint {c.constrName} is in the IIS")
# for v in model.getVars():
#     if v.IISLB:
#         print(f"Variable {v.varName} has an infeasible lower bound")
#     if v.IISUB:
#         print(f"Variable {v.varName} has an infeasible upper bound")



#print(model.objVal)
    
if model.status == GRB.OPTIMAL:
    allocation = []  # List to store the allocation of orders

    # Loop through each order
    for i in range(number_of_orders):
        # Check each plant for the current order
        assigned_plant = None
        for j in range(number_of_plants):
            if plant_alloc[i, j,0].x > 0.5:  # If order i is assigned to plant j
                assigned_plant = j
                break
        
        # Check each port for the current order
        assigned_port = None
        for k in range(number_of_ports):
            if port_alloc[i, k,0].x > 0.5:  # If order i is shipped through port k
                assigned_port = k
                break
        
        # Append the allocation as a tuple (order, plant, port)
        if assigned_plant is not None and assigned_port is not None:
            allocation.append((i, assigned_plant, assigned_port))

    # Print the allocation results
    #print("Order allocations (order, plant, port):", allocation)
else:
    pass
    #print("No optimal solution found. Status code:", model.status) 
    


# Sample data: replace with actual allocation results from the optimization
# Each entry is (order_id, plant_id, port_id)

# Define nodes
order_node = "All Orders"
plants = sorted(set(plant_id for _, plant_id, _ in allocation))
ports = sorted(set(port_id for _, _, port_id in allocation))

# Create a list of all node labels
node_labels = [order_node] + [f"Plant {j}" for j in plants] + [f"Port {k}" for k in ports]

# Calculate order counts for edges between levels
# First level (All Orders -> Plants)
orders_to_plants = Counter(plant_id for _, plant_id, _ in allocation)

# Second level (Plants -> Ports)
plants_to_ports = Counter((plant_id, port_id) for _, plant_id, port_id in allocation)

# Map node labels to indices for Sankey
node_indices = {label: i for i, label in enumerate(node_labels)}

# Define the Sankey diagram sources, targets, and values based on the calculations above
sources = []
targets = []
values = []

# Add edges from "All Orders" to each plant
for plant, count in orders_to_plants.items():
    sources.append(node_indices[order_node])
    targets.append(node_indices[f"Plant {plant}"])
    values.append(count)

# Add edges from each plant to each port
for (plant, port), count in plants_to_ports.items():
    sources.append(node_indices[f"Plant {plant}"])
    targets.append(node_indices[f"Port {port}"])
    values.append(count)

# Create the Sankey diagram using Plotly
fig = go.Figure(go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=node_labels,
        color="blue"
    ),
    link=dict(
        source=sources,    # indices of source nodes
        target=targets,    # indices of target nodes
        value=values,      # the flow values for each link
        color="rgba(100, 150, 250, 0.4)"
    )
))

# Set the layout and display the figure
fig.update_layout(title_text="Order Allocation Flow from Orders to Plants to Ports", font_size=12)
fig.show()



