from pandas import DataFrame
import numpy
import scipy.stats
from scipy.stats import binom
import pprint
import matplotlib.pyplot as plt

# ['Akosombo GS', 'Bui GS', 'Kpong GS', 'TAPCO(T1)', 'TICo(T2)', 'TT1PP', 'TT2PP', 'KTPP','new unit', 'new unit 2' ]

# the dataframe for the various power plants
power_plants = {
    'Plants' : ['Akosombo GS', 'Bui GS', 'Kpong GS', 'TAPCO(T1)', 'TICo(T2)', 'TT1PP', 'TT2PP', 'KTPP', 'CENIT', 'AMERI', 'SAPP1', 'SAPP2', 'KARPOWER', 'AKSA', 'TROJAN', 'GENSER', 'CENPOWER', 'ADD'],
    'Units' : [6, 4, 4, 3, 3, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 6],
    'Capacity' : [900.0, 360.0, 140.0, 300.0, 320.0, 100.0, 70.0, 200.0, 100.0, 230.0, 180.0, 340.0, 450.0, 220.0, 39.6, 18.0, 320.0, 660.0],
    'Avalability' : [0.90, 0.85, 0.72, 0.65, 0.85, 0.88, 0.85, 0.85, 0.92, 0.90, 0.92, 0.92, 0.90, 0.90, 0.70, 0.65, 0.90, 0.70],
    'Demand' :  {
        '2018' : 2523.0
    },
    'Growth' : 0.1511
}

# # the dataframe for the various power plants ----- text book values
# power_plants = {
#     'Plants' : ['H1', 'H2'],
#     'Units' : [6, 6],
#     'Capacity' : [30.0, 30.0],
#     'Avalability' : [0.990, 0.990],
#     'Demand' :  {
#         'use' : 185.0
#     },
#     'Growth' : 0.1511
# }

# # the dataframe for the various power plants  --- prof oteng paper
# power_plants = {
#     'Plants' : ['H1', 'T1', 'H2', 'T2', 'H3', 'T3'],
#     'Units' : [2, 1, 4, 1, 1, 2],
#     'Capacity' : [10.0, 10.0, 80.0, 20.0, 40.0, 80.0],
#     'Avalability' : [0.990, 0.980, 0.985, 0.975, 0.980, 0.970],
#     'Demand' :  {
#         'use' : 185.0
#     },
#     'Growth' : 0.1511
# }

# peak parameters
sd_value = power_plants['Demand']['2018'] * 0.03
lowest_peak = power_plants['Demand']['2018'] * 0.823


export_year = ''

# sum for keeping cumulative prob
cum_sum = 0.000
old_prob = 0.000
hour = 0
set_first = 0

# segment index for peak load
seg_index = 0
final_LOLE = 0.000

# Loss of Load Expectation

LOLE_days_year = {
    'LOLE' : [],
    'system_peak' : []
}

# working functions
def calculate_load_loss(row):
    global set_first
    # load_loss_capacity = row['total_capacity_in'] - power_plants['Demand'][export_year]
    load_loss_capacity = row['total_capacity_in'] - power_plants['Demand'][export_year]
    if load_loss_capacity < 0.000000 and set_first == 0:
        LOLE_days_year['LOLE'].append(row['Cumulative Probability'])
        set_first = 1
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
            LOLE_days_year['system_peak'].append(use_peak)
            continue
        use_year += 1
        # use_peak += float("{0:.2f}".format(power_plants['Growth']*use_peak))
        use_peak += 50.0
        power_plants['Demand'][str(use_year)] = use_peak
        LOLE_days_year['system_peak'].append(use_peak)

def calculate_cumulative_prob(row):
    global cum_sum
    global old_prob
    if row.name == 0:
        old_prob = row['total_probability']
        return cum_sum
        
    cum_sum -= old_prob
    old_prob = row['total_probability'] 
    return cum_sum

def calculate_EENS(row):
    global hour
    return hour * row['expected_load_loss']

def calculate_LOLE(row):
    global seg_index
    global final_LOLE
    if row['load_loss'] != 0 and seg_index != 0:
        expectation = row['total_probability'] * segment_values['t_value'][seg_index]
        seg_index -= 1
        final_LOLE += expectation
        return expectation
    
    return ("-")

# generate all the values for the years specified
calculate_system_peak(years=30)
system_peaks = {
    'year' : [],
    'system_peak' : []
}
for year in sorted(power_plants['Demand']):
    system_peaks['year'].append(year)
    system_peaks['system_peak'].append(power_plants['Demand'][year])


# print("System Peaks Export Done!!")

dataframe = DataFrame(power_plants, columns = ['Plants', 'Units', 'Capacity', 'Avalability'])

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


# print(probability_pp)

# next plant to be accessed from dataframe in loop
count_next_plant_prob = 0

