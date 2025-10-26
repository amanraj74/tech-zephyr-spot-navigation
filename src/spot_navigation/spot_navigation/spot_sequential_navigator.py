#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
import math, time
from enum import Enum

class State(Enum):
    SEEKING=1; AVOIDING=2; STUCK=3; COMPLETE=4

class Navigator(Node):
    def __init__(self):
        super().__init__('spot_navigator')
        self.waypoints=[{'n':'A','x':-3.5,'y':-0.5},{'n':'B','x':0.0,'y':-3.5},
                       {'n':'C','x':3.5,'y':0.5},{'n':'D','x':0.0,'y':1.5}]
        self.wp_idx=0; self.wp=self.waypoints[0]
        # SUPER FAST SPEEDS!
        self.safe,self.warn,self.tol,self.max_s,self.min_s,self.ang=0.6,1.2,0.35,1.5,0.25,1.5
        self.state=State.SEEKING; self.pos={'x':0.0,'y':0.0,'t':0.0}
        self.front=self.left=self.right=float('inf')
        self.last_t=time.time(); self.last_p={'x':0.0,'y':0.0}
        self.cmd_pub=self.create_publisher(Twist,'/cmd_vel',10)
        self.create_subscription(LaserScan,'/scan',self.scan_cb,10)
        self.create_subscription(Odometry,'/odom',self.odom_cb,10)
        self.create_timer(0.05,self.control)
        self.get_logger().info('='*60)
        self.get_logger().info('🚀 FAST MODE - TECH ZEPHYR 2025')
        self.get_logger().info('Team DeepLearners | Aman Jaiswal')
        self.get_logger().info('='*60)
    
    def scan_cb(self,msg):
        r,n=msg.ranges,len(msg.ranges)
        def gm(s,e): return min([x for x in r[s:e] if not math.isnan(x) and not math.isinf(x) and x>0.1],default=float('inf'))
        self.front,self.left,self.right=gm(int(n*0.45),int(n*0.55)),gm(int(n*0.2),int(n*0.35)),gm(int(n*0.65),int(n*0.8))
    
    def odom_cb(self,msg):
        self.pos['x'],self.pos['y']=msg.pose.pose.position.x,msg.pose.pose.position.y
        q=msg.pose.pose.orientation; self.pos['t']=math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y**2+q.z**2))
    
    def get_dist(self): return math.sqrt((self.wp['x']-self.pos['x'])**2+(self.wp['y']-self.pos['y'])**2)
    
    def get_angle(self):
        e=math.atan2(self.wp['y']-self.pos['y'],self.wp['x']-self.pos['x'])-self.pos['t']
        while e>math.pi: e-=2*math.pi
        while e<-math.pi: e+=2*math.pi
        return e
    
    def stuck(self):
        n=time.time()
        if n-self.last_t>=1.5:
            m=math.sqrt((self.pos['x']-self.last_p['x'])**2+(self.pos['y']-self.last_p['y'])**2)
            self.last_t,self.last_p=n,self.pos.copy(); return m<0.05
        return False
    
    def next_wp(self):
        self.get_logger().info('='*60)
        self.get_logger().info(f'✓ WAYPOINT {self.wp["n"]} REACHED!')
        self.wp_idx+=1
        if self.wp_idx>=len(self.waypoints):
            self.state=State.COMPLETE
            self.get_logger().info('🏆 MISSION COMPLETE!')
            self.get_logger().info('='*60)
        else:
            self.wp=self.waypoints[self.wp_idx]; self.state=State.SEEKING
            self.get_logger().info(f'→ Next: {self.wp["n"]}')
            self.get_logger().info('='*60)
    
    def control(self):
        if self.pos['x']==0.0: return
        cmd,d,a=Twist(),self.get_dist(),self.get_angle()
        if d<self.tol: self.next_wp(); return
        if self.front<self.safe: self.state=State.AVOIDING
        elif self.stuck(): self.state=State.STUCK
        elif self.state==State.AVOIDING and self.front>self.warn: self.state=State.SEEKING
        
        if self.state==State.SEEKING:
            s=self.min_s+(self.front-self.safe)*(self.max_s-self.min_s)/(self.warn-self.safe) if self.front<self.warn else self.max_s
            cmd.linear.x,cmd.angular.z=s,max(-self.ang,min(self.ang,3.5*a))
        elif self.state==State.AVOIDING:
            cmd.linear.x,cmd.angular.z=0.2,self.ang if self.left>self.right else -self.ang
        elif self.state==State.STUCK:
            cmd.linear.x,cmd.angular.z=-0.3,1.0; time.sleep(1.0); self.state=State.SEEKING
        elif self.state==State.COMPLETE:
            cmd.linear.x,cmd.angular.z=0.0,0.0; self.cmd_pub.publish(cmd); return
        
        self.cmd_pub.publish(cmd)

def main(): rclpy.init(); n=Navigator(); rclpy.spin(n); rclpy.shutdown()
if __name__=='__main__': main()
