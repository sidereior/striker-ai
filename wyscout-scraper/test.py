import pdfplumber
import re
import json
import time

def main():

	#reportName='Boston College Eagles - Syracuse Orange 1-1.pdf'
	#reportName='Clemson Tigers - Boston College Eagles 6-0.pdf' 
	#reportName='Duke Blue Devils - Boston College Eagles 3-2.pdf'
	reportName='Mount St. Mary\'s Mountaineers - Niagara Purple Eagles 0-0.pdf'
	#reportName='Stanford Cardinal - South Carolina Gamecocks 3-0.pdf'
	#reportName='ECNL East U15 - ECNL West U15 3-5.pdf'

	#teamName='Boston College Eagles'  # This name must appear EXACTLY as it does on the WyScout report
	teamName='Mount St. Mary\'s Mountaineers'
	#teamName='South Carolina Gamecocks'
	#teamName='ECNL East U15'


	#### Hard coded front matter.  Need to know ahead of time which categories are in the tables and how many metrics are stored per column
	## metricNames: our naming convention for what to call each of the metrics in the WyScout table
	## args: some columns in WyScout actually contain 2 metrics, some contain 1.  We need to specify that.
	## Note as a check, sum(args) should be equal to the corresponding number of elements in "metricNames"

	metricNames=[["Min. played","Goals","xG","Assists","xA","Actions","Shots","Passes","Crosses","Dribbles","Duels","Losses","Losses (own half)","Recoveries",
	"Recoveries (opp. half)","Touches (Pen. area)","Offsides","Yellow","Red"],
	["Min. played","Def. Duels","Off. Duels","Aerial Duels","Loose ball duels","Shots blocked","Interceptions","Clearances","Slide tackles",
	"Fouls","Fouls suffered","Free kicks","Direct kicks","Corners","Throw-ins"],
	["Min. played","Forward passes","Back passes","Lateral passes","Short-med passes","Long passes","Prog. passes","Passes final 3rd",
	"Through passes","Deep completions","Key passes","Second assists","Third assists","Shot assists","Avg. pass length"]]

	args=[[1,2,2,1,1,1,1,1,1,2,2,1,1,2],[1,1,1,1,1,1,2,1,2,1,1,1,1],[1,1,1,1,1,1,1,1,1,1,1,2,1,1]]

	#### The goalie tables are an entirely different matter.
	## goalieMetrics:  our naming convention for what to call each of the metrics in the WyScout goalie tables
	## kindOfMetric: need to know whether to treat it as a percent (pct) or a count (cnt) of a particular quantity
	## Note as a check, these arrays should be equal in size
	goalieMetrics=["Passes (tot.)","Passes (1rst)","Passes (2nd)","Saves (tot.)","Saves (1rst)","Saves (2nd)",
	"Passes beyond back 3rd (tot.)","Passes beyond back 3rd (1rst)","Passes beyond back 3rd (2nd)","Reflex saves (tot.)","Reflex saves (1rst)","Reflex saves (2nd)",
	"Back passes to GK (tot.)","Back passes to GK (1rst)","Back passes to GK (2nd)","Conceded penalties (tot)","Conceded penalties (1rst)","Conceded penalties (2nd)",
	"Shots against (tot)","Shots against (1rst)","Shots against (2nd)","Aerial Duels (tot.)","Aerial Duels (1rst.)","Aerial Duels (2nd.)",
	"Conceded goals (tot.)","Conceded goals (1rst)","Conceded goals (2nd)","Exits (tot.)","Exits (1rst)","Exits (2nd)"]

	kindOfMetric=['pct','pct','pct','cnt','cnt','cnt','pct','pct','pct','cnt','cnt','cnt','cnt','cnt','cnt','pct','pct','pct','cnt','cnt','cnt','pct',
	'pct','pct','cnt','cnt','cnt','cnt','cnt','cnt']

	# Here are the checks
	elementsPerTable1=list(map(sum,args));
	elementsPerTable2=list(map(len,metricNames));
	if(elementsPerTable1!=elementsPerTable2):
		print("number metric names provided is incompatible with number of metrics given in the tables, exiting ...")
		exit(0)
	if(len(goalieMetrics)!=len(kindOfMetric)):
		print("number of goalie metrics must match the corresponding metric type")
		exit(0)

	#############  End hard coded front matter #############
	# The formatting above should work for any WyScout report formatted like the ones I've looked at so far.  Hopefully its uniform formatting for all reports

	tic=time.time()
	# Open the report
	print("Opening report ...")
	pdf=pdfplumber.open(reportName)
	numPages=len(pdf.pages)
	#print(pdf.metadata)    # Use this to access metadata, but nothing useful seems to be here

	########### Get the competing team names from the second to last page of the report #######################
	print("Getting team names ...")
	page=pdf.pages[numPages-2]
	text=page.extract_text().split("\n")
	twoTeams=[]
	for i in range(len(text)):
		if "Player" in text[i]:   # Team names appear to be stored in element prior to word "Player"
			twoTeams.append(text[i-1])
	print("The two teams in this report are ",twoTeams)

	# Now store the starting lineup for later use (we'll use it to get goalie names)
	page=pdf.pages[1]
	strtLineup=page.extract_text().split("\n")

	if 0:  # Alternative, but more costly, way to get team names
		# Step 1
		twoTeams=[]			# Holds the 2 possible team names
		cnt=0
		for i in range(numPages):	# Scan through the report and figure out what the two possible team names are
			page=pdf.pages[i]
			text=page.extract_text().split("\n")
			if text[1]=='MATCH REPORT' and text[2]=='PASSES':
				twoTeams.append(text[0])
				cnt=cnt+1
				if(cnt==2):
					break
	# Step 2 
	#ros=getTeamRoster(pdf,twoTeams)

	#statLinkMatch=1
	#if statLinkMatch==1:
	#	teamName=twoTeams[0]
	#else:
	#	teamName=twoTeams[1]
	#print("teamName is now ",teamName)
	
	#### Main code where we extract the report data and package it in JSON format ####
	# Define our JSON response to send to the back-end.
	res = {
		"reportName": [],
		"team": teamName,
		"date": [],
		"players": [],
	}
	res["reportName"]=pdf.stream.name  # Returns the filename that was opened.  This matches reportName above

