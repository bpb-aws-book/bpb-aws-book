#!
#run command is: sh scaleout.sh
#set the load balancer url to the load balancer that is front ending your autoscaling group
loadbalancer_url=DjangoWebAppLoadBalancer-xxxxxxxx.us-east-1.elb.amazonaws.com
#need to exceed ALBRequestCountPerTarget value of 15 in 3 consecutive periods of one minute each
#The autoscaling group will have one instance begin with and this means one target
#if we make 16 calls each minute for 3 minutes, we will trigger the scale out event
#Learnt through a bit of experimentation that if we make 80 calls about 3 seconds apart,
#we make about 17 calls per minute, which is the ALBRequestCountPerTarget value > 15
#making 80 invocations will continue to invoke the load balancer URL for about 5 minutes
#which will trigger the scale out event
#if the script does not trigger the scale out event, then lower sleep time (SLEEP_TIMER_SECONDS)
#run this script on a Mac or Linux machine which has access to the website (your IP address specified
#in the CloudFormation template)
SLEEP_TIMER_SECONDS=3
LOOPS=80
for ((counter=1; counter<=$LOOPS; counter++))
    do 
        echo "Call Count: "$counter""; 
        curl $loadbalancer_url;
        echo "sleeping for "$SLEEP_TIMER_SECONDS" seconds";
        #sleep for 3 seconds
        sleep $SLEEP_TIMER_SECONDS 
    done  
echo "*******DONE*******"›
