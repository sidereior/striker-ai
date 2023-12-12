#import pdfquery
import pdfplumber
import re

#### Hard coded front matter.  Need to know ahead of time which categories are in the tables and how many metrics are stored per column
## metricNames: our naming convention for what to call each of the metrics in the WyScout table
## args: some columns in WyScout actually contain 2 metrics, some contain 1.  We need to specify that.
## Note as a check, sum(args) should be equal to the corresponding number of elements in "metricNames"
metricNames=[["Min. played","Goals","xG","Assists","xA","Actions","Shots","Passes","Crosses","Dribbles","Duels","Losses","Losses (own)","Recoveries",
"Recoveries (opp.)","Touches (PA)","Offsides","Yellow","Red"],
["Min. played","Def. Duels","Off Duels","Aerial Duels","Loose ball duels","shots blocked","Interceptions","Clearances","Slide tackles",
"Fouls","Fouls suffered","Free kicks","Direct free kicks","Corners","Throw-ins"],
["Min. played","Forward passes","Back passes","Lateral passes","Short-med passes","Long passes","Prog. passes","Passes final 3rd",
"Through passes","Deep completions","Key passes","Second assists","Third assists","Shot assists","Avg. pass length"]]
args=[[1,2,2,1,1,1,1,1,1,2,2,1,1,2],[1,1,1,1,1,1,2,1,2,1,1,1,1],[1,1,1,1,1,1,1,1,1,1,1,2,1,1]]

# Here is the check on number of metrics and args per column
elementsPerTable1=list(map(sum,args));
elementsPerTable2=list(map(len,metricNames));
if(elementsPerTable1!=elementsPerTable2):
	print("number metric names provided is incompatible with number of metrics given in the tables, exiting ...")
	exit(0)

# The formatting above should work for any WyScout report formatted like the ones I've looked at so far.  Hopefully its uniform formatting for all reports
# Here are a couple example reports for Boston College.  Note that the tables appear on different pages of the reports, but the code can handle

#reportName='Boston College Eagles - Syracuse Orange 1-1.pdf'
#reportName='Clemson Tigers - Boston College Eagles 6-0.pdf' 
reportName='test.pdf'

teamName='Boston College Eagles'  # This name must appear EXACTLY as it does on the WyScout report

# Open the report
pdf=pdfplumber.open(reportName)
numPages=len(pdf.pages)

tableData=[]
for i in range(numPages):	# Scan through the report and find all the pages with the data we want.  Concatenate together
	page=pdf.pages[i]
	text=page.extract_text().split("\n")

	# The line below seems sufficient to filter out the pages with only the data tables corresponding to the team we're working with (specified in teamName)
	if(text[0]==teamName and text[2]!='SHOTS' and text[2]!='PASSES'):	# Tables appear on pages where the first line contains nothing but the team name.  Good indicator to key on.
		print("Using page ",i)
		tableData=tableData+text	# This should be a big list of all the data on WyScout tables for the team "teamName"
		
whichTable=-1	# Need to indicate which of the 3 tables we're using to match with "metricNames" and "args" specified above.  
# Implicit assumption is these 3 tables always appear sequential in the document
for i in range(len(tableData)):   # Go line by line i.e., player by player
	if(tableData[i][0:6]=='Player'):
		print("Found word player on line ",i)
		whichTable=whichTable+1


	if(tableData[i][0].isdigit() and len(tableData[i])>2):  # See if start of line is a number (and not just page #).  This should signify player data
		plyrText=tableData[i].split()
		print(plyrText)  # print out the line we're processing
		exit(0)
		plyrJson='{'  # Initialize the json string
		pNum=plyrText[0]	# Player number is first element in line
		pName=plyrText[1]  	# first of possibly several pieces of the player name
		for j in range(2,len(tableData[i])):  # This cycles until we get the entire player name
			if(re.search('[a-zA-Z]',plyrText[j])):  # both these ways seem to work - which is more robust?