###################### This section pulls the raw data we'll need to get both the goalie and player data

	tableData=[]		# Will hold player table data
	playerPages=[]		# Will hold pages containing player information
	goaliePages=[]		# Will hold pages containing the goalie information
	lastImgs=0
	print("Gathering key pages of report ...")
	for i in range(numPages):	# Scan through the report and find all the pages with the data we want.  Concatenate together

		page=pdf.pages[i]
		if len(page.images)==2 and lastImgs==3:	# Ignore all pages after the transition from page.images==3 to page.images==2.  This signfies end of useful report info.
			break	# Using this check prevents us from needing to extract text from ALL the pages, we can break out of loop early
		else:
			lastImgs=len(page.images)
			
		text=page.extract_text().split("\n")  # break text from page into lines

		if(i==1):	# Read off the match date from the first page of the report (not the cover page though)
			matchDate = re.findall(r'\d{2}.\d{2}.\d{4}',text[0])[0]
			res["date"]=matchDate

		# The line below seems sufficient to filter out the pages with only the data tables corresponding to the team we're working with (specified in teamName)
		if(text[0]==teamName and text[2]!='SHOTS' and text[2]!='PASSES'):	# Tables appear on pages where the first line contains nothing but the team name.  Good indicator to key on.
			playerPages.append(i)
			tableData=tableData+text	# This should be a big list of all the data on WyScout tables for the team "teamName"

		if text[2]=='GOALKEEPER IN MATCH':  # Goalie data appears on pages where GOALKEEPER IN MATCH is stored in text[2]
			goaliePages.append(i)

