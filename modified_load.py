import scipy.stats
import pandas as pd

system_peak_value = 185.0
sd_value = system_peak_value * 0.04
lowest_peak = system_peak_value * 0.3

load_values = {
    "sd_mean" : [],
    "load_level" : [],
    "probability" : []
}

for sd_mean in range(-3, 4, 1):
        load_values['sd_mean'].append(sd_mean)
        load_values['load_level'].append(((system_peak_value - (abs(sd_mean) * sd_value)) , (system_peak_value + (sd_mean * sd_value)))[sd_mean >= 0])
        load_values['probability'].append((scipy.stats.norm(0, 1).cdf(sd_mean + 0.5))-(scipy.stats.norm(0, 1).cdf(sd_mean - 0.5)))

# save values for standard deviation distribution
dataframe = pd.DataFrame(load_values, columns = ['sd_mean', 'load_level', 'probability'])
header_load = ['SD from mean', 'Load Level', 'Probability']
dataframe.to_excel ('.\std_deviation_dist.xlsx', index = False, header=header_load)

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


t_frame = pd.DataFrame(t_values, columns = ['value_num', 'value', 'load_level'])
header_time_units = ['T', 'T value', 'Load Level']
t_frame.to_excel ('.\Time_unit_for_outage.xlsx', index = False, header=header_time_units)

segment_values = {
    'segment_num' : [],
    't_value' : []
}

for seg in range(0, len(t_values['value_num'])+1):
    if seg == 0:
        segment_values['segment_num'].append("Segment " +  str(seg+1))
        segment_values['t_value'].append(1.0)
        continue

    t = 0
    for t_val in range(seg, len(t_values['value_num'])+1):
        t += t_values['value'][t_val-1]
    segment_values['segment_num'].append("Segment " + str(seg+1))
    segment_values['t_value'].append(t)

# print(segment_values)

seg_frame = pd.DataFrame(segment_values, columns = ['segment_num', 't_value'])
header_segment = ['Segment', 'T value']
seg_frame.to_excel ('.\Segment_values.xlsx', index = False, header=header_segment)
