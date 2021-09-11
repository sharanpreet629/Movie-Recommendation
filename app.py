#Importing the libraries
import pickle
from flask import Flask, request, render_template, Markup
import numpy as np
import requests 
import pandas as pd 
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


#Global variables
app = Flask(__name__) #Creating the API

#Loading the form
@app.route('/', methods=['GET'])
def Home():
	return render_template('movies.html')


#Handling the data
df = pd.read_csv('movie_dataset.csv')

def getTitle(index):
    return df[df.index==index]['title'].values[0]

def getIndex(title):
    return df[df.title==title]['index'].values[0]


#User defined functions
@app.route('/recommend', methods=['POST'])
def sendRecommend():
	#Getting the input
	movieUserLikes = request.form['movie']
	numberOfRecs = int(request.form['recnumber'])
	userName = request.form['name']

	try:
		cv = CountVectorizer()
		countMatrix = cv.fit_transform(df['combined_features'])
		cosineSim = cosine_similarity(countMatrix)

		movieIndex = int(getIndex(movieUserLikes))
		
		similarMovies = list(enumerate(cosineSim[movieIndex]))
		sortedMovies = sorted(similarMovies, key = lambda x:x[1], reverse=True)[1:]
		returnMovies = [index for (index, sim) in sortedMovies]

		#Returning the response
		sendTitle = "Top " + str(numberOfRecs) + " movies similar to " + movieUserLikes
		sendRecs = ""
		i = 1

		for movie in returnMovies:
			sendRecs += Markup(str(i) + ". " + getTitle(movie) + "<br>") 
			i += 1
			if i > numberOfRecs:
				break

		#Saving movies in csv file
		with open('history.csv', 'a') as file:
			file.write(userName + "," + movieUserLikes + "," + str(numberOfRecs) + "," + sendRecs + "\n")

		return render_template('movies.html', movie_user_likes=sendTitle, movie_recs=sendRecs)

	except Exception as e:
		print(e)
		return render_template('new movie.html')



#Main function
if __name__ == '__main__':
	app.run(debug=True)