##################### That's it for core data extraction (expensive) - now we process (cheap) #################

	print("Processing the goalie data ...")
	# Goalie pages appear directly after last playerPage and are consecutive.  Use this fact to remove other teams' goalie(s)
	lastPage=playerPages[-1]
	goaliePages = [k for k in goaliePages if k >= lastPage]  # Goalie data always appears AFTER team data so we can remove any goalie appearing prior to our team pages  
	for i in range(len(goaliePages)):  # This piece handles case where other team appears after ours in the report
		if goaliePages[i]-lastPage == 1:
			lastPage=goaliePages[i]
		else:
			goaliePages.pop(i)  # Remove other teams' goalie from consideration

	#### Now process the goalie metrics #########
	#print("Processing pages ",goaliePages," for goalie data")
	for i in range(len(goaliePages)):  # for each goalie in the game ...
		newPlayer = {        # Create an empty player
			"name": None,
			"number": None,
			"metrics": [],
		}
		page=pdf.pages[goaliePages[i]]
		text=page.extract_text().split("\n")
		pName=text[0]
		# Now identify the goalie number using the starting lineup page we extracted earlier
		gkMatch = [k for k in strtLineup if pName in k]
		mstr='(\d+) ?'+pName  # searching for player number followed by player name with (optionally) a space between them
		result=re.findall(mstr,gkMatch[0])
		if len(result)>0:	# If we successfully found a number, otherwise don't report this field  
			pNum=int(result[0]) # We are interested in the integer value of the goalie number
			newPlayer["number"]=pNum
			
		newPlayer["name"]=pName
	
		for strt in range(len(text)):
			if text[strt].find('Passes / accurate')!= -1:  # Key on the text line that starts with the metric "Passes / accurate"
				break;  # This sets "strt" to beginning of range we want to scan
	
		mtrCtr=0
		for j in range(strt,strt+round(len(goalieMetrics)/3/2)):  # 3 numbers per metric (total, 1rst, 2nd) and 2 metrics per row of text, hence the /3 and /2 factors
			result=re.findall(r'\d+[/]?[%]?',text[j])
			result=text[j].split(' ')
			for x in result:
				if x[0].isdigit():  # It's a metric
					# Define the JSON of a metric to add to the "newPlayer".
					newMetric = {
						"name": goalieMetrics[mtrCtr],
						"total": None,
						"good": None,
					}
				
					if(kindOfMetric[mtrCtr]=='pct'):		# if the metric is given as a percent
						fracString=re.findall(r'\d+',x)
						if(int(fracString[0])==0):   # Probably the 0/0 case ...
							if(len(fracString)>1):   
								if(int(fracString[1])==0):  # the 0/0 case
									metricGood='NA'
									metricBad='NA'	
								else:			# but just in case its something like 0/1
									metricGood=int(fracString[1])
									metricBad=0
							else:  # The case where it is just a single "0"
								metricGood='NA'
								metricBad='NA'
						else:
							if(len(fracString[1])==2):	# Single digit percentage case
								metricGood=int(fracString[1][0])
								metricBad=int(fracString[0])-metricGood
							elif(int(fracString[1][-3:])==100):  # Handles 100% case
								metricGood=int(fracString[0])
								metricBad=0
							else:	# Handles tens of percent case
								metricGood=int(fracString[1][0:-2])
								metricBad=int(fracString[0])-metricGood
					
						mtrCtr=mtrCtr+1
						newMetric['total'] = metricBad
						newMetric['good'] = metricGood

					elif(kindOfMetric[mtrCtr]=='cnt'):  # If metric is a "count".  Note WyScout doesn't differentiate between 0 and 'NA' in the counter case !
						metricValue=int(x)
						mtrCtr=mtrCtr+1
						newMetric['total'] = metricValue
					else:  # default assumption is NA
						newMetric['total']='NA'
						newMetric['good']='NA'
					
					# Only add a new metric for a player if there is data.
					if (newMetric['total']!=None) and (newMetric['total'] != "NA"):
						newPlayer['metrics'].append(newMetric)	
					
		if len(newPlayer['metrics']) > 0:
			res['players'].append(newPlayer)					
			
	#### Done processing the goalies and stored data in our "res" dictionary
	print("Now processing field player data ...")	
	#### We've isolated the data we care about in "tableData".  Now scan through it	
	whichTable=-1	# Need to indicate which of the 3 tables we're using to match with "metricNames" and "args" specified above.  
	# Implicit assumption is these 3 tables always appear sequential in the document
	for i in range(len(tableData)):   # Go line by line i.e., player by player
		if(tableData[i][0:6]=='Player'):  # The text "Player" serves as a useful indicator that we've hit a table
			whichTable=whichTable+1

		if(tableData[i][0].isdigit() and len(tableData[i])>2):  # See if start of line is a number (and not just page #).  This should signify player data
			plyrText=tableData[i].split()
			# Define the structure to hold player data for the current row.
			newPlayer = {
				"name": None,
				"number": None,
				"metrics": [],
			}
		
			pNum=plyrText[0]	# Player number is first element in line
			pName=plyrText[1]  	# first of possibly several pieces of the player name
			for j in range(2,len(tableData[i])):  # This cycles until we get the entire player name
				if(re.search('[a-zA-Z]',plyrText[j])):  # both these ways seem to work - which is more robust?
	#			if(plyrText[j][0].isalpha()):
					pName=pName+' '+plyrText[j]
				else:
					break

			# Populate known player information.
			newPlayer['name'] = pName
			newPlayer['number'] = pNum
		
			# The rest of the line is comprised of different data types/formats.  Try to recognize and then extract these below
			mtrCtr=0  # counts through number of metrics in the table.  when finished it should match sum(args) for each table
			for k in range(j,len(plyrText)):  # each element in plyrText is a metric we need to extract

				# Define the JSON of a metric to add to the "newPlayer".
				newMetric = {
					"name": metricNames[whichTable][mtrCtr],
					"total": None,
					"good": None,
				}
			
				# Define a second metric if needed
				if(args[whichTable][k-j]==2):
					newMetric2 = {
						"name": metricNames[whichTable][mtrCtr+1],
						"total": None,
						"good": None,
					}
			
				slashLoc=(plyrText[k]).find('/')  # Need to know where the "slash" is in the metric text string to properly parse
				if(plyrText[k]=='-'):  # This handles the case where the players received no data, just a '-' which for us means 'NA'
					if(args[whichTable][k-j]==2):
						#print('Metric name s',metricNames[whichTable][mtrCtr],' and ',metricNames[whichTable][mtrCtr+1], 'are empty')
						metricValue1='NA'
						metricValue2='NA'

						mtrCtr=mtrCtr+2 # increment for 2 metrics		
					
						newMetric['total'] = metricValue1
						newMetric['good'] = metricValue2
					
					else:
						#print('Metric name ',metricNames[whichTable][mtrCtr],'is empty')
						metricValue='NA'

						mtrCtr=mtrCtr+1
						newMetric['total'] = metricValue
					
				elif(slashLoc== -1):  # If there's no / in the text, just recorde it as a real-valued metric
					metricValue=re.findall(r'\d+\.?\d*',plyrText[k])[0]
				
					if(plyrText[k].find('.')==-1):
						newMetric['total']=int(metricValue)
					else:
						newMetric['total']=float(metricValue) # If there's a decimal, it's a float
					
					if whichTable>0 and metricNames[whichTable][mtrCtr]=='Min. played':  # Since min. played is a repeated quantity, only keep the whichTable=0 instance
						newMetric['total']=None

					mtrCtr=mtrCtr+1
				
				elif(plyrText[k].find('%')==-1):  # If there's no percent sign just process as two separate metrics
					metricText=plyrText[k].split('/')
					metricValue1=int(metricText[0])   # First one always seems to be integer
				
					mtrCtr=mtrCtr+1
					if(plyrText[k].find('.')==-1):
						metricValue2=int(metricText[1])
					else:
						metricValue2=float(metricText[1]) # If there's a decimal, it's a float
					
					mtrCtr=mtrCtr+1
					newMetric['total'] = metricValue1
					newMetric2['total'] = metricValue2

				else:  # If there's no slash but there is a percentage, must be a two outcome data type
					fracString=re.findall(r'\d+',plyrText[k])
					if(len(fracString[1])==2):	# Single digit percentage case
						metricGood=int(fracString[1][0])
						metricBad=int(fracString[0])-metricGood
					elif(int(fracString[1][-3:])==100):  # Handles 100% case
						metricGood=int(fracString[0])
						metricBad=0
					else:	# Handles tens of percent case
						metricGood=int(fracString[1][0:-2])
						metricBad=int(fracString[0])-metricGood
						
					mtrCtr=mtrCtr+1
					newMetric['total'] = metricBad
					newMetric['good'] = metricGood
				
				# Only add a new metric for a player if there is data.
				if (newMetric['total']!=None) and (newMetric['total'] != "NA"):
					newPlayer['metrics'].append(newMetric)
				if(args[whichTable][k-j]==2):
					if (newMetric2['total'] != None) and (newMetric2['total'] != "NA"):
						newPlayer['metrics'].append(newMetric2)

									
		
			# Only add a new player if they have data in their row.
			if len(newPlayer['metrics']) > 0:
				res['players'].append(newPlayer)					
			
	# Print our results!
	#print(res)

	# Create a string so I can save it to a file.
	res = json.dumps(res)

	# Store the JSON result into pleaseWork.json.

	print("Writing data to file ... ")
	with open("pleaseWork.json", "w") as outfile:
		outfile.write(res)
	toc=time.time()
	print("Done, elapsed time = ",toc-tic," seconds")

