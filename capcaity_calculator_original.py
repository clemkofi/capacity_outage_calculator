from pandas import DataFrame
import numpy
from scipy.stats import binom
import pprint
import matplotlib.pyplot as plt

# ['Akosombo GS', 'Bui GS', 'Kpong GS', 'TAPCO(T1)', 'TICo(T2)', 'TT1PP', 'TT2PP', 'KTPP' ]

# the dataframe for the various power plants
power_plants = {
    'Plants' : ['H1', 'T1', 'H2', 'T2', 'H3', 'T3'],
    'Units' : [2, 1, 4, 1, 1, 2],
    'Capacity' : [10.0, 10.0, 80.0, 20.0, 40.0, 80.0],
    'Avalability' : [0.990, 0.980, 0.985, 0.975, 0.980, 0.970],
    'Demand' :  {
        '2018' : 185.0
    },
    'Growth' : 0.1511
}

export_year = ''

# working functions
def calculate_load_loss(row):
    load_loss_capacity = row['total_capacity_in'] - power_plants['Demand'][export_year]
    return (0, abs(load_loss_capacity)) [load_loss_capacity < 0.0]

def calculate_expected_load_loss(row):
    return row['load_loss'] * row['total_probability']

def calculate_expected_load_curtailment(row):
    return float("{0:.6f}".format(row['total_probability'] * 8760))

def calculate_system_peak(years):
    use_year = 0
    use_peak = 0
    for count in range (0,years+1):
        if count == 0:
            use_year = 2018
            use_peak = power_plants['Demand'][str(use_year)]
            continue
        use_year += 1
        use_peak += float("{0:.2f}".format(power_plants['Growth']*use_peak))
        power_plants['Demand'][str(use_year)] = use_peak

# generate all the values for the years specified
# calculate_system_peak(years=7)
system_peaks = {
    'year' : [],
    'system_peak' : []
}
for year in sorted(power_plants['Demand']):
    system_peaks['year'].append(year)
    system_peaks['system_peak'].append(power_plants['Demand'][year])

# export of system peaks 
# system_peaks_df = DataFrame(system_peaks, columns = ['year', 'system_peak'])
# plot to show the data
# ax = system_peaks_df.plot('year','system_peak')
# plt.show()
# system_peaks_df.to_excel ('.\system_peaks.xlsx', index = False, header=['Year', 'System Peak (For ' + str(len(system_peaks['system_peak'])-1) + ' years) Growth = 15.11%'])

print("System Peaks Export Done!!")

dataframe = DataFrame(power_plants, columns = ['Plants', 'Units', 'Capacity', 'Avalability'])
print(dataframe)

# number of elements in the dataframe
plant_count = dataframe.count()[0]

# probabilty calculations for each plant
probability_pp = {}

for count_plants in range(0, plant_count):
    plant_units = dataframe.iloc[count_plants,1]
    plant_capacity = dataframe.iloc[count_plants,2]
    plant_aval =  dataframe.iloc[count_plants,3]
    out_units_num = 0
    
    # unit capacity values
    unit_capacity = plant_capacity/plant_units
    unit_capacity_out = 0
    one_probability = []
    
    # do calculations for one plant
    for one_plant in range(plant_units, -1, -1):
        # print(one_plant)
        probability = binom.pmf(one_plant, plant_units, plant_aval)
        prob_calc = {
            'out' : out_units_num,
            'in' : one_plant,
            'capacity' : (0, unit_capacity_out) [unit_capacity_out > 0.0],
            'prob' : probability
        }
        one_probability.append(prob_calc)
        out_units_num+=1
        unit_capacity_out+=unit_capacity

    # add calculation for plant to the list
    probability_pp[count_plants] = one_probability


print(probability_pp)

# next plant to be accessed from dataframe in loop
count_next_plant_prob = 0

calculated_probs = {
    'total_capacity_out' : [],
    'total_capacity_in' : [],
    'total_probability' : [],
    'load_loss' : [],
    'expected_load_loss' : []
}

