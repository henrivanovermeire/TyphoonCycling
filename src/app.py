#-*- coding: utf"-8 -*-

import PySimpleGUI as sg

#import tkinter

import numpy as np

import matplotlib.pyplot as plt

import fitdecode

from scipy.signal import lfilter

#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import time

import math

#import os.path

from os.path import exists

import warnings



#from scipy.stats import norm as nm





reft = [120.,300.,600.,1200.,2400.]

refp=[]

filename = 'None'

reffile = ' None.txt'

p = []

alt = []

# dt = 0.5 # For Lars Bak

dt=1

ref = []

wbal= []

bmass=50

startlap=1

stoplap=100

s=5

fs=14

tickfs=14





breakflag=False

plottmax = 0

ptflag=False

againflag=False



def sniffFile():

    

    file = open(filename, mode= 'rb')

    header = file.readline()

    altcol = -1

    timecol = 0

    pcol = -1

    hrcol = -1

    x = header.split(b',')

    for column in x:

        if "ower" in str(column) or "watt" in str(column):

            pcol = x.index(column)

            

        elif "ltitu" in str(column):

             altcol = x.index(column)

        elif "eart" in str(column):

            hrcol=x.index(column)

    return pcol, altcol,hrcol



def getdata() :

    pread=[]

    altread=[]

    hrread=[]



    with warnings.catch_warnings():

        warnings.filterwarnings('ignore')

        if ".csv" in str(filename):

            pcol, altcol,hrcol = sniffFile()

##            print('-----------')

##            print('colnumber   ', pcol, altcol, hrcol)

            if pcol != -1:

                pread = np.genfromtxt(open(filename, "rb"),delimiter=",",skip_header=1, usecols=pcol,filling_values=5)

                n=len(pread)

            else :

                print('No Power data in this file')

            if altcol != -1:

                altread = np.genfromtxt(open(filename, "rb"),delimiter=",",skip_header=1, usecols=altcol,filling_values=0)

            else:

                print('No altitude data  in this file')

                altread=[0]*n

            if hrcol != -1:

                hrread = np.genfromtxt(open(filename, "rb"),delimiter=",",skip_header=1, usecols=hrcol,filling_values=0,)

            else:

                print('No HR data in this file')

                hrread=[0]*n

        elif (".fit" in str(filename) or ".FIT" in str(filename)) :

            with fitdecode.FitReader(filename) as fit_file:

                for frame in fit_file:

                    if isinstance(frame, fitdecode.records.FitDataMessage):

                        if frame.name == 'record':

                            if frame.has_field('power'):

                                pow=frame.get_value('power')

                                if type(pow)==int or type(pow)==float:

                                    pread.append(frame.get_value('power'))

                                    if frame.has_field('altitude'):

                                        altread.append(frame.get_value('altitude'))

                                    else:

                                        altread.append(0)

                                    if frame.has_field('heart_rate'):

                                        heart=frame.get_value('heart_rate')

                                        if type(heart)==int or type(heart)==float:  

                                            hrread.append(frame.get_value('heart_rate'))

                                        else:

                                            hrread.append(0)

                                    else:

                                        hrread.append(0)

                                        

        for i in range(2,len(hrread)):   #Avoid false hr readings

             if (math.isnan(hrread[i]) or hrread[i]==0):

                 hrread[i]=hrread[i-1]

             

    return pread, altread, hrread

    

    

