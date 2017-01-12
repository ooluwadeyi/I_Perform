#!/usr/bin/python
from kivy.app import App 
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup 
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.progressbar import ProgressBar 
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
import os
import sys
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import re
# import smtplib
# from email.MIMEMultipart import MIMEMultipart
# from email.MIMEText import MIMEText
import sendgrid
from sendgrid.helpers.mail import *
#########################################################

col_n = []
new_scores = []
old_scores = []
email_list = []

global aValue 
aValue = 0
fname = None
dict1 = {}
dict2 = {}

class IPerformRoot(BoxLayout):

	""" Root of all the widget"""
	

	label1 = ObjectProperty(None)
	lbl_text = ObjectProperty(None)
	analyze_screen = ObjectProperty(None)
	filechooser = ObjectProperty(None)



	
	

	# create a global variable fname that will store the filename for the csv file to be analyzed.
	# the csv file path and names are supplied when the function "analyze" is called by the on_release event of the "analyze_btn" button in 
	# "AnalyzeScreen" in the kv file 

	

	#set aValue to zero so you ca use it to determine when a file has been selected in the filechooser
	
	

	def __init__(self, **kwargs):
		super(IPerformRoot, self).__init__(**kwargs)
		self.screen_list = []

	def onBackBtn(self):
		
		if self.ids.IPscreen_manager.current == "analyze_screen":

			self.ids.IPscreen_manager.current ="start_screen" 
			
			return True
		# elif self.ids.IPscreen_manager.current == "start_screen":	

		# 	content = Button(text="Yes", size_hint=(0.2,0.2))
		# 	popup =Popup(title ="Do you want to close this Application?", content=content, size_hint=(0.5,0.5), auto_dismiss = False)
		# 	content.bind(on_press=popup.dismiss)			
		# 	popup.open()

		return False	

		

	def storeAValue(self):
		# this fucntion sets global variable aValue to 2 so that you can use it to check if filechooser on_selection event has fired
		
		global aValue

		aValue = 2

	def changeEmailText(self):

		self.ids.analyze_screen.label1.text = "Performance Email Sent"	


	def changeSmsText(self):
		self.ids.analyze_screen.label1.text = "Performance SMS Sent"

	def open(self, path, filename):
		with open(os.path.join(path, filename[0])) as f:
			print f.read()

	def load(self, path, filename):
		global fname 
		global aValue
		

		


		#check if filechooser's on_selection event has been fired, then proceed if the event fired, otherwise, pop up a window to warn

		if aValue == 0:
			popup = Popup(title = "Please select a csv file", content =  Label(text = 'Please select a csv file to go to analyze'), size_hint = (0.5, 0.5), auto_dismiss= True)		
			popup.open()
		else:
			if aValue == 2:

				fname = os.path.join(path, filename[0])
				if 	fname.endswith(".csv"):

					popup = Popup(title = "Chosen file..", content =  Label(text = 'You chose to load, %s filename' % filename), size_hint = (0.5, 0.5), auto_dismiss= True)		
			
					popup.open()
					self.ids.start_screen.lbl_text.text = fname
				else:
					popup = Popup(title = "Wrong file type..", content =  Label(text = 'Please choose a csv file'), size_hint = (0.5, 0.5), auto_dismiss= True)		
			
					popup.open()
		

	def gotoAnalyzeScreen(self):

		global aValue
		global fname

		if ((aValue == 0) | (fname is None)):
			popup = Popup(title = "Please select a csv file", content =  Label(text = 'Please select a csv file to go to analyze'), size_hint = (0.5, 0.5), auto_dismiss= True)		
			popup.open()
		else:
			if aValue == 2:

				self.ids.IPscreen_manager.current = "analyze_screen"	
				

	def analyze(self):
		
		#full_filename = os.path.join(path, filename[0])

		#first check for the file extension
		#get filename and convert to a pandas dataframe, df
		global fname
		global col_n
		global new_scores
		global old_scores

		global email_list

		subjects = []

		global dict1  # holds names of all students

		global dict2 # holds all the subjects offered by students

		dict3 = {} # holds the pandas series for the difference in scores for each subject
		dict4 = {} # holds the 
		df = pd.read_csv(fname, index_col = 0)
		
		col_n = df.columns

		number_of_students = len(df.index) 

		#guard_email = df.Email

		for email in df.Email:

			email_list.append(email)

		#print email_list

		for i in range(0, (number_of_students)):

			dict1[i] = (df.iloc[i, 0])+(df.iloc[i, 1])+(df.iloc[i,2]) # dict1 holds the names of all the students

		#print dict1
		for names in col_n:

			matchNew = re.search(r'New', names, re.I)
			matchOld = re.search(r'Old', names, re.I)

			if matchNew :
                
				new_scores.append(names)

			if matchOld:                    
  				old_scores.append(names)

  		for subj in new_scores:

  			matchSubj = subj.replace('New', '').replace('Score', '')  # removes the 'New' and 'Score' in front and back of the subjects and store in list subjects 

  
  			subjects.append(matchSubj)

  			
  		for i in range(len(subjects)):

  			dict2[i] = subjects[i]  # store the subjects in the dictionary dict2 

  				
  				
		#print df.ix[:, new_scores[0]] 

		for i in range(len(new_scores)):

			dict3[i] = df.ix[:, new_scores[i]] - df.ix[:, old_scores[i]]

		pb = ProgressBar(max=100, value=25)	
		popup = Popup(title ='Please wait... sending emails..', content = pb, size_hint=(0.4,0.4), auto_dismiss=False)		
		popup.open()
		n = 0
		number_subjects = len(dict2)
		msg_list =[]
		for i in range(len(dict1)):
			for j in range(len(dict2)):

				#print("The score of %s changed by %.2f in %s " % (dict1[i], dict3[j].iloc[i], dict2[j]))

				message = ("The score of %s changed by %.2f in %s \n" % (dict1[i], dict3[j].iloc[i], dict2[j]))
				
				msg_list.append(message)

				n += 1

				if n%number_subjects ==0:


					msg1 =("Hello Parent, Please be informed that: \n\n")
					msg2 = " ".join(msg_list)
					msg = msg1 + msg2

					print msg

					# senderObj = Sender()

					# senderObj.sendEmail(email_list[i],dict1[i], msg)

					msg_list = []
					self.ids.analyze_screen.label1.text = msg
		popup.dismiss()			

		


