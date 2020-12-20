import sqlite3
from sqlite3 import Error
from pprint import pprint as pp

from lyrics import parse_lyric


def create_connection(db_path='db.sqlite3'):
    connection = None
    try:
        connection = sqlite3.connect(db_path)
    except Error as err:
        print(err)
    return connection


def create_tables(connection):
    create_artists_songs_table = """
    CREATE TABLE IF NOT EXISTS artists (
      id integer PRIMARY KEY AUTOINCREMENT,
      name text NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS songs (
      id integer PRIMARY KEY AUTOINCREMENT,
      name text NOT NULL,
      translated_name text,
      lyric text NOT NULL,
      translated_lyric text,
      artist_id integer NOT NULL,
      FOREIGN KEY (artist_id) REFERENCES artists (id)
    );
    """
    cursor = connection.cursor()
    cursor.executescript(create_artists_songs_table)


def create_records(connection, lyric_dict):
    select_artist_id = """
    SELECT id FROM artists
    WHERE name = ?;
    """

    create_artist = """
    INSERT INTO
      artists (name)
    VALUES
      (?);
    """

    create_song = """
    INSERT INTO
      songs (name, translated_name, lyric, translated_lyric, artist_id)
    VALUES
      (?, ?, ?, ?, ?);
    """
    cursor = connection.cursor()
    artist = (lyric_dict['artist'],)
    cursor.execute(select_artist_id, artist)
    row = cursor.fetchone()
    if row is not None:
        artist_id = row[0]
    else:
        # That means there's no artist with that name yet.
        cursor.execute(create_artist, artist)
        artist_id = cursor.lastrowid
    # Create song.
    song = (
        lyric_dict['song'],
        lyric_dict['translated'],
        lyric_dict['lyric'],
        lyric_dict['translation'],
        artist_id
    )
    cursor.execute(create_song, song)
    connection.commit()


def get_song_info(connection, lyric_dict):
    select_song = """
    SELECT
      a.name,
      s.name,
      s.translated_name,
      s.lyric,
      s.translated_lyric
    FROM songs s JOIN artists a
    ON a.id = s.artist_id
    WHERE a.name = ? and s.name = ?;
    """
    cursor = connection.cursor()
    artist_song_names = (lyric_dict['artist'], lyric_dict['song'])
    cursor.execute(select_song, artist_song_names)
    row = cursor.fetchone()
    return row


def main():
    conn = create_connection()
    pass

if __name__ == '__main__':
    main()