def inputWindow():

    global startlap,stoplap,s,ptflag,ref,againflag,iri

    sg.theme('DarkAmber')

    layout=[

     [sg.Text('Welcome to Anaerobic analysis software of Charles Dauwe',font=('any 16' ))],

      

      [sg.Text('All info on www.TyphoonCycling.org',font=('any 16'))],

    

      [sg.Text('Your Recovery Index',font=('any 16'),size=(18,1)), sg.InputText("0.8", key = 'iri',size=(5,1),font=('any 16'),justification='r')],

    [sg.Text('Calibration Power-Duration points',font=('any 16')), sg.FileBrowse('Choose File', font=('any 16'),key= 'reffile', file_types=(("Text Files","**"),)), sg.OK(font=('any 16'))],

      

    [sg.Text('Best  2 Minutes Power',font=('any 16'),size=(18,1)), sg.InputText("0", key = 'refp1',size=(5,1),font=('any 16'),justification='r'),

     sg.Text('         RT',font=('any 16'),size=(8,1)),sg.InputText('0',key='rtfield',size=(5,1),font=('any 16'),justification='r'),sg.Text('W',font='any 16')],

    [sg.Text('Best  5 Minutes Power',font=('any 16'),size=(18,1)), sg.InputText("0", key = 'refp2',size=(5,1),font=('any 16'),justification='r'),

     sg.Text('         MAP',font=('any 16'),size=(8,1)),sg.InputText('0',key='mapfield',size=(5,1),font=('any 16'),justification='r'),sg.Text('W',font='any 16')],

    [sg.Text('Best 10 Minutes Power',font=('any 16'),size=(18,1)), sg.InputText("0", key = 'refp3',size=(5,1) ,font=('any 16'),justification='r'),

     sg.Text('         SCP',font=('any 16'),size=(8,1)),sg.InputText('0',key='scpfield',size=(5,1),font=('any 16'),justification='r'),sg.Text('W',font='any 16')],

    [sg.Text('Best 20 Minutes Power',font=('any 16'),size=(18,1)), sg.InputText("0", key = 'refp4',size=(5,1) ,font=('any 16'),justification='r'),

     sg.Text('         W',font=('any 16'),size=(8,1)),sg.InputText('0',key='wfield',size=(5,1),font=('any 16'),justification='r'),sg.Text('kJ',font='any 16')],

    [sg.Text('Best 40 Minutes Power',font=('any 16'),size=(18,1)), sg.InputText("0", key = 'refp5',size=(5,1) ,font=('any 16'),justification='r'),

     sg.Text('   VO2max',font=('any 16'),size=(8,1)),sg.InputText('0',key='vo2maxfield',size=(5,1),font=('any 16'),justification='r'),sg.Text('ml/min/kg',font='any 14')],

    [sg.Text('Body Mass',font=('any 16')), sg.InputText("0", key = 'bmass',size=(5,1),font=('any 16'),justification='r'),sg.Text('kg',font='any 16',size=(4,1))],

    [sg.Text('Show ECP graph ?',font=('any 16')), sg.Checkbox("", key = 'ptflag',size=(5,1),font=('any 16'))],

    [[sg.Text('Choose a CSV or FIT Power File : ',font=('any 16')), sg.FileBrowse(key = 'filename', font=('any 16'),file_types=(("All Files","*.*"),))]],

    

    [sg.Text('ROI starts at ',font=('any 16')), sg.InputText("0", key = 'start',size=(5,1),font=('any 16'),justification='r'),sg.Text('Ends at',font=('any 16'),justification='r'), sg.InputText("0", key = 'end',size=(5,1),font=('any 16'),justification='r')],

    [sg.Text('Smooth factor = ',font=('any 16')),sg.InputText("1",key='sm',size=(2,1),font=('any 16'),justification='r')],   

    [sg.Submit(font=('any 16'))] #, sg.Cancel(font=('any 16'))],

    ]

    win = sg.Window('Typhoon Cycling', layout)

    while True:

        event, values = win.read()

        if event == sg.WIN_CLOSED : #or event == 'Cancel':

            breakflag=True

            break

        elif event == "OK":

            reffile=values['reffile']

            if exists(reffile):

                againflag=True

                #print(exists(reffile))

                ref = np.loadtxt(values['reffile'],encoding='utf-8')

                #print(ref)

                    

                win.Element('refp1').update(int(ref[0]))

                win.Element('refp2').update(int(ref[1]))

                win.Element('refp3').update(int(ref[2]))

                win.Element('refp4').update(int(ref[3]))

                win.Element('refp5').update(int(ref[4]))

                win.Element('bmass').update(ref[5])

                CP, W, RT, scp, slope = calcRef(ref)

                win.Element('rtfield').update(int(RT))

                win.Element('mapfield').update(int(CP))

                win.Element('scpfield').update(int(scp))

                win.Element('wfield').update(W/1000)

                win.Element('vo2maxfield').update(vo2max)

                ptflag=values['ptflag']

                if ptflag==True:

                    showcpanalysis(u,ref)



                    

            elif againflag==True:

                win.Element('refp1').update(int(ref[0]))

                win.Element('refp2').update(int(ref[1]))

                win.Element('refp3').update(int(ref[2]))

                win.Element('refp4').update(int(ref[3]))

                win.Element('refp5').update(int(ref[4]))

                win.Element('bmass').update(ref[5])

                CP, W, RT, scp, slope = calcRef(ref)

                win.Element('rtfield').update(int(RT))

                win.Element('mapfield').update(int(CP))

                win.Element('scpfield').update(int(scp))

                win.Element('wfield').update(W/1000)

                win.Element('vo2maxfield').update(vo2max)

                ptflag=values['ptflag']

                if ptflag==True:

                    showcpanalysis(u,ref)

                

    

            else:

                

                sg.popup('Choose a power calibration file',font=('any 18'),background_color='grey',title=' ')

            

        elif event == "Submit":

       

            refp.append(float(values["refp1"]))

            refp.append(float(values["refp2"]))   

            refp.append(float(values["refp3"]))

            refp.append(float(values["refp4"]))

            refp.append(float(values["refp5"]))

            refp.append(float(values["bmass"]))

            startlap=int(values["start"])

            stoplap=int(values["end"])

            s=max(1,int(values["sm"]))

            iri=float(values['iri'])

            global filename

    

            filename = values["filename"]

            if (exists(filename) and againflag) :

                break

            else:

                sg.popup('Choose Power and/or Calibration File',title=' ',background_color='Grey',font='any 18')

                

    win.close()

        