#j###################################################################################

# class CloseApp():

# 	def closeApp(self):

# 		#self.ids.start_screen.lbl_text.text = "Closing.."
# 		os._exit(0)	


#################################################################	

class Sender():

	def __ini__(self, **kwargs):
		super(Sender, self).__init__(**kwargs)


	def sendEmail(self, RecipientEmail, student_name, message):

		myEmail = 'sunkanmi.laplace@gmail.com'
		
		try:	
			# msg = MIMEMultipart()

			# msg['From'] =  myEmail
			# msg['To'] = RecipientEmail
			# msg['Subject'] = 'Performance Report for %s ' % student_name

			# msg.attach(MIMEText(message, 'plain'))

			# server = smtplib.SMTP('smtp.gmail.com', 587)
			# server.starttls()
			# server.login(myEmail, Password)
			# text = msg.as_string()
			# server.sendmail(myEmail, RecipientEmail, text)
			# server.quit()
			sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
			from_email = Email(myEmail)
			subject = 'Performance Report for %s' % student_name
			to_email = Email(RecipientEmail)
			content = Content("text/plain", message)	
			mail = Mail(from_email, subject, to_email, content)
			response = sg.client.mail.send.post(request_body=mail.get())
			print(response.status_code)
			print(response.body)
			print(response.headers)

			

		except:

			print "Something went wrong"



class IPerformApp(App):
	
	def __init__(self, **kwargs):
		super(IPerformApp, self).__init__(**kwargs)

		Window.bind(on_keyboard=self.onBackBtn)	

	def onBackBtn(self, window, key, *args):
		
		if key == 27:

			

			return self.root.onBackBtn()	

	def build(self):
		#self.load_kv('iperform.kv')
		return IPerformRoot()

if __name__ =="__main__":
	IPerformApp().run()