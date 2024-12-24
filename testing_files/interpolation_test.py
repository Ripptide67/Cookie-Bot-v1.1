import matplotlib.pyplot as plt
import math

"""
GOAL: Take points along a contour and find the minimum number of lines needed
INPUT: A 2D list of contour points (in pixels)
OUTPUT: A 2D list of points of lines (in pixels)
"""
# INPUT
    
# contour_list = [[2, 1], [3, 1], [4, 1], [5, 2], [6, 3], [7, 4], [8, 4], [8, 5]]
contour_list = []
r = 100
for theta in range(360):
    x = math.sin(math.radians(theta))*r
    y = math.cos(math.radians(theta))*r
    contour_list.append([x, y])

tolerance = 0.3
# OUTPUT
contour_trace = []

# Function(s)
def interpolate(x1, y1, x2, y2, x):
    if abs(x2-x1) <= 0.00001:
        y = y1
    else:
        y = y1 + (x-x1)*((y2-y1)/(x2-x1)) # interpolate
    return y

# x0: x-coord of initial line point 
# y0: y-coord of initial line point
xi, yi = contour_list[0][0], contour_list[0][1]
contour_trace.append([xi, yi])
# Go through all the points starting with x1, y1
for i in range(len(contour_list)-2):
    xi2, yi2 = contour_list[i+2][0], contour_list[i+2][1]
    xi1, yi1 = contour_list[i+1][0], contour_list[i+1][1]
    yi1_pred = interpolate(xi, yi, xi2, yi2, xi1)
    if abs(yi1-yi1_pred) >= tolerance:
        contour_trace.append([xi1, yi1])
        xi, yi = xi1, yi1
    
    if i == len(contour_list)-3:
        contour_trace.append([xi2, yi2])

# Print results
ni_lines = len(contour_list)-1
nf_lines = len(contour_trace)-1
percent_diff = abs(ni_lines-nf_lines)/((ni_lines+nf_lines)/2) * 100
print("---------Reults---------")

print("Number of initial lines =", ni_lines )
print("Number of final lines =", nf_lines)
print("Efficiency Increase = %.2f%%" % percent_diff)


# Plot the results
contour_list_x = [contour_list[i][0] for i in range(len(contour_list))]
contour_list_y = [contour_list[i][1] for i in range(len(contour_list))]
contour_trace_x = [contour_trace[i][0] for i in range(len(contour_trace))]
contour_trace_y = [contour_trace[i][1] for i in range(len(contour_trace))]
plt.plot(contour_list_x, contour_list_y, 'g^', contour_trace_x, contour_trace_y, 'r--')
plt.ylabel('y')
plt.xlabel('x')
plt.title("Plot of contour data points")
plt.show()


