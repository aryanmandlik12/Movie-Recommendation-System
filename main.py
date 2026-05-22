import numpy as np
import pandas as pd
import ast
import nltk
import pickle
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

movies = pd.read_csv('TMDB_all_movies.csv')

# Data Preprocessing
# id, title, original_language, overview, genres, cast, director, poster_path
# for taking only the required columns and removing the null values and duplicates 
movies = movies[['id','title', 'original_language', 'overview', 'genres', 'cast', 'director']]
movies = movies.dropna()
print(movies.shape)
movies = movies.drop_duplicates()
print(movies.duplicated().sum())

#for converting the string representation of list to actual list
movies['genres'] = movies['genres'].apply(lambda x: x.split(', '))
movies['cast'] = movies['cast'].apply(lambda x: x.split(', '))
movies['director'] = movies['director'].apply(lambda x: x.split(', '))
movies['overview'] = movies['overview'].apply(lambda x: x.split())
print(movies.head())

#apply transformation to remove spaces because spaces can cause issue in creating tags
movies['genres'] = movies['genres'].apply(lambda x: [i.replace(" ", "") for i in x])
movies['cast'] = movies['cast'].apply(lambda x: [i.replace(" ", "") for i in x])
movies['director'] = movies['director'].apply(lambda x: [i.replace(" ", "") for i in x])
movies['overview'] = movies['overview'].apply(lambda x: [i.replace(" ", "") for i in x])
print(movies.head())

#creating a new column called tags which will contain all the information about the movie in a single column
movies['tags'] = movies['overview'] + movies['genres'] + movies['cast'] + movies['director']

new_df = movies[['id', 'title', 'tags']].copy()
new_df['tags'] = new_df['tags'].apply(lambda x: " ".join(x))
new_df['tags'] = new_df['tags'].apply(lambda x: x.lower())
new_df = new_df.reset_index(drop=True)  # fix index gaps from dropna/drop_duplicates
print(new_df.head())
pickle.dump(new_df.to_dict(), open('movies_dict.pkl', 'wb'))

#vectorization
cv = CountVectorizer(max_features=15000, stop_words='english')
vectors = cv.fit_transform(new_df['tags'])
print(vectors.shape)
pickle.dump(vectors, open('vectors.pkl', 'wb'))

#function to recommend movies based on the similarity score
def recommend(movie):
    matches = new_df[new_df['title'] == movie]
    if matches.empty:
        print(f"Movie '{movie}' not found in the dataset.")
        return
    idx = matches.index[0]
    # compute similarity only for this one movie instead of the full N×N matrix
    movie_vec = vectors[idx]
    scores = cosine_similarity(movie_vec, vectors).flatten()
    top_indices = scores.argsort()[::-1][1:6]
    print(f"Movies similar to '{movie}':")
    for i in top_indices:
        print(new_df.iloc[i]['title'])

movie_input = input("Enter a movie name: ")
recommend(movie_input)

