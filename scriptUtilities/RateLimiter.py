# Implement a class that allows max N requests per user within a time window (in seconds)
class RateLimiter

  allRequests = {"user": [{data: {}, timestamp: "2025-04-10_170056"},...]}

  N = 10 # max N requests
  resetTime = 8000 # Time in seconds

  def processRequests(requestData, user):
  	# If request count < N, process requests
  	requestsProcessing = allRequests[user]

  	if(requestsProcessing < N):
  		# process request and await response
  		requestsProcessing.append({data: request, timestamp: DateTime.Now()})
  		response = process(request)
  		# Find and remove this request from requestsProcessing


  	else:
  		# If request count == N, add to separate queue/ignore
  		println("Hit request rate limit. New requests will be processed after {resetTime/1000} seconds")
  		currentTime = DateTime.Now()
  		# Set a process that will clean up requestsProcessing in currentTime + resetTime
  		await
  	   






    