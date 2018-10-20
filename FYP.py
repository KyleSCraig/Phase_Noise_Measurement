import math
import numpy
import time
from scipy import signal
import spidev
import matplotlib.pyplot as plt
from datetime import datetime
import socket
HOST = '127.0.0.1'
PORT = 65432
## note: del array deletes the name which lets Python clean it up
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz= 1000000

def ReadChannel(channel):
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3) <<8) + adc[2]
##    data = channel*100+100+30* ##temporary without ADC
    return data

#from https://stackoverflow.com/questions/25191620/creating-lowpass-filter-in-scipy-understanding-methods-and-units
def butter_lowpass(cutoff, fs, order):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order, b, a): #possibly obsolete
    b, a = butter_lowpass(cutoff, fs, order)
    y = signal.lfilter(b, a, data)
    return y

def butter_lowpass_moving(data, cutoff, fs, order, b, a, z):
##    b, a = butter_lowpass(cutoff, fs, order)
    output, z = signal.lfilter(b, a, [data], zi=z)
    #print(output)
    return output[0], z
    
order = 6
fs = 350 #needs to be tested
cutoff = 100
initial_time = time.time()

#Setup outputs
filename = str(datetime.now())
file = open(filename,"w") #creates output file
file.close()
file_directory = open("Phase detector output directory","a")
file_directory.write(filename+"\n") #writes to a file that lets Processing know which file to read
file_directory.close()
#maybe have it wrote another line here upon exit (try: finally: style) so Processing knows whether or not the last line is new or old

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST,PORT))
        s.listen()
        print('Ready')
        conn, addr = s.accept()
        with conn:
            print('Connected')
            
            #Initialise filter       
            lp_b, lp_a = butter_lowpass(cutoff, fs, order)
            zp1 = signal.lfilter_zi(lp_b,lp_a)
            zp2 = signal.lfilter_zi(lp_b,lp_a)
            zp3 = signal.lfilter_zi(lp_b,lp_a)
            zm1 = signal.lfilter_zi(lp_b,lp_a)
            zm2 = signal.lfilter_zi(lp_b,lp_a)
            zm3 = signal.lfilter_zi(lp_b,lp_a)
            p1_filtered = []
            p2_filtered = []
            p3_filtered = []
            m1_filtered = []
            m2_filtered = []
            m3_filtered = []

            ##p1 = ReadChannel(3)
            ##p2 = ReadChannel(2)
            ##p3 = ReadChannel(1)
            ##m1 = ReadChannel(7)
            ##m2 = ReadChannel(6)
            ##m3 = ReadChannel(5)
            ##p1_temp, zp1 = butter_lowpass_moving(p1, cutoff, fs, order, lp_b, lp_a, zp1)
            ##p2_temp, zp2 = butter_lowpass_moving(p2, cutoff, fs, order, lp_b, lp_a, zp2)
            ##p3_temp, zp3 = butter_lowpass_moving(p3, cutoff, fs, order, lp_b, lp_a, zp3)
            ##m1_temp, zm1 = butter_lowpass_moving(m1, cutoff, fs, order, lp_b, lp_a, zm1)
            ##m2_temp, zm2 = butter_lowpass_moving(m2, cutoff, fs, order, lp_b, lp_a, zm2)
            ##m3_temp, zm3 = butter_lowpass_moving(m3, cutoff, fs, order, lp_b, lp_a, zm3)
            ##p1_filtered.append(p1_temp)
            ##p2_filtered.append(p2_temp)
            ##p3_filtered.append(p3_temp)
            ##m1_filtered.append(m1_temp)
            ##m2_filtered.append(m2_temp)
            ##m3_filtered.append(m3_temp)

            RC = 2*math.pi/cutoff
            tr = 5*RC
            sr = int(tr*fs)
            p1_filtered = []
            p2_filtered = []
            p3_filtered = []
            t = []
            for sample in range(sr):
                p1 = ((ReadChannel(3))/1024*3300/10-3)*(180/186)
                p2 = ((ReadChannel(2))/1024*3300/10-3)*(180/186)
                p3 = ((ReadChannel(1))/1024*3300/10-3)*(180/186)
                m1 = ReadChannel(7)
                m2 = ReadChannel(6)
                m3 = ReadChannel(5)
                p1_temp, zp1 = butter_lowpass_moving(p1, cutoff, fs, order, lp_b, lp_a, zp1)
                p2_temp, zp2 = butter_lowpass_moving(p2, cutoff, fs, order, lp_b, lp_a, zp2)
                p3_temp, zp3 = butter_lowpass_moving(p3, cutoff, fs, order, lp_b, lp_a, zp3)
                m1_temp, zm1 = butter_lowpass_moving(m1, cutoff, fs, order, lp_b, lp_a, zm1)
                m2_temp, zm2 = butter_lowpass_moving(m2, cutoff, fs, order, lp_b, lp_a, zm2)
                m3_temp, zm3 = butter_lowpass_moving(m3, cutoff, fs, order, lp_b, lp_a, zm3)
