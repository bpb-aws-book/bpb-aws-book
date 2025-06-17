# Run 5 invocations to cause throttling (since concurrency is set to 4)
for i in {1..5}; do
  aws lambda invoke \
    --function-name test \
    --invocation-type Event \
    --payload '{}' \
    output$i.txt &
done