def calcRef(ref):

    global bmass

    global CP

    global W

    global RT

    global scp

    global slope

    global vo2max

    global W2

    global u

    global p5

    global p1

    

    bmass=ref[5]

    # Shortest TD data for CP and W'   Careful: Indexing start at 0

    u = np.reciprocal(reft)

    v = ref

    global plottmax, p60

    plottmax=np.max(u)

    par=np.polyfit(u[0:3],ref[0:3],1)

    CP = par[1]

    W=par[0]

    # Longest TD data for RT, W2 

    W2 = (ref[3] - ref[4])/(1/reft[3] - 1/reft[4])

    RT = ref[4] - (W2/reft[4])

    tscp = (W2 - W)/(CP-RT)

    scp = CP + W/tscp # Volhoudtijd aan SCP

    slope = (1 - CP/scp)/(scp - RT)

    p60 = CP + W/60   # Powr for 1 minute

    p1 = CP + W/60

    p2 = CP + W/120

    p5 = CP + W/300

    p10 = CP + W/600

    p20 = RT + W2/1200

    p40 = RT + W2/2400

    vo2max=round(7+12.6*CP/bmass)

    

    

    print("------- Critical Power Values -------")

    print ("Recovery Threshold is : ", round(RT)," Watt")

    print ("Maximal Aerobic Power is : ",round(CP)," Watt")  

    print ("Estimated VO2max : ",vo2max," ml/kg/min")  

    print ("Supercritical Power is : ",round(scp)," Watt")

    print ("Anaerobic Capacity is : ",int(W)," Joule")

    #showcpanalysis(u,ref)

    

    

    return CP, W, RT, scp, slope



def showcpanalysis(u,v):

    

    xplot1=u[0:3] # Fast Dead

    yplot1=v[0:3] # Fast dead

    xplot2=u[3:5] # Slow dead

    yplot2=v[3:5] # Slow dead

    xplot3=(0, 1/120)

    yplot3=(CP,CP+W/120)

    xplot4=(0,1/600)

    yplot4=(RT,RT+W2/600)

   # fs=16

    fig, (ax1) = plt.subplots(1,figsize=(6,5))

    #fig.canvas.manager.set_window_title('Typhoon Cycling')    

    fig.suptitle('Extended CP analysis')

    ax1.set_ylabel('Power (W)', fontsize=fs,color='blue')

    ax1.set_xlabel('Inverse duration 1/sec', fontsize=fs,color='blue')      

    ax1.plot(xplot1,yplot1, 'r*',markersize=12)

    ax1.plot(xplot3,yplot3,'r--')

    ax1.plot(xplot4,yplot4,'b--')

    ax1.plot(xplot2,yplot2,'b*',markersize=12)

    ax1.set_xlim([0, 0.009])

    ax1.grid()

    plt.show()

    