##                message = str([p1_temp,p2_temp,p3_temp,m1_temp,m2_temp,m3_temp])+"\n"
##                conn.sendto(message.encode(),(HOST, PORT))
##                time.sleep(5)
                p1_filtered.append(p1_temp)
                p2_filtered.append(p2_temp)
                p3_filtered.append(p3_temp)
                t.append(round(time.time()-initial_time,3))
        ##    print(t)

            barrier = 10 #distance from 0/180 which is avoided
            buffer_len = fs*10 #vector to be calculated before writing


            p1_filtered = numpy.array(p1_filtered)
            p2_filtered = numpy.array(p2_filtered)
            p3_filtered = numpy.array(p3_filtered)

            #This section would be good I think, but is maybe too verbose as well as struggling when there is no signal change to pick up on (i.e. no phase noise)
##            test_idx = int(len(p1_filtered)*0.8) ##
##            covtest1a = p1_filtered[test_idx:-1]-numpy.mean(p1_filtered[test_idx:-1])
##            covtest1b = -p1_filtered[test_idx:-1]-numpy.mean(-p1_filtered[test_idx:-1])
##            covtest2a = p2_filtered[test_idx:-1]-numpy.mean(p2_filtered[test_idx:-1])
##            covtest2b = -p2_filtered[test_idx:-1]-numpy.mean(-p2_filtered[test_idx:-1])
##            covtest3a = p3_filtered[test_idx:-1]-numpy.mean(p3_filtered[test_idx:-1])
##            covtest3b = -p3_filtered[test_idx:-1]-numpy.mean(-p3_filtered[test_idx:-1])
            startpoints = [-1 for j in range(3)]
##            test_results = [sum((covtest1a-covtest2a)**2),sum((covtest1a-covtest2b)**2),sum((covtest1a-covtest3a)**2),sum((covtest1a-covtest3b)**2),sum((covtest2a-covtest3a)**2),sum((covtest2a-covtest3b)**2)] #calculates the sum squared error between every possible combination of signals, having removed the mean
            #print(test_results)
##            best_correlation = test_results.index(min(test_results))
            key_points = [p1_filtered[-1],p2_filtered[-1],p3_filtered[-1]]
