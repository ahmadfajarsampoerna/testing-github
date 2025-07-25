# models.py

from abc import ABC, abstractmethod

# Abstraksi
class Film(ABC):
    def __init__(self, id, judul, genre, poster, status, sutradara=None, durasi=None, rating=None, sinopsis=None, harga=50000):
        self.__id = id
        self.__judul = judul
        self.__genre = genre
        self.__poster = poster
        self.__status = status
        self.__sutradara = sutradara
        self.__durasi = durasi
        self.__rating = rating
        self.__sinopsis = sinopsis
        self.__harga = harga

    def get_id(self):
        return self.__id

    def get_judul(self):
        return self.__judul

    def get_genre(self):
        return self.__genre

    def get_poster(self):
        return self.__poster

    def get_status(self):
        return self.__status

    def get_sutradara(self):
        return self.__sutradara

    def get_durasi(self):
        return self.__durasi

    def get_rating(self):
        return self.__rating

    def get_sinopsis(self):
        return self.__sinopsis

    def get_harga(self):
        return self.__harga

    @abstractmethod
    def deskripsi(self):
        pass


class FilmSedangTayang(Film):
    def deskripsi(self):
        return f"{self.get_judul()} sedang tayang. Genre: {self.get_genre()}"


class FilmAkanDatang(Film):
    def deskripsi(self):
        return f"{self.get_judul()} akan segera tayang. Genre: {self.get_genre()}"