def calcBalance(CP, W, RT, scp, slope, power,iri):

    global AL,EL,FL,totalenergy,hr,wbal

    #p = np.loadtxt(open(filename, "rb"),delimiter=",",skiprows=1, usecols=pcol)

    global n

    p=power

    n = len(p)

    #print('lengte = ',n)

    #anfrac = [0]*n    

    AL = 0  # Aerobic Load

    EL = 0 # Slow dead load

    FL = 0  # Fast dead load

    tau = [0] * n

    fr = [0] *n

    wbal = [0] * n

    wbal[0] = W

    wbal[1]=W

    

    for i in range(2,n):

        if p[i] < RT:  

           fr[i] = 0

           wref=max(wbal[i-1],0)  # To avoid problems with negative balance

           tau[i] = max(wbal[i-1]/((RT - p[i])*iri),10) # Correction for IRI and limit value of 60 s

           #anaplus = min((W - wref)*(1 - np.exp(-dt/tau[i])),CP)

           #anaplus = min((W - wref)*(1 - np.exp(-dt/tau[i])),(CP-p[i]))

           anaplus = min((W - wref)*(1 - np.exp(-dt/tau[i])),max(CP-p[i]-0.28*bmass,0))

           wbal[i]=wbal[i-1]+anaplus

           AL = p[i]*dt + AL

        elif p[i] < scp:

           fr[i] = (p[i] - RT)*slope

           #anaplus = 0

           EL = p[i]*fr[i]*dt + EL

           AL = (1-fr[i])*p[i]*dt +AL

           wbal[i]=wbal[i-1]-fr[i]*p[i]*dt

        else:

           fr[i]=(p[i] - CP)/p[i]

           wbal[i]=wbal[i-1]-fr[i]*p[i]*dt

           #anaplus = 0

           FL = p[i]*fr[i]*dt +FL

           AL = (1-fr[i])*p[i]*dt +AL

           

    totalenergy=np.sum(p)*dt

    nhr=len(hr)

    print('\nAnalising file ',filename )

    print('-------- This ride stress values-------')

    print('Total Energy spend = ', int(totalenergy/1000), '  kJ')

    print('Maximal Power ',int(max(p)),'Watt')

    print('Maximal Heart Rate',int(max(hr[1:nhr])),'bpm')

    print('Aerobic Load is :', round(AL/(3600*RT),2))

    print('Slow Dead Load is = ', round(EL/W,2))

    print('Fast Dead Load is = ', round(FL/W,2))

          

    return wbal, totalenergy



def showtimezonebars():

    binlimits=[0,0.6*RT,0.75*RT,RT,scp,p5,p1,2000]  # ECP zones

    str1=str(int(binlimits[0]))+'-'+str(int(binlimits[1]))

    str2=str(int(binlimits[1]))+'-'+str(int(binlimits[2]))

    str3=str(int(binlimits[2]))+'-'+str(int(binlimits[3]))

    str4=str(int(binlimits[3]))+'-'+str(int(binlimits[4]))

    str5=str(int(binlimits[4]))+'-'+str(int(binlimits[5]))

    str6=str(int(binlimits[5]))+'-'+str(int(binlimits[6]))

    str7=str(int(binlimits[6]))+'-'+str(int(binlimits[7]))



    

    fig, ax = plt.subplots(figsize=(10,7))

    string='Typhoon Cycling    ' + filename

    fig.canvas.manager.set_window_title(string)   

    zones = ['Recover \n '+str1, 'FatMax \n'+str2, 'CarbMax\n'+str3 , 'SlowDeath\n'+str4,'VO2max\n'+str5 ,'Anaerobic\n'+str6,'Explosive\n'+str7 ]

    bar_colors = ['#99FF99','#00FF00','#009900','#FF8000', '#FF3333', '#990099','000000']

    hist,bin_edges =np.histogram(power,bins=binlimits)

    ax.bar(zones, dt*hist/60,  color=bar_colors, width=0.98)

    ax.set_ylabel('Minutes in zone',fontsize=16)

    #ax.set_title('Performance Chart')

    ax.grid(axis='y')

    ax.xaxis.set_tick_params(labelcolor='k',labelsize=fs*0.9)

    ax.yaxis.set_tick_params(labelcolor='k',labelsize=fs)

    plt.show()



