#!/usr/bin/python
import pygame
from pygame.locals import *
from deathstarclass import DeathStar
from numpy import *
import cv2
import time
import thread


capture = cv2.VideoCapture(0)
laserlocx,laserlocy = array([0]),array([0])


def procvid(app):
    #grab image from camera
    while 1:
        ret,frame = capture.read()
        gray =cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        #crop the image so that it only includes the surface
        ow,oh,junk = frame.shape
        #print framehape
        graycrop = gray[app.rowlow:app.rowhigh,app.collow:app.colhigh]
        #ret2,thresh=cv2.threshold(graycrop,self.threshval,255,cv2.THRESH_BINARY)
        thresh = cv2.adaptiveThreshold(graycrop,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,51,app.threshval)

        laserlocy,laserlocx = where(thresh>0)
        app.laserlocx,app.laserlocy= laserlocx, laserlocy
        #print app.laserlocx,app.laserlocy
        #cv2.imshow('video',thresh)
        #cv2.waitKey(10)
                #print laserlocx,laserlocy
        if len(app.laserlocx)>0:
            meanx = median(app.laserlocx+5)
            meany = median(app.laserlocy+25)
            #print meanx*scalex,meany*scaley
            if app.oldlasershot==False:
                app.lasershotnow=True
                app.oldlasershot=True
                app.shotx = meanx*app.scalex
                app.shoty = meany*app.scaley

                shotxs= (app.shotx-app.width/2)/app.starscale
                shotys = -(app.shoty-app.height/2)/app.starscale

                #pygame.draw.circle(app._display_surf, green, (int(shotx),int(shoty)), app.plateradius, 5)
                #the star has a built-in hit checker. def checkHit(xp, yp,spread,height=500,width=500):
                app.lastshottime,targhit,j1,j2 = app.star.checkHit_delayed(shotxs,shotys,1,app.t1buf[0],app.t2buf[0],app.height,app.width)
                #print app.lastshottime,targhit
                if ((meanx*app.scalex-app.resetx)**2+(meany*app.scaley-app.resety)**2)<=app.plateradius**2:
                    app.star.reset(t2=0.5)
                    app.activator_hit=0#reset the activator
                
                if ((meanx*app.scalex-app.actx)**2+(meany*app.scaley-app.acty)**2)<=app.actplateradius**2:
                    app.activator_hit=1#set the activator hit to zero
                    app.activator_hittime = time.time()
                    #app.star.simulate=True
                    #app.star.setstarttime()
        else:
            if app.oldlasershot == True:
                app.lasershotnow=False
                app.oldlasershot=False



# See this: https://thinkrpi.wordpress.com/2013/05/22/opencv-and-camera-board-csi/

pygame.font.init() # you have to call this at the start,
myfont = pygame.font.SysFont("Comic Sans MS", 18)

red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
darkBlue = (0,0,128)
white = (255,255,255)
black = (0,0,0)
pink = (255,200,200)
grey = (128,128,128)
 