def getTeamRoster(pdf,twoTeams):


	numPages=len(pdf.pages)
	tableData=[]		# Will hold player table data
	playerPages=[]
	for i in range(numPages):	# Scan through the report and find all the pages with the data we want.  Concatenate together
		page=pdf.pages[i]
		text=page.extract_text().split("\n")
		
		# The line below seems sufficient to filter out the pages with only the data tables corresponding to the team we're working with (specified in teamName)
		if(text[0]==twoTeams[0] and text[2]!='SHOTS' and text[2]!='PASSES'):	# Tables appear on pages where the first line contains nothing but the team name.  Good indicator to key on.
			playerPages.append(i)
			tableData=tableData+text	# This should be a big list of all the data on WyScout tables for the team "teamName"
			break	# in this routine, once we get one teams' data we can break out of the loop

	# This will hold list of players
	playerList={
		"players": [],
	}
	whichTable=-1	# Need to indicate which of the 3 tables we're using to match with "metricNames" and "args" specified above.  
	# Implicit assumption is these 3 tables always appear sequential in the document
	for i in range(len(tableData)):   # Go line by line i.e., player by player
		if(tableData[i][0:6]=='Player'):  # The text "Player" serves as a useful indicator that we've hit a table
			whichTable=whichTable+1

		if(tableData[i][0].isdigit() and len(tableData[i])>2):  # See if start of line is a number (and not just page #).  This should signify player data
			plyrText=tableData[i].split()
			# Define the structure to hold player data for the current row.
			newPlayer = {
				"name": None,
				"number": None,
			}
		
			pNum=plyrText[0]	# Player number is first element in line
			pName=plyrText[1]  	# first of possibly several pieces of the player name
			for j in range(2,len(tableData[i])):  # This cycles until we get the entire player name
				if(re.search('[a-zA-Z]',plyrText[j])):  # both these ways seem to work - which is more robust?
#			if(plyrText[j][0].isalpha()):
					pName=pName+' '+plyrText[j]
				else:
					break

		# Populate known player information.
			newPlayer['name'] = pName
			newPlayer['number'] = pNum

			if len(newPlayer['name']) > 0:
				playerList['players'].append(newPlayer)	

	return playerList
# If this playerList matches the statLink roster, set teamN
if __name__=="__main__":
	main()