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
df = pd.read_csv('movie_dataset.csv', error_bad_lines=False)

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


@app.route('/newmovie', methods=['POST'])
def newMovie():

	#Getting the details entered by the user
	userName = request.form['user']
	name = request.form['name']
	genre = request.form['genre']
	keywords = request.form['keywords']
	cast = request.form['cast']
	director = request.form['director']
	numberOfRecs = int(request.form['recnumber'])

	if len(name) == 0:
		name = " "

	if len(genre) == 0:
		genre = " "

	if len(keywords) == 0:
		keywords = " "

	if len(cast) == 0:
		cast = " "

	if len(director) == 0:
		director = " "


	df = pd.read_csv('movie_dataset.csv')
	movieIndex = df.shape[0]

	combinedFeatures = genre + " " + keywords + " " + cast + " " + director
	print(combinedFeatures)
	
	#Storing them in the dataset
	with open('movie_dataset.csv', 'a') as file:
		file.write("\n" + str(movieIndex) + ",," + genre + ",,," + keywords + ",,,,,,,,,,,,," + name + ",,," + 
		cast + ",," + director + "," + combinedFeatures)

	#Reloading the dataset and calculating the similarity
	df = pd.read_csv('movie_dataset.csv')

	cv = CountVectorizer()
	countMatrix = cv.fit_transform(df['combined_features'])
	cosineSim = cosine_similarity(countMatrix)

	similarMovies = list(enumerate(cosineSim[movieIndex]))
	sortedMovies = sorted(similarMovies, key= lambda x:x[1], reverse=True)[1:]
	returnMovies = [index for (index, sim) in sortedMovies]

	#Returning the response
	sendTitle = "Top " + str(numberOfRecs) + " movies similar to " + name
	sendRecs = ""
	i = 1

	for movie in returnMovies:
		sendRecs += Markup(str(i) + ". " + getTitle(movie) + "<br>") 
		i += 1
		if i > numberOfRecs:
			break

	#Saving movies in csv file
	with open('history.csv', 'a') as file:
		file.write(userName + "," + name + "," + str(numberOfRecs) + "," + sendRecs + "\n")

	return render_template('movies.html', movie_user_likes=sendTitle, movie_recs=sendRecs)

#Main function
if __name__ == '__main__':
	app.run(debug=True)