##            if(best_correlation < 4):
##                startpoints[0] = p1_filtered[-1]
##            else:
##                startpoints[1] = p2_filtered[-1]
##            if(best_correlation == 0):
##                startpoints[1] = p2_filtered[-1]
##            elif(best_correlation == 1):
##                startpoints[1] = 360-p2_filtered[-1]
##            elif(best_correlation == 2 or best_correlation == 4):
##                startpoints[2] = p3_filtered[-1]
##            elif(best_correlation == 3 or best_correlation == 5):
##                startpoints[2] = 360-p3_filtered[-1]
        ##        print(startpoints)

            ## This is the replacement which should be just as good
            dist_from_centre = [abs(p1_filtered[-1]-90),abs(p2_filtered[-1]-90),abs(p3_filtered[-1]-90)]
            missingrow = dist_from_centre.index(max(dist_from_centre)) ##this was added later but probably all that's required
            if(missingrow==0):
                if(p1_filtered[-1]>90):
                    startpoints[1] = 360-p2_filtered[-1]
                    startpoints[2] = p3_filtered[-1]
                else:
                    startpoints[1] = p2_filtered[-1]
                    startpoints[2] = 360-p3_filtered[-1]
            elif(missingrow==1):
                if(p2_filtered[-1]>90):
                    startpoints[2] = 360-p3_filtered[-1]
                    startpoints[0] = p1_filtered[-1]
                else:
                    startpoints[2] = p3_filtered[-1]
                    startpoints[0] = 360-p1_filtered[-1]
            elif(missingrow==2):
                if(p3_filtered[-1]>90):
                    startpoints[0] = 360-p1_filtered[-1]
                    startpoints[1] = p2_filtered[-1]
                else:
                    startpoints[0] = p1_filtered[-1]
                    startpoints[1] = 360-p2_filtered[-1]


                    
            if(startpoints[0]==-1):
                missingrow = 0
            elif(startpoints[1]==-1):
                missingrow = 1
            elif(startpoints[2]==-1):
                missingrow = 2
            print(missingrow)
            if(abs(startpoints[(missingrow+1)%3]-startpoints[(missingrow+2)%3])<180): #determines the approximate ideal location of the remaining phase
                intended_position = (180+(startpoints[(missingrow+1)%3]+startpoints[(missingrow+2)%3])/2)%360
            else:
                intended_position = (startpoints[(missingrow+1)%3]+startpoints[(missingrow+2)%3])/2

            if(abs(key_points[missingrow]-intended_position)<abs(360-key_points[missingrow]-intended_position)):
                startpoints[missingrow] = key_points[missingrow]
            else:
                startpoints[missingrow] = 360-key_points[missingrow]

            if(numpy.mod((startpoints[0]-startpoints[1]),360)<180): #if they're actually all backwards    
                startpoints = 360-numpy.array(startpoints)


            #may need to be flipped if the nature of the three phase detectors is opposite to what was done in the theoretical trial        
            #NOTE THIS IS MESSY

            P1 = [startpoints[0]]
            P2 = [startpoints[1]]
            P3 = [startpoints[2]]


            while True:    #plt.close(fig=None)
                buffer_len = fs*60
                
##                print(time.time())
##                print(time.time())
                P1 = [P1[-1]]
                P2 = [P2[-1]]
                P3 = [P3[-1]]
                p1_filtered = [p1_temp]
                p2_filtered = [p2_temp]
                p3_filtered = [p3_temp]
                P1_raw = [p1_temp]
                P2_raw = [p2_temp]
                P3_raw = [p3_temp]
                M1 = [m1_temp]
                M2 = [m2_temp]
                M3 = [m3_temp]
                t = [t[-1]]


                print(buffer_len)
                for b in range(1,buffer_len):
##                    print(b)
                    p1 = ((ReadChannel(3))/1024*3300/10-3)*(180/186)
                    p2 = ((ReadChannel(2))/1024*3300/10-3)*(180/186)
                    p3 = ((ReadChannel(1))/1024*3300/10-3)*(180/186)
                    m1 = ReadChannel(7)
                    m2 = ReadChannel(6)
                    m3 = ReadChannel(5)
                    p1_temp, zp1 = butter_lowpass_moving(p1, cutoff, fs, order, lp_b, lp_a, zp1)
                    p2_temp, zp2 = butter_lowpass_moving(p2, cutoff, fs, order, lp_b, lp_a, zp2)
                    p3_temp, zp3 = butter_lowpass_moving(p3, cutoff, fs, order, lp_b, lp_a, zp3)
                    m1_temp, zm1 = butter_lowpass_moving(m1, cutoff, fs, order, lp_b, lp_a, zm1)
                    m2_temp, zm2 = butter_lowpass_moving(m2, cutoff, fs, order, lp_b, lp_a, zm2)
                    m3_temp, zm3 = butter_lowpass_moving(m3, cutoff, fs, order, lp_b, lp_a, zm3)
