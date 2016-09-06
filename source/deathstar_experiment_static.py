#!/usr/bin/python
import pygame
from pygame.locals import *
from deathstarclass import DeathStar
from numpy import *
import cv2
import time
import thread

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import os

import datetime
now = datetime.datetime.now()
fname = 'Data/'+str(now.year)+'_'+str(now.month)+'_'+str(now.day)+'_'+str(now.hour)+'_'+str(now.minute)+'_'+str(now.second)+'.txt'

gmail_user = "deathstarsimulator@gmail.com"
gmail_pwd = "3gunstar"


capture = cv2.VideoCapture(0)
laserlocx,laserlocy = array([0]),array([0])


def mail(to, subject, text, attach):
   msg = MIMEMultipart()

   msg['From'] = gmail_user
   msg['To'] = to
   msg['Subject'] = subject

   msg.attach(MIMEText(text))

   part = MIMEBase('application', 'octet-stream')
   part.set_payload(open(attach, 'rb').read())
   Encoders.encode_base64(part)
   part.add_header('Content-Disposition',
           'attachment; filename="%s"' % os.path.basename(attach))
   msg.attach(part)

   mailServer = smtplib.SMTP("smtp.gmail.com", 587)
   mailServer.ehlo()
   mailServer.starttls()
   mailServer.ehlo()
   mailServer.login(gmail_user, gmail_pwd)
   mailServer.sendmail(gmail_user, to, msg.as_string())
   # Should be mailServer.quit(), but that crashes...
   mailServer.close()


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
                #feed these coords to the app for storage in file.
                app.shotx_starcoords,app.shoty_starcoords=shotxs,shotys

                #pygame.draw.circle(app._display_surf, green, (int(shotx),int(shoty)), app.plateradius, 5)
                #the star has a built-in hit checker. def checkHit(xp, yp,spread,height=500,width=500):
                app.lastshottime,app.targhit,app.targtried,app.mindist = app.star.checkHit_delayed(shotxs,shotys,2,app.t1buf[0],app.t2buf[0],app.height,app.width)
                #print app.lastshottime,targhit

                if ((meanx*app.scalex-app.resetx)**2+(meany*app.scaley-app.resety)**2)<=2*app.plateradius**2:      
                    app.star.reset(t2=0.5)
                    mail("deathstarsimulator@gmail.com",
                    app.fname,
                    app.fname,
                    app.fname)
                    app.f.close()
                    now = datetime.datetime.now()
                    app.fname = 'Data/'+str(now.year)+'_'+str(now.month)+'_'+str(now.day)+'_'+str(now.hour)+'_'+str(now.minute)+'_'+str(now.second)+'.txt'
                    app.f=open(app.fname,'wb')

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
        now = datetime.datetime.now()
        self.fname = 'Data/'+str(now.year)+'_'+str(now.month)+'_'+str(now.day)+'_'+str(now.hour)+'_'+str(now.minute)+'_'+str(now.second)+'.txt'
        self.f = open(self.fname,'wb')
        self.f.write('time theta_1  t1d theta_2 t2d xst yst x1 y1 x2 y2 x3 y3 x4 y4 x5 y5 shot actual_shot_time targ_hit targ_tried min_distance\n')

        self.lagtime = 0.2#lag of the video
        self.staticmode = True
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
        
        self.star = DeathStar(l1=0.89,l2=0.8,b1=1,b2=1,dt=self.dt,platemass=7.5,t2=.5,shotweight=0.001,Jst=3.51,mst=28.08)
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

        #the following are set by the CV thread and keep track of shots 
        self.shotx_starcoords = 0
        self.shoty_starcoords = 0
        self.targhit = 0
        self.targtried = 0
        self.mindist = 10000000

    def draw_star(self):
        

        #this is mostly taken from the death star class, but adapted for pygame. Can't think of a good way to work it in...
        
        hingex = self.width/2
        hingey = self.height/2
        #star position
        self.xst = -self.star.l2*cos(-self.star.t2)*self.starscale+hingex
        self.yst = -(self.star.l2*sin(-self.star.t2))*self.starscale+hingey
        #mass one
        self.x1 = self.xst+self.starscale*self.star.l1*sin(-self.star.t1)
        self.y1 = self.yst - self.starscale*self.star.l1*cos(-self.star.t1)
        #mass two
        self.x2 = self.xst+self.starscale*self.star.l1*sin(-self.star.t1-self.star.alpha)
        self.y2 = self.yst - self.starscale*self.star.l1*cos(-self.star.t1-self.star.alpha)
        #mass three
        self.x3 = self.xst+self.starscale*self.star.l1*sin(-self.star.t1-2*self.star.alpha)
        self.y3 = self.yst - self.starscale*self.star.l1*cos(-self.star.t1-2*self.star.alpha)
        #mass four
        self.x4 = self.xst+self.starscale*self.star.l1*sin(-self.star.t1-3*self.star.alpha)
        self.y4 = self.yst - self.starscale*self.star.l1*cos(-self.star.t1-3*self.star.alpha)
        #mass five
        self.x5 = self.xst+self.starscale*self.star.l1*sin(-self.star.t1-4*self.star.alpha)
        self.y5 = self.yst - self.starscale*self.star.l1*cos(-self.star.t1-4*self.star.alpha)

        pygame.draw.lines(self._display_surf, white, False, [(hingex,hingey), (self.xst,self.yst)], 3)
        pygame.draw.lines(self._display_surf, grey, False, [(self.xst,self.yst), (self.x1,self.y1)], 3)
        pygame.draw.lines(self._display_surf, grey, False, [(self.xst,self.yst), (self.x2,self.y2)], 3)
        pygame.draw.lines(self._display_surf, grey, False, [(self.xst,self.yst), (self.x3,self.y3)], 3)
        pygame.draw.lines(self._display_surf, red, False, [(self.xst,self.yst), (self.x4,self.y4)], 3)
        pygame.draw.lines(self._display_surf, grey, False, [(self.xst,self.yst), (self.x5,self.y5)], 3)




        #mass one ellipse
        if (self.star.m1>self.star.shotweight):
            pygame.draw.circle(self._display_surf, grey, (int(self.x1),int(self.y1)), self.plateradius, 0)

        #mass 2 ellipse
        if (self.star.m2>self.star.shotweight):
            pygame.draw.circle(self._display_surf, grey, (int(self.x2),int(self.y2)), self.plateradius, 0)

        #mass 3 ellipse
        if (self.star.m3>self.star.shotweight):
            pygame.draw.circle(self._display_surf, grey, (int(self.x3),int(self.y3)), self.plateradius, 0)

        
        #mass 4ellipse
        if (self.star.m4>self.star.shotweight):
            pygame.draw.circle(self._display_surf, red, (int(self.x4),int(self.y4)), self.plateradius, 0)

        #mass one ellipse
        if (self.star.m5>self.star.shotweight):
            pygame.draw.circle(self._display_surf, grey, (int(self.x5),int(self.y5)), self.plateradius, 0)
 
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
        if (event.type is KEYDOWN and event.key==K_s): #PRESSING THE S KEY TOGGLES STATIC MODE
            if self.staticmode == True:
                self.staticmode=False
            else:
                self.staticmode = True
        #let's look for hits based on mouse clicks!!
        if event.type == pygame.MOUSEBUTTONDOWN:
            #get the mouse position
            pos = pygame.mouse.get_pos()
            print pos[0],pos[1]
            #pull out the "world" coordinates of the shot
            shotx = (pos[0]-self.width/2)/self.starscale
            shoty = -(pos[1]-self.height/2)/self.starscale
            self.shotx,self.shoty = shotx,shoty
            #the star has a built-in hit checker. def checkHit(xp, yp,spread,height=500,width=500):
            self.lastshottime,targhit = self.star.checkHit(shotx,shoty,1,self.height,self.width)
            if ((pos[0]-self.resetx)**2+(pos[1]-self.resety)**2)<=self.plateradius**2:
                self.star.reset(t2=0.5)
                self.activator_hit = 0
                self.activator_down=0


            if ((pos[0]-self.actx)**2+(pos[1]-self.acty)**2)<=self.actplateradius**2:
                #self.star.simulate=True
                self.star.setstarttime()
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
        #updae the star dynamics.
        if self.staticmode==False:
            self.star.updateDynamics(self.dt) #this will automatically star the sim once we set mass 4 to 0.
        else:
            t1,t1d,t2,t2d = self.star.t1,self.star.t1d,self.star.t2,self.star.t2d
            self.star.updateDynamics(self.dt)
            self.star.t1,self.star.t1d,self.star.t2,self.star.t2d = t1,t1d,t2,t2d

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
            if self.star.simulate==True:
                    self.f.write(str(self.star.simtime)+'\t'+str(self.star.t1)+'\t'+str(self.star.t1d)+'\t'+str(self.star.t2)+'\t'+str(self.star.t2d)+'\t'+str(self.xst)+'\t'+str(self.yst)+'\t'+str(self.x1)+'\t'+str(self.y1)+'\t'+str(self.x2)+'\t'+str(self.y2)+'\t'+str(self.x3)+'\t'+str(self.y3)+'\t'+str(self.x4)+'\t'+str(self.y4)+'\t'+str(self.x5)+'\t'+str(self.y5)+'\t'+str(1)+'\t'+str(self.lastshottime-self.lagtime)+'\t'+str(self.targhit)+'\t'+str(self.targtried)+'\t'+str(self.mindist*self.starscale)+'\t'+str(self.shotx)+'\t'+str(self.shoty)+'\n')
        else:
            if self.star.simulate==True:
                    self.f.write(str(self.star.simtime)+'\t'+str(self.star.t1)+'\t'+str(self.star.t1d)+'\t'+str(self.star.t2)+'\t'+str(self.star.t2d)+'\t'+str(self.xst)+'\t'+str(self.yst)+'\t'+str(self.x1)+'\t'+str(self.y1)+'\t'+str(self.x2)+'\t'+str(self.y2)+'\t'+str(self.x3)+'\t'+str(self.y3)+'\t'+str(self.x4)+'\t'+str(self.y4)+'\t'+str(self.x5)+'\t'+str(self.y5)+'\t'+str(0)+'\t'+str(self.lastshottime-self.lagtime)+'\t'+str(self.targhit)+'\t'+str(self.targtried)+'\t'+str(self.mindist*self.starscale)+'\t'+str(self.shotx)+'\t'+str(self.shoty)+'\n')

         #draw the activator popper
        if self.activator_hit is not 1:
            pygame.draw.circle(self._display_surf, grey, (self.actx,self.acty), self.actplateradius, 0)
            pygame.draw.rect(self._display_surf, grey, (self.actx-int(self.actplateradius/2),self.acty-2*self.actplateradius,self.actplateradius,self.actplateradius*6.0), 0)
            pygame.draw.circle(self._display_surf, grey, (self.actx,self.acty-2*self.actplateradius), int(self.actplateradius/2.), 0)
        #pygame.draw.rect(self._display_surf, grey, (self.actx-self.actplateradius*.4,self.acty,self.actplateradius,self.actplateradius*3.0), 0)
        #pygame.draw.rect(self._display_surf, grey, (self.actx-self.actplateradius*.4,self.acty-self.actplateradius,self.actplateradius*1.5,self.actplateradius*3.0), 0)
        #pygame.draw.circle(self._display_surf, grey, (self.actx,self.acty-self.actplateradius), int(self.actplateradius/2.0), 0)
        
        
            #pygame.draw.circle(self._display_surf, green, (int(self.shotx),int(self.shoty)), self.plateradius, 5)

        pygame.draw.circle(self._display_surf, grey, (self.resetx,self.resety), self.plateradius, 0)
        
        pygame.draw.circle(self._display_surf, white, (0,0), 10, 0)
        pygame.draw.circle(self._display_surf, white, (self.width,0), 10, 0)
        pygame.draw.circle(self._display_surf, white, (self.width,self.height), 10, 0)
        pygame.draw.circle(self._display_surf, white, (0,self.height), 10, 0)

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