calculated_probs = {
    'total_capacity_out' : [],
    'total_capacity_in' : [],
    'total_probability' : []
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

# get sum of propability 
cum_sum = output_table_out['total_probability'].sum()
print("Probability sum is " + str(cum_sum))

# function to get to cumulative prob
output_table_out['Cumulative Probability'] = output_table_out.apply(calculate_cumulative_prob, axis=1)

plotting_values = {
    "system_peaks" : [],
    "years" : [],
    "LOLE" : [] 
}

# # do this for every year and every system peak
for year in sorted(power_plants['Demand']):
    global set_first
    set_first = 0

    # get the correct year to use
    export_year = year

    # generate load values using the sd value
    load_values = {
        'sd_mean' : [],
        'load_level' : [],
        'probability' : []
    }

    for sd_mean in range(-3, 4, 1):
        load_values['sd_mean'].append(sd_mean)
        load_values['load_level'].append(((power_plants['Demand'][export_year] - (abs(sd_mean) * sd_value)) , (power_plants['Demand'][export_year] + (sd_mean * sd_value)))[sd_mean >= 0])
        load_values['probability'].append((scipy.stats.norm(0, 1).cdf(sd_mean + 0.5))-(scipy.stats.norm(0, 1).cdf(sd_mean - 0.5)))

    # save values for standard deviation distribution
    dataframe = DataFrame(load_values, columns = ['sd_mean', 'load_level', 'probability'])
    header_load = ['SD from mean', 'Load Level', 'Probability']
    dataframe.to_excel ('.\std_deviation_dist'+ str(year)+ '.xlsx', index = False, header=header_load)

    # calculate the time for the various peaks
    t_values = {
        "value_num" : [],
        "value" : [],
        "load_level" : []
    }

    for peak in range(0, len(load_values['load_level'])):
        x = (load_values['load_level'][peak - 1], lowest_peak)[peak == 0]
        print("x : ", x, " peak: ",  load_values['load_level'][peak])
        t = (10.0/7.0)*(1 - (x/load_values['load_level'][peak]))
        print("t : ", t)

        # now calculate the probability
        t_values['value_num'].append('t' + str(peak+1))
        t_values['value'].append(t * load_values['probability'][peak])
        t_values['load_level'].append(load_values['load_level'][peak])

    t_frame = DataFrame(t_values, columns = ['value_num', 'value', 'load_level'])
    header_time_units = ['T', 'T value', 'Load Level']
    t_frame.to_excel ('.\Time_unit_for_outage'+ str(year)+ '.xlsx', index = False, header=header_time_units)

    # getting segement values 
    segment_values = {
        'segment_num' : [],
        't_value' : [],
        'lower_bound' : [],
        'upper_bound' : []
    }

    for seg in range(0, len(t_values['value_num'])+1):
        if seg == 0:
            segment_values['segment_num'].append("Segment " +  str(seg+1))
            segment_values['t_value'].append(1.0)
            segment_values['upper_bound'].append(lowest_peak)
            segment_values['lower_bound'].append(0)
            continue

        t = 0
        for t_val in range(seg, len(t_values['value_num'])+1):
            t += t_values['value'][t_val-1]
        segment_values['segment_num'].append("Segment " + str(seg+1))
        segment_values['t_value'].append(t)
        segment_values['upper_bound'].append(t_values['load_level'][seg-1])
        segment_values['lower_bound'].append((t_values['load_level'][seg-2],lowest_peak)[seg == 1])

        if t_values['load_level'][seg-2] == power_plants['Demand'][export_year]:
            seg_index = seg

    # print(segment_values)

    seg_frame = DataFrame(segment_values, columns = ['segment_num', 't_value', 'lower_bound','upper_bound'])
    header_segment = ['Segment', 'T value', 'Lower Bound', 'Upper Bound']
    seg_frame.to_excel ('.\Segment_values'+ str(year)+ '.xlsx', index = False, header=header_segment)
    
    # calculations for load loss in MW
    output_table_out['load_loss'] = output_table_out.apply(calculate_load_loss, axis=1)
    output_table_out['LOLE'] = output_table_out.apply(calculate_LOLE, axis=1)
    output_table_out['expected_load_loss'] = output_table_out.apply(calculate_expected_load_loss, axis=1)

    print("Sum for expected_load_loss is ", output_table_out['expected_load_loss'].sum())

    LOLE_days_year_final = "LOLE = " + str((float("{0:.6f}".format(final_LOLE * 365.0)))) + " days/year"
    LOLE_months_year_final = "LOLE = " + str((float("{0:.6f}".format(final_LOLE * 12.0)))) + " months/year"
    LOLE_hours_year_final = "LOLE = " + str((float("{0:.6f}".format(final_LOLE * 8760.0)))) + " hours/year"

    # appending values to plot
    plotting_values['system_peaks'].append(power_plants['Demand'][year])
    plotting_values['years'].append(year)
    plotting_values['LOLE'].append(float("{0:.6f}".format(final_LOLE * 365.0)))


    output_table_out = output_table_out.append({'LOLE': LOLE_days_year_final}, ignore_index=True)
    output_table_out = output_table_out.append({'LOLE': LOLE_months_year_final}, ignore_index=True)
    output_table_out = output_table_out.append({'LOLE': LOLE_hours_year_final}, ignore_index=True)

    # header array
    header=['Total Capacity Out (MW)', 'Total Capacity In (MW)', 'Probability', 'Cumulative Probability', 'Load Loss (by ' + str(power_plants['Demand'][year]) + 'MW)', 'LOLE', 'Expected Load Loss']

    # # calculations for expected load curtailment
    # for i in range(2,9,2):
    #     hour = i
    #     output_table_out['Hr' + str(i)] = output_table_out.apply(calculate_EENS, axis=1)
    #     print("Sum for Hour " + str(i) + " "+ str(year) + " is ", output_table_out['Hr' + str(i)].sum())
    #     header.append('Hr' + str(i))

    # export the results to excel
    # output_table_out.to_excel ('.\export_COPT_' + str(power_plants['Demand'][year]) + '.xlsx', index = False, header=header)
    # output_table_out.to_excel ('.\export_COPT_tester' + year + '.xlsx', index = False, header=header)

print("2523.0", plotting_values)

# export of system peaks 
# system_sensitivity = DataFrame(LOLE_days_year, columns = ['LOLE', 'system_peak'])
# # plot to show the data
# ax1 = system_sensitivity.plot('system_peak','LOLE')
# plt.show()

print("Done!!!")