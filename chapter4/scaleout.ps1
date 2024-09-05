#run command on admin PowerShell prompt is: .\scaleout.ps1
#set the load balancer url to the load balancer that is front ending your autoscaling group
$LoadBalancerURL=DjangoWebAppLoadBalancer-xxxxxxxx.us-east-1.elb.amazonaws.com
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
Set-Variable -Name "SLEEP_TIMER_SECONDS" -Value 3
Set-Variable -Name "LOOP" -Value 80
For ($counter=1; $counter -le $LOOP; $counter++) {
    'Call Count:' + $counter
    cURL $LoadBalancerURL
    'Going to sleep for ' + $SLEEP_TIMER_SECONDS + ' seconds'
    Start-Sleep -s $SLEEP_TIMER_SECONDS
}
echo '*******DONE*******'
