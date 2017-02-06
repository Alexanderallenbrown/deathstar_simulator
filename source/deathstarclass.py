""" Class Intro Here"""

#Alexander Brown, Ph.D.
#September 9, 2015

from numpy import *
from scipy import *
from matplotlib.pyplot import *
import time

class DeathStar:
    #class owned vars
    def __init__(self,dt=0.001,t1=0,t2=0,Jst=1,platemass=5,l1=1,l2=1,b1=1,b2=1,starscale=130,shotweight=0.1,mst=15,use_pygame=False):
        self.t2store = t2
        self.Jst = Jst
        self.t1 = t1#star angle
        self.t2 = t2#swinger angle
        self.t1d = 0#star angular vel
        self.t2d = 0#swinger angular vel
        self.g = 9.81#gravity
        self.dt = dt#time step. SHOULD BE UPDATED CONTINUOUSLY
        self.starttime=0
        #star properties
        self.platemass=platemass
        self.m1 = platemass
        self.m2 = platemass
        self.m3 = platemass
        self.m4 = platemass
        self.m5 = platemass
        self.mst = mst
        self.l1=l1
        self.l2=l2
        #angle between arms
        self.alpha = 2*pi/5
        self.b1 = b1
        self.b2 = b2

        #plate diameter
        self.radius=.3

        #what scale to draw star at
        self.starscale = starscale
        self.shotweight= shotweight
        #do we simulate the dynamics?
        self.simulate=False
        self.simtime = 0

        #star position
        self.xst = -self.l2*cos(self.t2)
            #mass five
        self.yst = -self.l2*sin(self.t2)
        #mass one
        self.x1 = self.xst-self.l1*sin(self.t1)
        self.y1 = self.yst + self.l1*cos(self.t1)
        #mass two
        self.x2 = self.xst-self.l1*sin(self.t1+self.alpha)
        self.y2 = self.yst + self.l1*cos(self.t1+self.alpha)
        #mass three
        self.x3 = self.xst-self.l1*sin(self.t1+2*self.alpha)
        self.y3 = self.yst + self.l1*cos(self.t1+2*self.alpha)
        #mass four
        self.x4 = self.xst-self.l1*sin(self.t1+3*self.alpha)
        self.y4 = self.yst + self.l1*cos(self.t1+3*self.alpha)
        #mass five
        self.x5 = self.xst-self.l1*sin(self.t1+4*self.alpha)
        self.y5 = self.yst + self.l1*cos(self.t1+4*self.alpha)

    ###### 9/9/2015 10:10AM

    def plotStar(self,scale=1):

        #clear the figure
        cla()

        #star position
        xst = -self.l2*cos(self.t2)
        yst = -self.l2*sin(self.t2)
        #mass one
        x1 = xst-self.l1*sin(self.t1)
        y1 = yst + self.l1*cos(self.t1)
        #mass two
        x2 = xst-self.l1*sin(self.t1+self.alpha)
        y2 = yst + self.l1*cos(self.t1+self.alpha)
        #mass three
        x3 = xst-self.l1*sin(self.t1+2*self.alpha)
        y3 = yst + self.l1*cos(self.t1+2*self.alpha)
        #mass four
        x4 = xst-self.l1*sin(self.t1+3*self.alpha)
        y4 = yst + self.l1*cos(self.t1+3*self.alpha)
        #mass five
        x5 = xst-self.l1*sin(+self.t1+4*self.alpha)
        y5 = yst + self.l1*cos(+self.t1+4*self.alpha)


        #star line
        plot([0,xst*scale],[0,yst*scale],'k')

        #mass one line
        plot([xst*scale,x1*scale],[yst*scale,y1*scale],'b')
        #mass one ellipse
        if (self.m1>self.shotweight):
            plot(x1*scale,y1*scale,'ko',markersize=10*scale)

        #mass 2 line
        plot([xst*scale,x2*scale],[yst*scale,y2*scale],'b')
        #mass 2 ellipse
        if (self.m2>self.shotweight):
            plot(x2*scale,y2*scale,'ko',markersize=10*scale)

        #mass 3 line
        plot([xst*scale,x3*scale],[yst*scale,y3*scale],'b')
        #mass 3 ellipse
        if (self.m3>self.shotweight):
            plot(x3*scale,y3*scale,'ko',markersize=10*scale)

        #mass 4 line
        plot([xst*scale,x4*scale],[yst*scale,y4*scale],'r')
        #mass 4ellipse
        if (self.m4>self.shotweight):
            plot(x4*scale,y4*scale,'ro',markersize=10*scale)

        #mass 5 line
        plot([xst*scale,x5*scale],[yst*scale,y5*scale],'b')
        #mass one ellipse
        if (self.m5>self.shotweight):
            plot(x5*scale,y5*scale,'ko',markersize=10*scale)

        axis('equal')
        axis([-2.5*scale,2.5*scale,-2.5*scale,2.5*scale])

        pause(.001)


    def statederivs(self,th1,th1d,th2,th2d):
    #println(t)
        p0 = self.m1+self.m2+self.m3+self.m4+self.m5
        p3 = p0+self.mst
        p1 = self.m1*cos(th1-th2)+self.m2*cos(th1+self.alpha-th2)+self.m3*cos(th1+2*self.alpha-th2)+self.m4*cos(th1+3*self.alpha-th2)+self.m5*cos(th1+4*self.alpha-th2)
        p2 = self.m1*sin(th1-th2)+self.m2*sin(th1+self.alpha-th2)+self.m3*sin(th1+2*self.alpha-th2)+self.m4*sin(th1+3*self.alpha-th2)+self.m5*sin(th1+4*self.alpha-th2)
        p4 = p1
        p5 = p2

        dldt1 = self.l1*self.g*(self.m1*sin(th1)+self.m2*sin(th1+self.alpha)+self.m3*sin(th1+2*self.alpha)+self.m4*sin(th1+3*self.alpha)+self.m5*sin(th1+4*self.alpha))-self.l1*self.l2*th1d*th2d*p2
        dldt2 = (self.l1*self.l2*th1d*th2d*p2+self.l2*self.g*cos(th2)*p3)

        #set class-owned state derivs.
        t1ddot = 1/((p0*self.l1*self.l1+self.Jst)*(1-p1*p4/(p0*p3)))*(dldt1+self.l1*self.l2*(   p2*th2d*(th1d-th2d) - p1/(p3*self.l2*self.l2)*   ( dldt2 + p5*self.l1*self.l2*th1d*(th1d-th2d) ) ) -self.b1*(th1d-th2d))
        t2ddot = 1/(p3*self.l2*self.l2*(1-p1*p4/(p0*p3)))*(dldt2+self.l1*self.l2*(   p5*th1d*(th1d-th2d) -p4/(p0*self.l1*self.l1)*   ( dldt1  + p2*self.l1*self.l2*th2d*(th1d-th2d) ) ) -self.b2*th2d)
        return t1ddot,t2ddot

    def updateDynamics(self,dt):

        #now update dynamics.
        if (self.simulate==True):
            self.simtime+=dt
            #improved euler integration
            t1ddot,t2ddot = self.statederivs(self.t1,self.t1d,self.t2,self.t2d)
            oldt1ddot = t1ddot
            oldt2ddot = t2ddot
            oldt1d = self.t1d+ oldt1ddot*dt
            oldt2d = self.t2d+ oldt2ddot*dt
            oldt1 = self.t1+oldt1d*dt
            oldt2 = self.t2 + oldt2d*dt
            #correction using heun's method
            #first compute state derivs using euler's prediction
            t1ddot,t2ddot = self.statederivs(oldt1,oldt1d,oldt2,oldt2d)
            #then compute actual new vals using the average
            self.t1 += dt/2*(oldt1d+self.t1d)
            self.t2 += dt/2*(oldt2d+self.t2d)
            self.t1d += dt/2*(oldt1ddot + t1ddot)
            self.t2d += dt/2*(oldt2ddot + t2ddot)

            #star position
            self.xst = -self.l2*cos(self.t2)
            self.yst = -self.l2*sin(self.t2)
            #mass one
            self.x1 = self.xst-self.l1*sin(self.t1)
            self.y1 = self.yst + self.l1*cos(self.t1)
            #mass two
            self.x2 = self.xst-self.l1*sin(self.t1+self.alpha)
            self.y2 = self.yst + self.l1*cos(self.t1+self.alpha)
            #mass three
            self.x3 = self.xst-self.l1*sin(self.t1+2*self.alpha)
            self.y3 = self.yst + self.l1*cos(self.t1+2*self.alpha)
            #mass four
            self.x4 = self.xst-self.l1*sin(self.t1+3*self.alpha)
            self.y4 = self.yst + self.l1*cos(self.t1+3*self.alpha)
            #mass five
            self.x5 = self.xst-self.l1*sin(self.t1+4*self.alpha)
            self.y5 = self.yst + self.l1*cos(self.t1+4*self.alpha)

        #return the time step so we can keep track.
        return self.t1,self.t2,self.t1d,self.t2d
    
    def checkHit_delayed(self,xp, yp,spread,t1,t2,height=500,width=500):
        #star position
        xst = -self.l2*cos(t2)
        yst = -self.l2*sin(t2)
        #mass one
        x1 = xst-self.l1*sin(t1)
        y1 = yst + self.l1*cos(t1)
        #mass two
        x2 = xst-self.l1*sin(t1+self.alpha)
        y2 = yst + self.l1*cos(t1+self.alpha)
        #mass three
        x3 = xst-self.l1*sin(t1+2*self.alpha)
        y3 = yst + self.l1*cos(t1+2*self.alpha)
        #mass four
        x4 = xst-self.l1*sin(t1+3*self.alpha)
        y4 = yst + self.l1*cos(t1+3*self.alpha)
        #mass five
        x5 = xst-self.l1*sin(t1+4*self.alpha)
        y5 = yst + self.l1*cos(t1+4*self.alpha)

        d1sq = (xp-x1)*(xp-x1)+(yp-y1)*(yp-y1)
        d2sq = (xp-x2)*(xp-x2)+(yp-y2)*(yp-y2)
        d3sq = (xp-x3)*(xp-x3)+(yp-y3)*(yp-y3)
        d4sq = (xp-x4)*(xp-x4)+(yp-y4)*(yp-y4)
        d5sq = (xp-x5)*(xp-x5)+(yp-y5)*(yp-y5)
        dists = [d1sq,d2sq,d3sq,d4sq,d5sq]
        mindist = min(dists)**.5
        targtried = argmin(dists)+1#added one so that does not start at 0
        #println(x1,y1,x2,y2,x3,y3,x4,y4,x5,y5)
        #println(d1sq,d2sq,d3sq,d4sq,d5sq)
        targhit = 0
        if (d1sq<=spread*spread*self.radius*self.radius):
            if(self.m1>self.shotweight):
                self.m1=self.shotweight
                targhit = 1

        if (d2sq<=spread*spread*self.radius*self.radius):
            if(self.m2>self.shotweight):
                self.m2=self.shotweight
                targhit = 2

        if (d3sq<=spread*spread*2*self.radius*self.radius):
         if(self.m3>self.shotweight):
            self.m3=self.shotweight
            targhit=3

        if (d4sq<=spread*spread*2*self.radius*self.radius):
            if(self.m4>self.shotweight):
                self.m4=self.shotweight
                if self.simulate is not True:
                    self.simulate=True
                    self.setstarttime()
                targhit = 4

        if (d5sq<=spread*spread*self.radius*self.radius):
            if(self.m5>self.shotweight):
                self.m5=self.shotweight
                targhit = 5
        return self.simtime,targhit,targtried,mindist
       # print d1sq,d2sq,d2sq,d4sq,d5sq
    def setstarttime(self):
        self.starttime=time.time()
    def reset(self,t1=0,t2=0):
        self.simulate=False
        self.t1=t1
        self.t2=t2
        self.t1d=0
        self.t2d=0
        self.m1=self.platemass
        self.m2=self.platemass
        self.m3=self.platemass
        self.m4=self.platemass
        self.m5=self.platemass
        self.simtime=0

    def checkHit(self,xp, yp,spread,height=500,width=500):
        d1sq = (xp-self.x1)*(xp-self.x1)+(yp-self.y1)*(yp-self.y1)
        d2sq = (xp-self.x2)*(xp-self.x2)+(yp-self.y2)*(yp-self.y2)
        d3sq = (xp-self.x3)*(xp-self.x3)+(yp-self.y3)*(yp-self.y3)
        d4sq = (xp-self.x4)*(xp-self.x4)+(yp-self.y4)*(yp-self.y4)
        d5sq = (xp-self.x5)*(xp-self.x5)+(yp-self.y5)*(yp-self.y5)
        #println(x1,y1,x2,y2,x3,y3,x4,y4,x5,y5)
        #println(d1sq,d2sq,d3sq,d4sq,d5sq)
        targhit = 0
        if (d1sq<=spread*spread*self.radius*self.radius):
            if(self.m1>self.shotweight):
                self.m1=self.shotweight
                targhit = 1

        if (d2sq<=spread*spread*self.radius*self.radius):
            if(self.m2>self.shotweight):
                self.m2=self.shotweight
                targhit = 2

        if (d3sq<=spread*spread*2*self.radius*self.radius):
         if(self.m3>self.shotweight):
            self.m3=self.shotweight
            targhit=3

        if (d4sq<=spread*spread*2*self.radius*self.radius):
            if(self.m4>self.shotweight):
                self.m4=self.shotweight
                self.simulate=True
                self.starttime=time.time()
                targhit = 4

        if (d5sq<=spread*spread*self.radius*self.radius):
            if(self.m5>self.shotweight):
                self.m5=self.shotweight
                targhit = 5
        return self.simtime,targhit
       # print d1sq,d2sq,d2sq,d4sq,d5sq

    def reset(self,t1=0,t2=0):
        self.simulate=False
        self.t1=t1
        self.t2=t2
        self.t1d=0
        self.t2d=0
        self.m1=self.platemass
        self.m2=self.platemass
        self.m3=self.platemass
        self.m4=self.platemass
        self.m5=self.platemass
        self.simtime=0

    def runsim(self,simtime,shot_times,targets_hit,timevec = None,animate=False):
        """def runsim(self,simtime,shot_times,targets_hit,timevec = None):
            runs a post-hoc simulation of the target when shot times and targets hit are known.
            If you don't want to use the star's built-in dt, you can specify a time vector. This will override dt
        """
        if (timevec==None):
            tvec = arange(0,simtime,self.dt)#time vector
        else:
            tvec = timevec

        hit_index = 0 #for hits only
        shot_index = 0#for all shots
        t1vec = zeros(len(tvec))
        t2vec = zeros(len(tvec))
        t1dvec = zeros(len(tvec))
        t2dvec = zeros(len(tvec))
        if animate==True:
            ion()
            figure()


        #starting at the second index, simulate the star.
        for ind in range(1,len(tvec)):
            self.dt = tvec[ind]-tvec[ind-1]
            
            #
            if shot_index>(len(shot_times)-1):
                shot_index = len(shot_times)-1
            if hit_index>=len(targets_hit)-1:
                hit_index=len(targets_hit)-1
            if tvec[ind]>=shot_times[shot_index]:
            
                if targets_hit[hit_index]!=0:
                    if targets_hit[hit_index]==1:
                        self.m1=self.shotweight
                    if targets_hit[hit_index]==2:
                        self.m2 = self.shotweight
                    if targets_hit[hit_index]==3:
                        self.m3 = self.shotweight
                    if targets_hit[hit_index]==4:
                        self.m4 = self.shotweight
                        self.simulate=True
                    if targets_hit[hit_index]==5:
                        self.m5 = self.shotweight
                    hit_index+=1

                shot_index+=1

            self.updateDynamics(self.dt)
            if animate==True:
                self.plotStar()

            t1vec[ind] = self.t1
            t2vec[ind] = self.t2
            t1dvec[ind] = self.t1d
            t2dvec[ind] = self.t2d
        return tvec,t1vec,t1dvec,t2vec,t2dvec






if __name__ == '__main__':
    """ this is a demo for the death star module. """
    #first, we initialize a star instance.
    star = DeathStar(dt=.033,l1=0.7,l2=0.8,b1=2.5,b2=1.5,platemass=5,t2=.5,shotweight=0.001,Jst=1.7,mst=20)

    #make up some shot times
    #shots = array([0.0,1.0,2.0,3.0,4.0])
    shots = array([0,.33,0.62])#shots
    hits = array([4,3,2])
    #which targets did we hit?
    #hits = array([4,5,3,1,2])
    #how long should we run our simulation?
    tmax = 10#seconds

    tvec,theta1,theta1dot,theta2,theta2dot=star.runsim(tmax,shots,hits,animate=True)
    # figure(1)
    # axis('equal')
    # ion()
    # for ind in range(0,100,len(tvec)):
    #     cla()
    #     star.plotStar()
    #     # show()
    #     pause(0.1)


    figure(2)
    subplot(2,1,1)
    plot(tvec,theta1)
    ylabel('Star Angle (rad)')
    subplot(2,1,2)
    plot(tvec,theta2)
    ylabel('Hinge Angle (rad)')
    xlabel('Time (s)')
    show()

    
