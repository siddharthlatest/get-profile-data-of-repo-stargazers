### Script to get GitHub profile data of all Stargazers of a given GitHub repository 
###
###	by Max Woolf (@minimaxir)

import json
import csv
import urllib2
import datetime
import time
import sys

repo="appbaseio/dejavu"
access_token="ce4d75e5bf40abeb7c5aea44379b67f58c26e0ca"

if len(sys.argv) < 2 or len(sys.argv) > 3:
	print("Usage: python repo_stargazers.py user/repo [access_token]")
elif len(sys.argv) == 2:
	repo = sys.argv[1]
else:
	repo = sys.argv[1]
	access_token = sys.argv[2]

fields = ["firstname", "lastname", "company", "email", "num_followers", "num_repos", "created_at","star_time"]
page_number = 0
users_processed = 0
stars_remaining = True
list_stars = []

print "Gathering Stargazers for %s..." % repo

###
###	This block of code creates a list of tuples in the form of (username, star_time)
###	for the Statgazers, which will laterbe used to extract full GitHub profile data
###

while stars_remaining:
	query_url = "https://api.github.com/repos/%s/stargazers?page=%s&access_token=%s" % (repo, page_number, access_token)
	
	req = urllib2.Request(query_url)
	req.add_header('Accept', 'application/vnd.github.v3.star+json')
	response = urllib2.urlopen(req)
	data = json.loads(response.read())
	
	for user in data:
		username = user['user']['login']
		
		star_time = datetime.datetime.strptime(user['starred_at'],'%Y-%m-%dT%H:%M:%SZ')
		star_time = star_time + datetime.timedelta(hours=-5) # EST
		star_time = star_time.strftime('%Y-%m-%d %H:%M:%S')
		
		list_stars.append((username, star_time))
		
	if len(data) < 25:
		stars_remaining = False
	
	page_number += 1

print "Done Gathering Stargazers for %s!" % repo

list_stars = list(set(list_stars)) # remove dupes

print "Now Gathering Stargazers' GitHub Profiles..."

###
###	This block of code extracts the full profile data of the given Stargazer
###	and writes to CSV
###
		
with open('%s-stargazers.csv' % repo.split('/')[1], 'w') as stars:

	stars_writer = csv.writer(stars)
	stars_writer.writerow(fields)
	
	for user in list_stars:
		username = user[0]
	
		query_url = "https://api.github.com/users/%s?access_token=%s" % (username, access_token)
	
		req = urllib2.Request(query_url)
		response = urllib2.urlopen(req)
		data = json.loads(response.read())

		name = data['name'] or ""
		firstname = name.split(" ")[0]
		lastname = " ".join(name.split(" ")[1:])
		if firstname is not None:
			firstname = firstname.encode('utf-8')
		if lastname is not None:
			lastname = lastname.encode('utf-8')
		company = data['company']
		if company is not None:
			company = company.encode('utf-8')
		email = data['email']
		num_followers = data['followers']
		num_repos = data['public_repos']
		
		created_at = datetime.datetime.strptime(data['created_at'],'%Y-%m-%dT%H:%M:%SZ')
		created_at = created_at + datetime.timedelta(hours=-5) # EST
		created_at = created_at.strftime('%Y-%m-%d %H:%M:%S')
		
		if email is not None:
			stars_writer.writerow([firstname, lastname, company, email, num_followers, num_repos, created_at, user[1]])
		
		users_processed += 1
		
		if users_processed % 100 == 0:
			print "%s Users Processed: %s, Page Number: %s" % (users_processed, datetime.datetime.now(), page_number)
			
		time.sleep(1) # stay within API rate limit of 5000 requests / hour + buffer
