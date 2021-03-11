#!/usr/bin/env python3

import sys
import argparse
import plotly.graph_objects as go
from plotly.offline import plot
from SankeyAccount import SankeyAccount

def process_balances(account_list,sankey_iface):
    flows_list = []
    dest_list = []
    origin_list = []
    nodeid_list = []
    for acc in account_list:
        balance = sankey_iface.get_balance(acc)
        flows_list.append(balance)
        nodeid_list.append(sankey_iface.get_account_id(acc))
        dest_list.append(sankey_iface.get_account_id(acc))
        origin_list.append(sankey_iface.get_account_id(acc.get_parent()))
    return (flows_list,origin_list,dest_list,nodeid_list)


def process_inc_exp(account_list,sankey_iface):
    flows_list = []
    dest_list = []
    origin_list = []
    nodeid_list = []
    for acc in account_list:
        flow = sankey_iface.get_flow(acc)
        flows_list.append(abs(flow))
        nodeid_list.append(sankey_iface.get_account_id(acc))
        if flow > 0 :
            dest_list.append(sankey_iface.get_account_id(acc))
            origin_list.append(sankey_iface.get_account_id(acc.get_parent()))
        else:
            origin_list.append(sankey_iface.get_account_id(acc))
            dest_list.append(sankey_iface.get_account_id(acc.get_parent()))
    return (flows_list,origin_list,dest_list,nodeid_list)

def main():
    parser = argparse.ArgumentParser(description='Generate Sankey Diagrams from Gnucash')
    parser.add_argument('filepath', metavar='filepath', type=str, help='gnucash file path')
    parser.add_argument('export_type', metavar='export_type',
                        choices=['expenses','income','balances'], type=str, help='export type')

    args = parser.parse_args()

    sankeyAcc = SankeyAccount(args.filepath)

    try:
        if args.export_type == "expenses":
            test = sankeyAcc.get_expenses()
            (flows_list,origin_list,dest_list,nodeid_list) = process_inc_exp(test,sankeyAcc)
        elif args.export_type == "income":
            test = sankeyAcc.get_income()
            (flows_list,origin_list,dest_list,nodeid_list) = process_inc_exp(test,sankeyAcc)
        elif args.export_type == "balances":
            test = sankeyAcc.get_all_accounts(2)
            (flows_list,origin_list,dest_list,nodeid_list) = process_balances(test,sankeyAcc)

    except:
        print("Unexpected error:", sys.exc_info())

    sankeyAcc.close_file()

    fig = go.Figure(data=[go.Sankey(
            arrangement='snap',
            node = dict(
                pad = 10,
                thickness = 20,
                line = dict(color = "black", width = 0.5),
                label = sankeyAcc.get_account_names(),
            ),
            link = dict(
                source = origin_list, # indices correspond to labels, eg A1, A2, A2, B1, ...
                target = dest_list,
                value = flows_list,

        ))])

    fig.update_layout(title_text="Income/Expenses Flow", font_size=10)
    fig.show()
    plot(fig)

if __name__ == "__main__":
    main()