##                    print([p1_temp,p2_temp,p3_temp,m1_temp,m2_temp,m3_temp])
##                    if((b%10)==1):
                    
                    p1_filtered.append(p1_temp)
                    p2_filtered.append(p2_temp)
                    p3_filtered.append(p3_temp)
                    t.append(time.time()-initial_time)



                    
                    if (p1_temp<barrier):
                        deltaphase = (p2_temp-p2_filtered[b-1]-(p3_temp-p3_filtered[b-1]))/2
                    elif (p2_temp<barrier):
                        deltaphase = (p3_temp-p3_filtered[b-1]-(p1_temp-p1_filtered[b-1]))/2
                    elif (p3_temp<barrier):
                        deltaphase = (p1_temp-p1_filtered[b-1]-(p2_temp-p2_filtered[b-1]))/2
                    elif (p1_temp>180-barrier):
                        deltaphase = (p3_temp-p3_filtered[b-1]-(p2_temp-p2_filtered[b-1]))/2
                    elif (p2_temp>180-barrier):
                        deltaphase = (p1_temp-p1_filtered[b-1]-(p3_temp-p3_filtered[b-1]))/2
                    elif (p3_temp>180-barrier):
                        deltaphase = (p2_temp-p2_filtered[b-1]-(p1_temp-p1_filtered[b-1]))/2

                    else:
                        if(bool(((p1_temp<p2_temp) and (p1_temp<p3_temp)) or ((p1_temp>p2_temp) and (p1_temp>p3_temp))) ^ bool(p2_temp<p3_temp)):
                            deltaphase = (p1_temp-p1_filtered[b-1]+p2_temp-p2_filtered[b-1]+p3_temp-p3_filtered[b-1])
                        else:
                            deltaphase = -(p1_temp-p1_filtered[b-1]+p2_temp-p2_filtered[b-1]+p3_temp-p3_filtered[b-1])

                    P1.append(P1[-1]+deltaphase)
                    P2.append(P2[-1]+deltaphase)
                    P3.append(P3[-1]+deltaphase)
                    #ratio_old definitely needs a new name
                    ratio_old1 = 1-(abs(abs(p1_temp-numpy.mod(P1[b],360))-abs(p1_temp-(numpy.mod(-P1[b],360))))/360)**2
                    if(abs(p1_temp-numpy.mod(P1[b],360))<abs(p1_temp-(numpy.mod(-P1[b],360)))):
                        P1[b] = ratio_old1*P1[b]+(1-ratio_old1)*(p1_temp+360*((P1[b]+90)//360))
                    else:
                        P1[b] = ratio_old1*P1[b]+(1-ratio_old1)*(-p1_temp+360*((P1[b]+180+90)//360))
                        
                    ratio_old2 = 1-(abs(abs(p2_temp-numpy.mod(P2[b],360))-abs(p2_temp-(numpy.mod(-P2[b],360))))/360)**2
                    if(abs(p2_temp-numpy.mod(P2[b],360))<abs(p2_temp-(numpy.mod(-P2[b],360)))):
                        P2[b] = ratio_old2*P2[b]+(1-ratio_old2)*(p2_temp+360*((P2[b]+90)//360))
                    else:
                        P2[b] = ratio_old2*P2[b]+(1-ratio_old2)*(-p2_temp+360*((P2[b]+180+90)//360))
                        
                    ratio_old3 = 1-(abs(abs(p3_temp-numpy.mod(P3[b],360))-abs(p3_temp-(numpy.mod(-P3[b],360))))/360)**2
                    if(abs(p3_temp-numpy.mod(P3[b],360))<abs(p3_temp-(numpy.mod(-P3[b],360)))):
                        P3[b] = ratio_old3*P3[b]+(1-ratio_old3)*(p3_temp+360*((P3[b]+90)//360))
                    else:
                        P3[b] = ratio_old3*P3[b]+(1-ratio_old3)*(-p3_temp+360*((P3[b]+180+90)//360))

                    real_change = numpy.median(numpy.array([P1[-1]-P1[-2],P2[-1]-P2[-2],P3[-1]-P3[-2]]))
        ##            print(b, [P1[-1]-P1[-2],P2[-1]-P2[-2],P3[-1]-P3[-2]])
            ##        print(real_change)
                    P1[-1] = P1[-2] + real_change
                    P2[-1] = P2[-2] + real_change
                    P3[-1] = P3[-2] + real_change
                    M1.append(int(m1_temp))
                    M2.append(int(m2_temp))
                    M3.append(int(m3_temp))
                    P1_raw.append(int(p1_temp))
                    P2_raw.append(int(p2_temp))
                    P3_raw.append(int(p3_temp))
##                    message = str([int(20*(time.time()-initial_time)),int(p1_temp),int(p2_temp),int(p3_temp),int(m1_temp),int(m2_temp),int(m3_temp)])+"\n"
##                    message = str([int(20*(time.time()-initial_time)),int(P1[-1]),int(P2[-1]),int(P3[-1]),int(m1_temp),int(m2_temp),int(m3_temp)])+"\n"
                    message = str([int(20*(time.time()-initial_time)),int(P1[-1]*10),int(P2[-1]*10),int(P3[-1]*10),int(p1*10),int(p2*10),int(p3*10)])+"\n"
##                    message = str([int(20*(time.time()-initial_time)),int((b+240)%360),int((b+120)%360),int(b%360),int(m1_temp),int(m2_temp),int(m3_temp)])+"\n"
##                    message = str([int(100*(time.time()-initial_time)),int((P1[-1]-startpoints[0])*100),int(P2[-1]),int(P3[-1]),int(m1_temp),int(m2_temp),int(m3_temp)])+"\n"
##                    print(message)
                    conn.sendto(message.encode(),(HOST, PORT))
##                    file = open(filename,"a")
##                    file.write(str([p1_temp,p2_temp,p3_temp,m1_temp,m2_temp,m3_temp]))
##                    file.close()
                #insert writing code
####                print(time.time())
                file = open(filename,"a")
                file.write(str([t,P1_raw,P2_raw,P3_raw,M1,M2,M3])+"\n")
                file.close()
##                print(len(P1),len(t))


                
##                FreqPow = numpy.abs(numpy.fft.fft(P1[300:]))
##                FreqPow1 = numpy.abs(numpy.fft.fft(P1_raw[300:]))
##                FreqPow2 = numpy.abs(numpy.fft.fft(P2_raw[300:]))
##                FreqPow3 = numpy.abs(numpy.fft.fft(P3_raw[300:]))
##                fs2 = int((len(t)-300)/(t[-1]-t[300]))
##                print(fs)
##                freqx = numpy.fft.fftfreq(len(t)-300)*fs2
##                plt.plot(freqx[1:int(len(freqx)/2-1)],FreqPow[1:int(len(freqx)/2-1)])
##                plt.xlim(0,150)
##                plt.ylim(0,500)
##                plt.figure()
##                plt.plot(freqx[1:int(len(freqx)/2-1)],FreqPow1[1:int(len(freqx)/2-1)])
##                plt.xlim(0,150)
##                plt.ylim(0,500)
##                plt.figure()
##                plt.plot(freqx[1:int(len(freqx)/2-1)],FreqPow2[1:int(len(freqx)/2-1)])
##                plt.xlim(0,150)
##                plt.ylim(0,500)
##                plt.figure()
##                plt.plot(freqx[1:int(len(freqx)/2-1)],FreqPow3[1:int(len(freqx)/2-1)])
##                plt.xlim(0,150)
##                plt.ylim(0,500)
##                plt.show()
  ##End of FFT

                
##                print(time.time())
##                print(' ')
        ##        print(t)
                #plt.plot(t1,P2)
            ##    plt.plot(t1,P2)
            ##    plt.plot(t1,P3)



finally:
##    file.
    file_directory = open("Phase detector output directory.txt","a")
    file_directory.write(" \n") #lets Processing to know to wait for a new file
    file_directory.close()       
