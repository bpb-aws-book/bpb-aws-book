helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
-n kube-system \
--set clusterName=bpb-eks-cluster \
--set serviceAccount.create=true \
--set region=<YOUR REGION> \
--set vpcId=<YOUR VPC ID> \
--set serviceAccount.annotations."eks\.amazonaws\.com/role-arn"=arn:aws:iam::111111111111:role/<Your EKS Load Balancer Role>
