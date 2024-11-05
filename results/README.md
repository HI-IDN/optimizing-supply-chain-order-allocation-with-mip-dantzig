# Nomen est omen!

Here we find (visual) results of the optimization problem. To use these open the
`.htm` files in a browser. The browser should automatically find the data it needs.

## `order_allocation_flow_sankey.htm`

This is the HTML that contains the most basic result of the optimization visualizing 
how many orders are processed by each plant (plants that don't do anything are omited).
In the next layer this diagram shows how many orders from which plant are shipped via 
respective ports. 

## `order_allocation_flow_w_violations_sankey.htm`

This HTML file is like the first one but with the additional layer that differentiates 
VMI violating orders. This plot is quite laggy somehow. Why? We do not know!

## `plant_port_connections.htm`

Being the most basic, this HTML file contains only the connections between the plants 
and ports.
