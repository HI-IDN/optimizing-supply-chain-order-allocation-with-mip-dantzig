import pandas as pd
from gurobipy import Model, GRB
import gurobipy as gb


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
    


# model = Model('warehouse_problem')

# number_of_orders = len(ID_per_order)        # index i
# number_of_plants = len(cost_per_unit)         # index j
# number_of_ports = len(costs_per_port)          # index k
# number_of_days = 1

# plant_alloc = model.addVars(number_of_orders, number_of_plants, number_of_days, vtype=GRB.BINARY,name="Plant Allocation")        # number of plant j producing order i
# port_alloc = model.addVars(number_of_orders, number_of_ports, number_of_days, vtype=GRB.BINARY,name="Port Allocation")        # number of port k shipping order i
    
# def objective_function(cost_per_unit,costs_per_port,ID_quant_per_order,plant_alloc,port_alloc):
#     gb.quicksum(cost_per_unit[])
    
    
    
    
