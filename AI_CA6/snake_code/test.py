import numpy as np
qtable = np.load("s2_qtble.npy")
naridi = int (0)
for i in range(1 , 8192,2) :
    if(qtable[i][0]<0):
        naridi+=1

print(naridi)