def showpowerzonebars(p):

    binlimits=[0,0.6*RT,0.75*RT,RT,scp,p5,p1,2000]  # ECP zones

    str1=str(int(binlimits[0]))+'-'+str(int(binlimits[1]))

    str2=str(int(binlimits[1]))+'-'+str(int(binlimits[2]))

    str3=str(int(binlimits[2]))+'-'+str(int(binlimits[3]))

    str4=str(int(binlimits[3]))+'-'+str(int(binlimits[4]))

    str5=str(int(binlimits[4]))+'-'+str(int(binlimits[5]))

    str6=str(int(binlimits[5]))+'-'+str(int(binlimits[6]))

    str7=str(int(binlimits[6]))+'-'+str(int(binlimits[7]))

    z=[0]*(len(binlimits)-1)

    for i in range(len(p)):

        pp=p[i]

        for j in range(0,len(binlimits)-1):

            z[j]=z[j]+dt*pp*(pp>binlimits[j])*(pp<=binlimits[j+1])/1000  # Kilojouse



    fig, ax = plt.subplots(1,figsize=(10,7))

    string='Typhoon Cycling    ' + filename

    fig.canvas.manager.set_window_title(string)

    zones = ['Recover \n '+str1, 'FatMax \n'+str2, 'CarbMax\n'+str3 , 'SlowDeath\n'+str4,'VO2max\n'+str5 ,'Anaerobic\n'+str6,'Explosive\n'+str7 ]

    #zones = ['Recover', 'FatMax', 'CarbMax', 'SlowDeath','VO2max','Anaerobic','Explosive']

    bar_colors = ['#99FF99','#00FF00','#009900','#FF8000', '#FF3333', '#990099','000000']

    ax.bar(zones,z,width=0.98, align='center',color=bar_colors)

    ax.set_ylabel('Total Energy in Zone ( kJ)',fontsize=16)

    ax.grid(axis='y')

    ax.yaxis.set_tick_params(labelcolor='k',labelsize=fs)

    ax.xaxis.set_tick_params(labelcolor='k',labelsize=fs*0.9)

    #plt.show() 

   

       

def updateRefs(wbal):

    idx=0

    minvalue=wbal[0]

    for i in range(1,len(wbal)):

        if wbal[i] < minvalue:

            minvalue=wbal[i]

            idx=i

    minvalue=minvalue/W   

    if minvalue < -0.05 :

        for j in range(0,5):

            N2=reft[j]

            id0=int(idx-N2)

            pmax = sum(power[id0 : idx])/N2

            if pmax > refp[j] + 1:

                print('\n -----New record power found ----  ')

                str1='Reftime = '

                str2=str("{:.0f}".format(reft[j]/60))

                str3=' minutes      Refpower = '

                str4=str("{:.0f}".format(pmax))

                str5=' Watt'

                string=str1 + str2 +str3 + str4 + str5

                print(string)

                sg.Popup(string,font='any 18',title=' New record performance',)

                

             

