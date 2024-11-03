import pandas as pd


# OrderList = pd.read_excel("Supply chain logisitcs problem.xlsx", "OrderList")
# FreightRates = pd.read_excel("Supply chain logisitcs problem.xlsx", "FreightRates")
# WhCosts = pd.read_excel("Supply chain logisitcs problem.xlsx", "WhCosts")
# WhCapacities = pd.read_excel("Supply chain logisitcs problem.xlsx", "WhCapacities")
# ProductsPerPlant = pd.read_excel("Supply chain logisitcs problem.xlsx", "ProductsPerPlant")
# VmiCustomers = pd.read_excel("Supply chain logisitcs problem.xlsx", "VmiCustomers")
# PlantPorts = pd.read_excel("Supply chain logisitcs problem.xlsx", "PlantPorts")

file_path = "Supply chain logisitcs problem.xlsx"


####CPU################################################################################################
cpu = pd.read_excel(file_path, sheet_name='WhCosts', usecols=['WH', 'Cost/unit'])
cpu.columns = ['Plant', 'UnitCost']  # Rename columns for easier reference
cpu = cpu.sort_values(by='Plant').reset_index(drop=True)
cpu['Plant'] = cpu['Plant'].replace({'PLANT': ''}, regex=True).astype(int)
print(cpu)


####NoI################################################################################################
noi = pd.read_excel(file_path, sheet_name='OrderList', usecols=['Order ID', 'Unit quantity'])
print(noi)


####WoO################################################################################################
woo = pd.read_excel(file_path, sheet_name='OrderList', usecols=['Weight'])
print(woo)


####OPID###############################################################################################
opid = pd.read_excel(file_path, sheet_name='OrderList', usecols=['Order ID'])
print(opid)


####PPID###############################################################################################
ppid = pd.read_excel(file_path, sheet_name='ProductsPerPlant', usecols=['Plant Code', 'Product ID'])
ppid = ppid.groupby('Plant Code')['Product ID'].apply(list).reset_index()
ppid = ppid[ppid['Plant Code'] != 'CND9']
ppid.reset_index(drop=True, inplace=True)
ppid.columns = ['Plant', 'ProductID']  # Rename columns for easier reference
ppid = ppid.sort_values(by='Plant').reset_index(drop=True)
ppid['Plant'] = ppid['Plant'].replace({'PLANT': ''}, regex=True).astype(int)
print(ppid)


####C##################################################################################################
c = pd.read_excel(file_path, sheet_name='OrderList', usecols=['Customer'])
print(c)


####VMI################################################################################################
vmi = pd.read_excel(file_path, sheet_name='VmiCustomers', usecols=['Plant Code', 'Customers'])

# create a list of plants from PLANT01 to PLANT19
plant_list = [f'PLANT{i:02}' for i in range(1, 20)]
# creat a DataFrame with all Plants and an empty 'Customers' collumn
all_plants = pd.DataFrame({'Plant Code': plant_list})

vmi = vmi.groupby('Plant Code')['Customers'].apply(list).reset_index()

#merge list from excel with list for all plants
vmi = all_plants.merge(vmi, on='Plant Code', how='left')

vmi.columns = ['Plant', 'Customers']  # Rename columns for easier reference
vmi = vmi.sort_values(by='Plant').reset_index(drop=True)
vmi['Plant'] = vmi['Plant'].replace({'PLANT': ''}, regex=True).astype(int)
print(vmi)


####DC#################################################################################################
dc = pd.read_excel(file_path, sheet_name='WhCapacities', usecols=['Plant ID', 'Daily Capacity '])
dc.columns = ['Plant', 'Daily Capacity']  # Rename columns for easier reference
dc = dc.sort_values(by='Plant').reset_index(drop=True)
dc['Plant'] = dc['Plant'].replace({'PLANT': ''}, regex=True).astype(int)
print(dc)


####CP#################################################################################################
cp = pd.read_excel(file_path, sheet_name='PlantPorts', usecols=['Plant Code', 'Port'])
cp.columns = ['Plant', 'Port']  # Rename columns for easier reference
cp = cp.groupby('Plant')['Port'].apply(list).reset_index()

# Rename PORT01, PORT02, etc. to 1, 2, etc.
unique_ports = cp['Port'].explode().unique()
port_mapping = {port: str(i + 1) for i, port in enumerate(unique_ports)}
cp['Port'] = cp['Port'].apply(lambda ports: [port_mapping[port] for port in ports])

cp = cp.sort_values(by='Plant').reset_index(drop=True)
cp['Plant'] = cp['Plant'].replace({'PLANT': ''}, regex=True).astype(int)
print(cp)

####cpw################################################################################################
cpw = pd.read_excel(file_path, sheet_name='FreightRates', usecols=['orig_port_cd', 'minimum cost', 'rate'])
cpw.columns = ['Port', 'Fixed cost', 'Variable cost']  # Rename columns for easier reference
# Convert 'Fixed cost' and 'Variable cost' to float
cpw['Fixed cost'] = cpw['Fixed cost'].replace({'\$': '', ',': '.'}, regex=True).astype(float)
cpw['Variable cost'] = cpw['Variable cost'].replace({'\$': '', ',': '.'}, regex=True).astype(float)

cpw = cpw.groupby('Port').agg({'Fixed cost': 'mean', 'Variable cost': 'mean'}).reset_index()
cpw = cpw.sort_values(by='Port').reset_index(drop=True)
cpw['Port'] = cpw['Port'].replace({'PORT': ''}, regex=True).astype(int)
print(cpw)









