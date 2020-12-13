Project - Interactive Stock Trading Tool

[Package requirment]
bs4, requests, json, numpy, plotly.graph_objects, datetime, time, matplotlib.pyplot, matplotlib.ticker.
Finhub API key has been hard coded

[Interaction]
Step 1: Find Stock
Run the program, wait for it to retrieve stock symbols
Input a page number. Do so until you find a stock interested in

Step 2: Check Balance statement
Press "c" to balance statement check phase
Input a symbol, e.g. "AAPL"
The program will scrap its basic financial information in the past 4 years. And calculated some important features 
automatically. Profit rate, debt rate and ROE in the past 4 years will be ploted. In command line, it will judge whether if 
this is a good stock.

Step 3: Real time data
Press "y" to get quote
Input a resolution you are interested in, D for day, W for week and M for month
Input an 8-digit date, e.g. 20200101

You can exit at anytime by input "exit"