# calculations for the combined probabilties
for count_plants_prob in range(0, plant_count):
    
    # index for the next plant
    count_next_plant_prob = count_plants_prob + 1

    if(count_next_plant_prob == plant_count):
        break

    # check to see if the first two power plants have been calculated 
    if(count_next_plant_prob >= 2):
        combined_data_capacity = []
        combined_data_probability = []
        # iterate through all the probabilities for each plant
        for combined_plants_prob in range(0, len(calculated_probs['total_probability'])):
            # print(calculated_probs['total_capacity'][combined_plants_prob], calculated_probs['total_probability'][combined_plants_prob])
            value_combined_plant_prob = calculated_probs['total_probability'][combined_plants_prob]
            combined_one_time_capacity = calculated_probs['total_capacity_out'][combined_plants_prob]

            for combined_next_plant_prob in range(0, dataframe.iloc[count_next_plant_prob,1] + 1):
                new_combined_prob = value_combined_plant_prob * probability_pp[count_next_plant_prob][combined_next_plant_prob]['prob']
                sub_total_combined_capacity = combined_one_time_capacity + probability_pp[count_next_plant_prob][combined_next_plant_prob]['capacity']

                # add them to the main dcitionary
                combined_data_capacity.append(sub_total_combined_capacity)
                combined_data_probability.append(new_combined_prob)
        
        # now push the calculated values into the calculated probabilities object
        calculated_probs['total_capacity_out'] = combined_data_capacity
        calculated_probs['total_capacity_in'] = combined_data_capacity[::-1]
        calculated_probs['total_probability'] = combined_data_probability

    else:
        # iterate through all the probabilities for each plant
        for one_plant_prob in range(0, dataframe.iloc[count_plants_prob,1] + 1):
            value_one_plant_prob = probability_pp[count_plants_prob][one_plant_prob]['prob']
            one_time_capacity = probability_pp[count_plants_prob][one_plant_prob]['capacity']

            # iterate through the probabilities for the next plant and multiply by previous plant value taken 
            # add the capacities to get the total capacity working 
            for next_plant_prob in range(0, dataframe.iloc[count_next_plant_prob,1] + 1):
                new_prob = value_one_plant_prob * probability_pp[count_next_plant_prob][next_plant_prob]['prob']
                sub_total_capacity = one_time_capacity + probability_pp[count_next_plant_prob][next_plant_prob]['capacity']

                # add them to the main dcitionary
                calculated_probs['total_capacity_out'].append(sub_total_capacity)
                calculated_probs['total_probability'].append(new_prob)

            calculated_probs['total_capacity_in'] = calculated_probs['total_capacity_out'][::-1]


# putting the results in a dataframe
output_table = DataFrame(calculated_probs, columns = ['total_capacity_out', 'total_capacity_in', 'total_probability'])

# use the aggregation function to sum the table up and remove redundant rows 
aggregation_functions = {'total_capacity_out' : 'first', 'total_capacity_in' : 'first', 'total_probability' : 'sum'}
output_table_out = output_table.groupby('total_capacity_out').aggregate(aggregation_functions).reindex(columns=output_table.columns)

# do this for every year and every system peak
for year in sorted(power_plants['Demand']):
    # get the correct year to use
    export_year = year
    
    # calculations for load loss in MW
    output_table_out['load_loss'] = output_table_out.apply(calculate_load_loss, axis=1)
    output_table_out['expected_load_loss'] = output_table_out.apply(calculate_expected_load_loss, axis=1)

    # calculations for expected load curtailment
    output_table_out['expected_load_curtailment'] = output_table_out.apply(calculate_expected_load_curtailment, axis=1) 

    # export the results to excel
    output_table_out.to_excel ('.\export_COPT_tester' + year + '.xlsx', index = False, header=['Total Capacity Out (MW)', 'Total Capacity In (MW)', 'Probability', 'Load Loss (by ' + str(power_plants['Demand'][year]) + 'MW)', 'Expected Load Loss', 'Expected Load Curtailment'])

print("Done!!!")