class App:
    def __init__(self):
        self.lagtime = 0.2#lag of the video
        #assume we run at 60 fps to start.
        #we will fill up these buffers for checking hits. Hits will be checked based on old angles.
        self.t1buf = zeros(int(60*self.lagtime)) 
        self.t2buf = zeros(int(60*self.lagtime))

        self.size = self.width, self.height = 720, 480
        self.rowlow,self.rowhigh,self.collow,self.colhigh = 0,200,150,520
        self.scalex = float(self.width)*1.0/float(self.colhigh-self.collow)
        self.scaley = float(self.height)*1.0/float(self.rowhigh-self.rowlow)-.40
        self.laserlocx,self.laserlocy=array([]),array([])
        self.lastshottime = 0
        self.oldtime = time.time() #set the last loop time
        self.dt = time.time()-self.oldtime
        self._running = True
        self._display_surf = None
        self._image_surf = None
        #self.background = pygame.image.load("rangebay.jpg")
        #self.bgrect = self.background.get_rect()
        
        self.star = DeathStar(l1=0.89,l2=0.8,b1=5,b2=.01,dt=self.dt,platemass=7.5,t2=.5,shotweight=0.001,Jst=3.51,mst=28.08)
        self.plateradius_meters = 5*.0254 #in meters, how large the plate diameter is.
        self.star.radius = self.plateradius_meters
        #we need to scale the star so that our height (480) gives us enough room at the bottom of the star.
        self.starscale = self.height*.4/(1.1*(self.star.l1+self.star.l2))
        self.star.starscale = self.starscale
        self.plateradius = int(self.plateradius_meters*self.starscale)
        print self.plateradius
        self.resetx = 50
        self.resety = 450
        #activator popper
        self.actx = 50
        self.acty = 240+100
        self.actplateradius = self.plateradius
        self.activator_hit = 0
        self.activator_delay = 0.2#in seconds, how long before we release the star after activator is hit.
        self.activator_down = 0#this only goes true after the delay has passed
        self.activator_hittime = 0

        

        self.oldlasershot = False
        self.currlasershot = False
        self.lasershotnow = False

        self.threshval = -16
        # self.oldlasershottime = time.time()
        # self.laserdelay = 0.1

    def draw_star(self):
        

        #this is mostly taken from the death star class, but adapted for pygame. Can't think of a good way to work it in...
        
        hingex = self.width/2
        hingey = self.height/2
        #star position
        xst = -self.star.l2*cos(-self.star.t2)*self.starscale+hingex
        yst = -(self.star.l2*sin(-self.star.t2))*self.starscale+hingey
        #mass one
        x1 = xst+self.starscale*self.star.l1*sin(-self.star.t1)
        y1 = yst - self.starscale*self.star.l1*cos(-self.star.t1)
        #mass two
        x2 = xst+self.starscale*self.star.l1*sin(-self.star.t1-self.star.alpha)
        y2 = yst - self.starscale*self.star.l1*cos(-self.star.t1-self.star.alpha)
        #mass three
        x3 = xst+self.starscale*self.star.l1*sin(-self.star.t1-2*self.star.alpha)
        y3 = yst - self.starscale*self.star.l1*cos(-self.star.t1-2*self.star.alpha)
        #mass four
        x4 = xst+self.starscale*self.star.l1*sin(-self.star.t1-3*self.star.alpha)
        y4 = yst - self.starscale*self.star.l1*cos(-self.star.t1-3*self.star.alpha)
        #mass five
        x5 = xst+self.starscale*self.star.l1*sin(-self.star.t1-4*self.star.alpha)
        y5 = yst - self.starscale*self.star.l1*cos(-self.star.t1-4*self.star.alpha)

        pygame.draw.lines(self._display_surf, white, False, [(hingex,hingey), (xst,yst)], 3)
        pygame.draw.lines(self._display_surf, grey, False, [(xst,yst), (x1,y1)], 3)
        pygame.draw.lines(self._display_surf, grey, False, [(xst,yst), (x2,y2)], 3)
        pygame.draw.lines(self._display_surf, grey, False, [(xst,yst), (x3,y3)], 3)
        pygame.draw.lines(self._display_surf, red, False, [(xst,yst), (x4,y4)], 3)
        pygame.draw.lines(self._display_surf, grey, False, [(xst,yst), (x5,y5)], 3)




        #mass one ellipse
        if (self.star.m1>self.star.shotweight):
            pygame.draw.circle(self._display_surf, grey, (int(x1),int(y1)), self.plateradius, 0)

        #mass 2 ellipse
        if (self.star.m2>self.star.shotweight):
            pygame.draw.circle(self._display_surf, grey, (int(x2),int(y2)), self.plateradius, 0)

        #mass 3 ellipse
        if (self.star.m3>self.star.shotweight):
            pygame.draw.circle(self._display_surf, grey, (int(x3),int(y3)), self.plateradius, 0)

        
        #mass 4ellipse
        if (self.star.m4>self.star.shotweight):
            pygame.draw.circle(self._display_surf, red, (int(x4),int(y4)), self.plateradius, 0)

        #mass one ellipse
        if (self.star.m5>self.star.shotweight):
            pygame.draw.circle(self._display_surf, grey, (int(x5),int(y5)), self.plateradius, 0)
 
    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_mode((720,480),pygame.FULLSCREEN)
        self._running = True
        self._display_surf.fill((0,0,0))
        #self._display_surf.blit(self.background,self.bgrect)
 
    def on_event(self, event):

        if(event.type is KEYDOWN and event.key==K_w):
            pygame.display.set_mode(self.size)
        if (event.type is KEYDOWN and event.key==K_f):
            pygame.display.set_mode(self.size,FULLSCREEN)
        if (event.type is KEYDOWN and event.key==K_i):
            self.threshval+=1
        if (event.type is KEYDOWN and event.key==K_k):
            self.threshval-=1
        #let's look for hits based on mouse clicks!!
        if event.type == pygame.MOUSEBUTTONDOWN:
            #get the mouse position
            pos = pygame.mouse.get_pos()
            print pos[0],pos[1]
            #pull out the "world" coordinates of the shot
            shotx = (pos[0]-self.width/2)/self.starscale
            shoty = -(pos[1]-self.height/2)/self.starscale

            #the star has a built-in hit checker. def checkHit(xp, yp,spread,height=500,width=500):
            self.lastshottime,targhit = self.star.checkHit(shotx,shoty,1,self.height,self.width)
            if ((pos[0]-self.resetx)**2+(pos[1]-self.resety)**2)<=self.plateradius**2:
                self.star.reset(t2=0.5)
                self.activator_hit = 0
                self.activator_down=0
            
            if ((pos[0]-self.actx)**2+(pos[1]-self.acty)**2)<=self.actplateradius**2:
                #self.star.simulate=True
                #self.star.setstarttime()
                self.activator_hit = 1
                self.activator_hittime=time.time()
                #print "activator!!"
                

         #see if we quit.   
        if event.type == pygame.QUIT:
            self._running = False
    def on_loop(self):
        #how long has it been since the last loop?
        timenow = time.time()
        self.dt = timenow-self.oldtime
        self.oldtime = timenow
        
        #check to see if activator is hit/down
        if self.activator_hit is 1 and self.activator_down is 0:
            if (timenow-self.activator_hittime)>=self.activator_delay:
                self.activator_down = 1
                self.star.simulate=True
                self.star.setstarttime()
        
        #print self.dt
        #set the current time step
        self.star.dt = self.dt
        #update the star dynamics.
        self.star.updateDynamics(self.dt) #this will automatically star the sim once we set mass 4 to 0.
        #now update buffers for t1, t2 so that the cv system can use old angles to check hits.
        self.t1buf = append(self.t1buf[1:],self.star.t1)
        self.t2buf = append(self.t2buf[1:],self.star.t2)
        #black out the screen
        self._display_surf.fill((0,0,0))#clear the screen to redraw
        #self._display_surf.blit(self.background,self.bgrect)
        #draw the star
        self.draw_star()
        #draw the reset button
        if self.lasershotnow==True:
            pass
            #pygame.draw.circle(self._display_surf, green, (int(self.shotx),int(self.shoty)), self.plateradius, 5)

        #draw the activator popper
        if self.activator_hit is not 1:
            pygame.draw.circle(self._display_surf, grey, (self.actx,self.acty), self.actplateradius, 0)
            pygame.draw.rect(self._display_surf, grey, (self.actx-int(self.actplateradius/2),self.acty-2*self.actplateradius,self.actplateradius,self.actplateradius*6.0), 0)
            pygame.draw.circle(self._display_surf, grey, (self.actx,self.acty-2*self.actplateradius), int(self.actplateradius/2.), 0)
            p1=(self.width-self.actx,self.height-self.acty)
            L=20
            p2=(p1[0]-L*sin(pi/6.), p1[1]+L*cos(pi/6.))
            p3=(p1[0]+L*sin(pi/6.),p1[1]+L*cos(pi/6.)) 
            pygame.draw.polygon(self._display_surf,white,[p1,p2,p3])       #pygame.draw.rect(self._display_surf, grey, (self.actx-self.actplateradius*.4,self.acty,self.actplateradius,self.actplateradius*3.0), 0)
        #pygame.draw.rect(self._display_surf, grey, (self.actx-self.actplateradius*.4,self.acty-self.actplateradius,self.actplateradius*1.5,self.actplateradius*3.0), 0)
        #pygame.draw.circle(self._display_surf, grey, (self.actx,self.acty-self.actplateradius), int(self.actplateradius/2.0), 0)
        
        
        pygame.draw.circle(self._display_surf, grey, (self.resetx,self.resety), self.plateradius, 0)
        #now draw text for reset and time
        textreset = myfont.render('RESET',False,grey)
        self._display_surf.blit(textreset,(75,450))
        texttime = myfont.render('TIME: '+str(self.lastshottime)+' s',False,grey)
        self._display_surf.blit(texttime,(200,50))
        texttime = myfont.render('thresh: '+str(self.threshval),False,grey)
        self._display_surf.blit(texttime,(600,50))
        time.sleep(0.01)

        

        #print self.dt
        # if self.lasershotnow == True:
        #     #the star has a built-in hit checker. def checkHit(xp, yp,spread,height=500,width=500):
        #     self.lastshottime,targhit = self.star.checkHit(meanx,meany,1,self.height,self.width)
        #     if ((meanx-self.resetx)**2+(meany-self.resety)**2)<=self.plateradius**2:
        #         self.star.reset(t2=0.5)


        # if len(laserloc>0):
        #     print laserloc[0][0],laserloc[1][0]

        


    def on_render(self):
        pygame.display.update()


    def on_cleanup(self):
        pygame.quit()
 
    def on_execute(self):
        if self.on_init() == False:
            self._running = False
 
        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()
 
if __name__ == "__main__" :
    
    theApp = App()
    thread.start_new_thread(procvid,(theApp,))
    theApp.on_execute()
