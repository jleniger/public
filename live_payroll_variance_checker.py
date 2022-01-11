# -*- coding: utf-8 -*-
"""
Created on Wed Oct 27 15:37:26 2021

@author: jeffl
"""

import pandas as pd
import paycode_lists

def setup():
    """import payroll file csv to be analyzed and create a pandas dataframe (df) with the data"""
    csv_path = 'Pre Process Register Data Export (Jan 5).csv'
    global df
    df = pd.read_csv(csv_path).set_index('Check/Voucher', drop = False) 
    df = df.fillna(0)

def calc_subtotals(output_list_name, paycode_list):
    """adds a new subtotal(new df column) for each grouping of codes needed 
    (for example, ft_earnings) that is not available in the raw data of the export"""
    subtotal = 0
    for code in paycode_list:
        if code in df.keys():
            subtotal +=df[code]
    df[output_list_name] = subtotal

def run_subtotals_by_list_name():
    """uses dictionary in paycode_lists to assign name (i.e. 'ft_earnings') and list (list of ft_earnings codes) 
    passed to calc_subtotals function in running subtotals"""
    for output_list_name, paycode_list in paycode_lists.paycode_list_dictionary.items():
        calc_subtotals(output_list_name, paycode_list)    

def run_recalculations():
    """recalculates expected paycheck amounts for FICA taxes withheld and 401EE/ER contributions"""
    for check_no, paycode in df.iterrows():
        #FT employees
        if paycode['ft_earnings'] > 0:
            ft_taxable = paycode['ft_earnings'] - paycode['cafeteria_exclusions']
            pt_taxable = 0
        else:
        #30HR benefitted (PT) employees
            if paycode['cafeteria_exclusions'] > 0:
                ft_taxable = 0
                pt_taxable = paycode['pt_earnings'] - paycode['cafeteria_exclusions']
            #PT employees
            else:
                ft_taxable = 0
                pt_taxable = paycode['pt_earnings']
        df.loc[check_no, 'medicare_recalc'] = (ft_taxable + pt_taxable) * .0145
        df.loc[check_no, 'social_security_recalc'] = pt_taxable * .062
        df.loc[check_no, 'ft_401ee_recalc'] = paycode['ft_401_earnings'] * .04
        df.loc[check_no, 'ft_401er_recalc'] = paycode['ft_401_earnings'] * .12
        
def run_variance_checks():
    """calculates variances between results of run_recalculations function and actual amount on the paycheck"""
    for check_no, paycode in df.iterrows():    
        df.loc[check_no, 'medicare_variance'] = paycode['medicare_recalc'] - paycode['T-MED']
        df.loc[check_no, 'social_security_variance'] = paycode['social_security_recalc'] - paycode['T-SS']
        df.loc[check_no, 'ft_401ee_variance'] = paycode['ft_401ee_recalc'] - paycode['D-401A'] - paycode['D-401ED']
        df.loc[check_no, 'ft_401er_variance'] = paycode['ft_401er_recalc'] - paycode['E-401ERAmount']
         
def display_material_variances(variance_list):
    """displays a df display of all checks with materially significant variances for variance_list, for follow up and correction
    uses 4 cents as the material error threshhold on a single check; also sums each variance for a quick double-check"""
    for variance in variance_list:
        display(df[(df[variance] <= -0.04) | (df[variance] >= 0.04)])
        print(variance, df[variance].sum())

if __name__ == "__main__":
      setup()
      run_subtotals_by_list_name()
      run_recalculations()
      run_variance_checks()
      display_material_variances(paycode_lists.variance_list)
      #print(df)


        