if __name__ == '__main__':

    print("      Welcome to the Typhoon Cycling Software      ")

    print('Free version offered by charles.dauwe@telenet.be')

    print('All relevant explanations on www.typhooncycling.org')

    

    bf=False    

    filename='none'

    reffile='none'

    while True:

        if bf:

            break

        print('============================================')

        print()

        

        inputWindow()

        if breakflag:

            break

    

        pread, altread,hrread = getdata()

        

        if stoplap==0 or stoplap<startlap:

            stoplap=len(pread)

            

        power=pread[startlap:stoplap]

        alt=altread[startlap:stoplap]

        hr=hrread[startlap:stoplap]



        #print(CP,W,RT)

        wbal, etot =calcBalance(CP,W, RT,scp,slope,power,iri)

        updateRefs(wbal)

        nplot=np.arange(0, n, 1)   # For plots in seconds

        #xplot=nplot/3600    # For plots in hours

        xplot=dt*nplot/3600

        xmax=max(xplot)

        mina=min(alt)

        maxa=max(alt)

        if mina < 0:

            for i in range(0,n):

                alt[i]=alt[i]+abs(mina)

        h=alt

        # Smoothing

        b = [1.0 / s] * s

        a = 1

        pp=lfilter(b, a, power) 

        wbalpro=[1]*n

        for i in range(0,n):

           wbalpro[i]=wbal[i]/W*100

        nh=[100]*n

        zeros=[0]*n

        g=min(0,min(wbalpro))

        Aerobicload=AL/(3600*RT)

        Slowload=EL/W

        Fastload=FL/W

  # Plotting the Wbal results       

        fs=16

        ticksz=13

        fig, (ax1,ax2) = plt.subplots(2,figsize=(14,8))

        string='Typhoon Cycling    ' + filename

        fig.canvas.manager.set_window_title(string)    

        ax3 = ax2.twinx()

        ax1.set_ylabel('Anaerobic Balance (%)', fontsize=fs,color='red')       

        ax1.plot(xplot, wbalpro, color='red',linestyle='-',linewidth=2)

        ax1.axhline(y=100, color='red',linestyle='--', linewidth=2)

        ax1.axhline(y = 0, color='black', linestyle='--',linewidth=2, label = 'Wbal')

        ax1.fill_between(xplot/3600,wbalpro, nh, facecolor='lightgrey', interpolate=True)

        ax1.set_xlim([0, xmax])

        ax1.set_ylim(g,112)

        ax1.grid()

        str1="    Aerobic Load = "

        str2="    Slow dead Load = "

        str3="    Fast Dead Load = "

        str4="    Total Energy = "

        str11=str("{:.2f}".format(Aerobicload))

        str21=("{:.2f}".format(Slowload))

        str31=("{:.2f}".format(Fastload))

        str41=str(int(totalenergy/1000))

        string=str1 + str11 + str2 + str21 + str3 +str31+str4+str41+" kJ"

        ax1.text(xplot[0],102,string,fontsize=fs )

        ax1.xaxis.set_tick_params(labelsize=ticksz)

        ax1.yaxis.set_tick_params(labelsize=ticksz)

        ax4=ax1.twinx()

        ax4.plot(xplot,hr,color='black',linestyle='-',linewidth=1)

        ax4.set_ylabel('Heart Rate (bpm)',color='black',fontsize=fs)

        ax4.set_ylim(0,220)

        ax4.xaxis.set_tick_params(labelsize=ticksz)

        ax4.yaxis.set_tick_params(labelsize=ticksz)

        ax2.set_xlim([0, xmax])

        maxy=max(2.0*scp,max(pp))

        ax2.set_ylim([0,maxy])

        ax2.grid()

       # ax1.fill_between(nplot, wbalpro, facecolor='grey', interpolate=True)

        ax2.plot(xplot, pp, color='blue',linewidth=1, label='Delivered Power')

        ax2.set_ylabel('Power (W)',color='blue', fontsize=fs)

        ax2.axhline(y=scp, color='r', linestyle='--',linewidth=2, label='SCP: %d W' % round(scp))

        ax2.axhline(y=RT, color = 'g',linestyle='--',linewidth=2, label='RT: %d W' % round(RT))

        ax2.xaxis.set_tick_params(labelsize=ticksz)

        ax2.yaxis.set_tick_params(labelsize=ticksz)

        

        ax3.plot(xplot,h, color='brown', linestyle='-', linewidth=2)

        ax3.set_ylabel('Altitude (m)',color='brown', fontsize=fs)

        ax3.set_xlim([0, xmax])

        maxh=max(h)

        ax3.set_ylim([0,maxh*2+1])

        ax2.set_xlabel('Time (hours)',fontsize=fs)

        ax3.xaxis.set_tick_params(labelsize=ticksz)

        ax3.yaxis.set_tick_params(labelsize=ticksz)

        #ax2.set_xlabel('Time (hours',fontsize=fs)

        plt.show()

        #plt.draw()

        showtimezonebars()

        showpowerzonebars(power)

        plt.show()

        time.sleep(1)

        event=sg.popup_yes_no('Another Analysis ?',font='any 18',title=' ')

        if event=='No':

            print('Program ended')

            break
