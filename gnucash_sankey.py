#!/usr/bin/env python3

import sys
import argparse
import plotly.graph_objects as go
from plotly.offline import plot
from GnucashInterface import GnucashInterface

def process_balances(account_list,gnc_iface):
    flows_list = []
    dest_list = []
    origin_list = []
    nodeid_list = []
    for acc in account_list:
        balance = gnc_iface.get_balance(acc)
        flows_list.append(balance)
        nodeid_list.append(gnc_iface.get_account_id(acc))
        dest_list.append(gnc_iface.get_account_id(acc))
        origin_list.append(gnc_iface.get_account_id(acc.get_parent()))
    return (flows_list,origin_list,dest_list,nodeid_list)


def process_inc_exp(account_list,gnc_iface):
    flows_list = []
    dest_list = []
    origin_list = []
    nodeid_list = []
    for acc in account_list:
        flow = gnc_iface.get_flow(acc)
        flows_list.append(abs(flow))
        nodeid_list.append(gnc_iface.get_account_id(acc))
        if flow > 0 :
            dest_list.append(gnc_iface.get_account_id(acc))
            origin_list.append(gnc_iface.get_account_id(acc.get_parent()))
        else:
            origin_list.append(gnc_iface.get_account_id(acc))
            dest_list.append(gnc_iface.get_account_id(acc.get_parent()))
    return (flows_list,origin_list,dest_list,nodeid_list)

def generate_diagram(origin_list,dest_list,flows_list,names_list):
    fig = go.Figure(data=[go.Sankey(
            arrangement='snap',
            orientation='v',
            node = dict(
                pad = 10,
                thickness = 20,
                line = dict(color = "black", width = 0.5),
                label = names_list,
            ),
            link = dict(
                source = origin_list, # indices correspond to labels, eg A1, A2, A2, B1, ...
                target = dest_list,
                value = flows_list,

        ))])

    fig.update_layout(title_text="Gnucash Sankey Diagram", font_size=10)
    fig.show()
    plot(fig)

def main():
    #Parse Arguments
    parser = argparse.ArgumentParser(description='Generate Sankey Diagrams from Gnucash')
    parser.add_argument('filepath', metavar='filepath', type=str, help='gnucash file path')
    parser.add_argument('export_type', metavar='export_type',
                        choices=['expenses','income','balances'], type=str, help='export type')
    args = parser.parse_args()
    
    #instatiate the gnucash interface
    gnc_iface = GnucashInterface(args.filepath)

    try: #we use a try/except in case something goes crazy, to still close the gnucash file
        if args.export_type == "expenses":
            test = gnc_iface.get_expenses()
            (flows_list,origin_list,dest_list,nodeid_list) = process_inc_exp(test,gnc_iface)
        elif args.export_type == "income":
            test = gnc_iface.get_income()
            (flows_list,origin_list,dest_list,nodeid_list) = process_inc_exp(test,gnc_iface)
        elif args.export_type == "balances":
            test = gnc_iface.get_all_accounts(2)
            (flows_list,origin_list,dest_list,nodeid_list) = process_balances(test,gnc_iface)
    except:
        print("Unexpected error:", sys.exc_info())

    #close gnucash file, even when an error was catched through except.
    gnc_iface.close_file()

    #finally, generate the diagram wil flows, destinations, origins, etc.
    generate_diagram(origin_list,dest_list,flows_list,gnc_iface.get_account_names())

if __name__ == "__main__":
    main()
