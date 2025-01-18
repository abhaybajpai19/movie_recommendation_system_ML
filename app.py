from flask import Flask, render_template, request, jsonify
import pickle
import pandas as pd
import requests

app = Flask(__name__)

# Load data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Function to fetch movie poster
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    return "https://via.placeholder.com/500x750?text=No+Image+Available"

# Function to recommend movies
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_posters

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        movie_name = request.form.get("movie_name")
        recommended_movies, recommended_posters = recommend(movie_name)
        return render_template("index.html", movies=movies['title'].values, recommendations=zip(recommended_movies, recommended_posters))
    return render_template("index.html", movies=movies['title'].values, recommendations=[])

if __name__ == "__main__":
    app.run(debug=True)
