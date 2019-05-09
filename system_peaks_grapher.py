import numpy
import matplotlib.pyplot as plt
import scipy.stats

peaks = sorted([2306.0,2523.0])[::-1]

months = [mon for mon in range(0,2,1)]

peak_text = []

print(peaks)
print(months)

sd_value = peaks[0] * 0.03
lowest_peak = 0.00
# lowest_peak = power_plants['Demand']['use'] * 0.3

# generate load values using the sd value
load_values = {
    "sd_mean" : [],
    "load_level_upper" : [],
    "load_level_lower" : [],
    "probability" : []    
}

for sd_mean in range(-3, 4, 1):
        load_values['sd_mean'].append(sd_mean)
        upper_level = ((peaks[0] - (abs(sd_mean) * sd_value)) , (peaks[0] + (sd_mean * sd_value)))[sd_mean >= 0]
        load_values['load_level_upper'].append(upper_level)
        peak_text.append(str(upper_level) + " MW")
        load_values['load_level_lower'].append(((peaks[1] - (abs(sd_mean) * sd_value)) , (peaks[1] + (sd_mean * sd_value)))[sd_mean >= 0])
        load_values['probability'].append((scipy.stats.norm(0, 1).cdf(sd_mean + 0.5))-(scipy.stats.norm(0, 1).cdf(sd_mean - 0.5)))

lowest_peak = load_values['load_level_lower'][0]

# calculate the time for the various peaks
t_values = {
    "value_num" : [],
    "value" : [],
    "load_level" : []
}

for peak in range(0, len(load_values['load_level_upper'])):
    x = (load_values['load_level_upper'][peak - 1], lowest_peak)[peak == 0]
    print("x : ", x, " peak: ",  load_values['load_level_upper'][peak])
    t = (10.0/1.0)*(1 - (x/load_values['load_level_upper'][peak]))
    print("t : ", t)

    # now calculate the probability
    t_values['value_num'].append('t' + str(peak+1))
    t_values['value'].append(t * load_values['probability'][peak])
    t_values['load_level'].append(load_values['load_level_upper'][peak])

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

    if t_values['load_level'][seg-2] == peaks[0]:
        seg_index = seg

# # save values for standard deviation distribution
# dataframe = DataFrame(load_values, columns = ['sd_mean', 'load_level', 'probability'])
# header_load = ['SD from mean', 'Load Level', 'Probability']
# dataframe.to_excel ('.\std_deviation_dist.xlsx', index = False, header=header_load)

# plt.plot(months, peaks, months, [peaks[1],peaks[1]], '--r', [months[1], months[1]], [peaks[1],(peaks[1]/1.1)], '--r')
# plt.plot(months, peaks)

# plot for the various load level
# for val in range(0, len(load_values['load_level_upper'])):
#     plt.plot(months, [load_values['load_level_upper'][val], load_values['load_level_lower'][val]])

print(segment_values['t_value'])
print(segment_values['upper_bound'])
print(lowest_peak)
# plot for the modified load-duration curve
plt.plot(segment_values['t_value'], segment_values['upper_bound'])

# dotted line segment_values['load_level_lower']
# plt.plot(months, [sorted(load_values['load_level_lower'])[0],sorted(load_values['load_level_lower'])[0]], '--r', [months[1], months[1]], [(sorted(load_values['load_level_upper'])[::-1])[0],(sorted(load_values['load_level_lower'])[0]/2.0)], 'black') 
plt.plot(months, [lowest_peak, lowest_peak], '--r', [months[1], months[1]], [(sorted(load_values['load_level_upper'])[::-1])[0],(lowest_peak/2.0)], 'black') 

# plt.title("Conditional Load Duration Curve")
plt.title("Modified Load Duration Curve")
plt.xlabel("Time (t)")
plt.ylabel("Peak Load (MW)")
# plt.legend(peak_text, loc='lower left')
plt.show()

