cd && mkdir chapter25 && cd chapter25
mkdir src
mkdir -p ~/chapter25/src/invokemodel_vs_converse
mkdir -p ~/chapter25/src/streaming_vs_nonstreaming
mkdir -p ~/chapter25/src/inference_params

wget -O ~/chapter25/25_1_BedrockAPI.json https://raw.githubusercontent.com/bpb-aws-book/bpb-aws-book/main/chapter25/25_1_BedrockAPI.json

wget -O ~/chapter25/src/invokemodel_vs_converse/lambda_function.py https://raw.githubusercontent.com/bpb-aws-book/bpb-aws-book/main/chapter25/src/invoke_vs_converse/lambda_function.py

wget -O ~/chapter25/src/streaming_vs_nonstreaming/lambda_function.py https://raw.githubusercontent.com/bpb-aws-book/bpb-aws-book/main/chapter25/src/streaming_vs_nonstreaming/lambda_function.py

wget -O ~/chapter25/src/inference_params/lambda_function.py https://raw.githubusercontent.com/bpb-aws-book/bpb-aws-book/main/chapter25/src/inference_params/lambda_function.py

sam deploy --template-file ~/chapter25/25_1_BedrockAPI.json --stack-name chapter25-stack-1 --capabilities CAPABILITY_IAM --resolve-s3
