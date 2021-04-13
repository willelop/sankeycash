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
        print(acc.get_full_name() + ": " + str(flow))
        flows_list.append(abs(flow))
        nodeid_list.append(gnc_iface.get_account_id(acc))
        if flow > 0 :
            dest_list.append(gnc_iface.get_account_id(acc))
            origin_list.append(gnc_iface.get_account_id(acc.get_parent()))
        else:
            origin_list.append(gnc_iface.get_account_id(acc))
            dest_list.append(gnc_iface.get_account_id(acc.get_parent()))
    return (flows_list, origin_list, dest_list, nodeid_list)


def generate_diagram(origin_list, dest_list, flows_list, names_list, args, gnc_iface):
    fig = go.Figure(data=[go.Sankey(
            arrangement='snap',
            orientation=args.diag_orientation,
            node=dict(
                pad=10,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=names_list,
            ),
            link=dict(
                source=origin_list,# indices correspond to labels, eg A1, A2, A2, B1, ...
                target=dest_list,
                value=flows_list,
        ))])

    title_str = "Gnucash Sankey Diagram " + "[" + args.export_type + "] "
    title_str = title_str + gnc_iface.get_period_string()
    fig.update_layout(title_text=title_str, font_size=10)
    fig.show()
    plot(fig)


def main():
    #Parse Arguments
    parser = argparse.ArgumentParser(description='Generate Sankey Diagrams from Gnucash')
    parser.add_argument('filepath', metavar='filepath', type=str, help='gnucash file path')
    parser.add_argument('export_type', metavar='export_type',
                        choices=['expenses','income','balances'], type=str, help='export type')
    parser.add_argument('--depth', dest='depth_val', type=int, default=1000,
                    help='account tree depth')
    parser.add_argument('--orient', dest='diag_orientation', type=str, default='h',
                    choices=['h','v'],
                    help='diagram oritentation')
    parser.add_argument('--account', dest='balance_account', type=str, default='Assets',
                    help='account to diplay balance')
    parser.add_argument('--equityacc', dest='equity_account', type=str, default='Equity',
                    help='equity account name')
    parser.add_argument('--incomeacc', dest='income_account', type=str, default='Income',
                    help='income account name')
    parser.add_argument('--expenseacc', dest='expense_account', type=str, default='Expenses',
                    help='income account name')
    parser.add_argument('--period', dest='assess_period', type=str, default='month',
                    help='time period of assessment')
    parser.add_argument('--date', dest='assess_datetime', type=str, default='current',
                    help='assessment time, in the format dd.mm.yyyy')
    args = parser.parse_args()
    # instatiate the gnucash interface
    gnc_iface = GnucashInterface(args.filepath,
                                 args.income_account, args.expense_account, args.equity_account)

    gnc_iface.set_assessment_datetime(args.assess_datetime)
    gnc_iface.set_assessment_period(args.assess_period)

    try: # we use a try/except in case something goes crazy, to still close the gnucash file
        if args.export_type == "expenses":
            test = gnc_iface.get_expenses(args.depth_val)
            (flows_list, origin_list, dest_list, nodeid_list) = process_inc_exp(test, gnc_iface)

        elif args.export_type == "income":
            test = gnc_iface.get_income(args.depth_val)
            (flows_list, origin_list, dest_list, nodeid_list) = process_inc_exp(test, gnc_iface)

        elif args.export_type == "balances":
            test = gnc_iface.get_all_accounts(args.balance_account, args.depth_val)
            (flows_list, origin_list, dest_list, nodeid_list) = process_balances(test, gnc_iface)

        if len(test) > 0:
            # finally, generate the diagram wil flows, destinations, origins, etc.
            generate_diagram(origin_list, dest_list, flows_list, gnc_iface.get_account_names(True), args, gnc_iface)
        else:
            print('Couldn\'t find any accounts')
    except:
        print("Unexpected error:", sys.exc_info())

    # close gnucash file, even when an error was catched through except.
    gnc_iface.close_file()


if __name__ == "__main__":
    main()