#			if(plyrText[j][0].isalpha()):
				pName=pName+' '+plyrText[j]
			else:
				break
		#print("Player name is ",pName)
		plyrJson=plyrJson+'player: '+pName+' metrics: [\n{\n'
		
		# The rest of the line is comprised of different data types/formats.  Try to recognize and then extract these below
		mtrCtr=0  # counts through number of metrics in the table.  when finished it should match sum(args) for each table
		for k in range(j,len(plyrText)):
#			print(plyrText[k])
			slashLoc=(plyrText[k]).find('/')
			if(plyrText[k]=='-'):
				if(args[whichTable][k-j]==2):
					#print('Metric name s',metricNames[whichTable][mtrCtr],' and ',metricNames[whichTable][mtrCtr+1], 'are empty')
					metricValue1='NA'
					metricValue2='NA'
					plyrJson=plyrJson+'name: '+str(metricNames[whichTable][mtrCtr])+' trials: ['
					plyrJson=plyrJson+metricValue1+'] \n'
					mtrCtr=mtrCtr+1
					plyrJson=plyrJson+'name: '+str(metricNames[whichTable][mtrCtr])+' trials: ['
					plyrJson=plyrJson+metricValue2+'] \n'					
					mtrCtr=mtrCtr+1
				else:
					#print('Metric name ',metricNames[whichTable][mtrCtr],'is empty')
					metricValue='NA'
					plyrJson=plyrJson+'name: '+str(metricNames[whichTable][mtrCtr])+' trials: ['
					plyrJson=plyrJson+str(metricValue)+'] \n'
					mtrCtr=mtrCtr+1
					
			elif(slashLoc== -1):  # If there's no / in the text, just recorde it as a real-valued metric
				metricValue=re.findall(r'\d+\.?\d*',plyrText[k])[0]
				#print("Metric name is ",metricNames[whichTable][mtrCtr])
				#print("value is ",metricValue)
				plyrJson=plyrJson+'name: '+str(metricNames[whichTable][mtrCtr])+' trials: ['
				plyrJson=plyrJson+str(metricValue)+'] \n'

				mtrCtr=mtrCtr+1
			elif(plyrText[k].find('%')==-1):  # If there's no percent sign just process as two separate metrics
				metricText=plyrText[k].split('/')
				metricValue1=int(metricText[0])   # First one always seems to be integer
				#print("Metric name is ",metricNames[whichTable][mtrCtr])
				#print("Metric value is ",metricValue1)
				plyrJson=plyrJson+'name: '+str(metricNames[whichTable][mtrCtr])+' trials: '
				plyrJson=plyrJson+str(metricValue1)+'] \n'					
				mtrCtr=mtrCtr+1
				if(plyrText[k].find('.')==-1):
					metricValue2=int(metricText[1])
				else:
					metricValue2=float(metricText[1]) # If there's a decimal, it's a float
					
				#print("Metric name is ",metricNames[whichTable][mtrCtr])
				#print("Metric value is ",metricValue2)
				plyrJson=plyrJson+'name: '+str(metricNames[whichTable][mtrCtr])+' trials: ['
				plyrJson=plyrJson+str(metricValue2)+'] \n'	
				mtrCtr=mtrCtr+1

			else:  # If there's no slash but there is a percentage, must be a two outcome data type
				fracString=re.findall(r'\d+',plyrText[k])
				#print(fracString)
				if(len(fracString[1])==2):
					metricGood=0
					metricBad=int(fracString[0])
				elif(int(fracString[1][-3:])==100):
					metricGood=int(fracString[0])
					metricBad=0
				else:
					metricGood=int(fracString[1][0:-2])
					metricBad=int(fracString[0])-metricGood
		
				#print("Metric name is ",metricNames[whichTable][mtrCtr])
				#print("Metric values are good ",metricGood," and bad ",metricBad)
				plyrJson=plyrJson+'name: '+str(metricNames[whichTable][mtrCtr])+' trials: ['
				plyrJson=plyrJson+str(metricGood)+'/'+str(metricBad)+'] \n'		
				mtrCtr=mtrCtr+1
				
		plyrJson=plyrJson+'}]\n}'
		print(plyrJson)