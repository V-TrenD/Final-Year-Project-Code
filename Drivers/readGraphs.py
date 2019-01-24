import math

from matplotlib import pyplot as plt
from scipy import stats


print "READ SPEED TEST Data"
#savefile = file("ReadIntX-39kpbs", 'r')  # Card Read Speed
#savefil2 = file("ReadIntX-38kpbs", 'r')  # Card Read Speed
#savefile = file("ReadCardX-200kpbs", 'r')  # Card Read Speed
#savefil2 = file("ReadCardX-171kpbs", 'r')  # Card Read Speed
#savefile = file("ReadData-2902kpbs", 'r') # Card Write Speed
#savefile = file("ReadInt-4014kpbs", 'r') # Interface read speed
#savefile = file("ReadCardX-217kpbs", 'r')
#savefil2 = file("ReadCardX-201kpbs", 'r')
savefile = file("TransactionTime0", 'r')
times = eval(savefile.readline())
times = times[1:]
print times
savefile.close()

total = 0
bitR = []
byteR = []
bitR2 = []
for t in times:
    datarate = 1.0/(t/((3+1)*256))
    if datarate > 90000:
        datarate *= 0.45
    print datarate, datarate*10
    bitR += [datarate*7]
    byteR += [t*1000]
    total += datarate*8

mean = sum(byteR)/len(byteR)    

#plt.plot(bitR, '-')
plt.plot([0,99], [mean, mean], 'g-')
plt.plot(byteR, 'o', color='r')

# times2 = eval(savefil2.readline())
# savefil2.close()
# for t in times2:
#     datarate = 1.0/(t/((3+1)*256))
#     if datarate > 90000:
#         datarate *= 0.45
#     print datarate, datarate*8
#     bitR2 += [datarate*7]
#  
# mean2 = sum(bitR2)/len(bitR2)
# plt.plot([0,99], [mean2, mean2], 'b--')
# plt.plot(bitR2, '*', color='k')

#plt.title(r"Card Write Speed, AVG1=%dkbps, AVG2=%dkbps"%((mean/1000),(mean2/1000)))

plt.title(r"Transaction Speed, AVG1=%fms"%((mean)))
plt.xlabel("Sample")
plt.ylabel("Time (ms)")
#plt.ylim([0, 7e5])
plt.show()

#savefile.write(str(times))
#for d in data:
#    savefile.write(d)
#savefile.flush()
#savefile.close()