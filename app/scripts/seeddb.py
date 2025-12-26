from app.db.session import SessionLocal
from app.models.models import Director, Genre, Movie, MovieRating


sample_directors = [
{"name": "Christopher Nolan", "birth_year": 1970},
{"name": "Greta Gerwig", "birth_year": 1983},
]


sample_genres = [
{"name": "Drama"},
{"name": "Sci-Fi"},
{"name": "Comedy"},
]


sample_movies = [
{"title": "Inception", "director_idx": 0, "release_year": 2010, "cast": "Leonardo DiCaprio"},
{"title": "Little Women", "director_idx": 1, "release_year": 2019, "cast": "Saoirse Ronan"},
]


def seed():
    db = SessionLocal()
    try:
        # directors
        dirs = []
        for d in sample_directors:
            obj = Director(name=d["name"], birth_year=d.get("birth_year"))
            db.add(obj)
            dirs.append(obj)
        db.flush()


        gens = []
        for g in sample_genres:
            obj = Genre(name=g["name"])
            db.add(obj)
            gens.append(obj)
        db.flush()


        movies = []
        for m in sample_movies:
            movie = Movie(title=m["title"], director_id=dirs[m["director_idx"]].id, release_year=m["release_year"], cast=m.get("cast"))
            movie.genres = [gens[0]] # attach Drama for simplicity
            db.add(movie)
            movies.append(movie)
        db.flush()


        # add some ratings
        for movie in movies:
            r = MovieRating(movie_id=movie.id, score=8)
            db.add(r)


        db.commit()
        print("Seeded DB successfully")
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()