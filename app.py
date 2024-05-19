import json
import re
from collections import defaultdict
from typing import Dict, List
import random
import pronouncing
import streamlit as st
import lyricsgenius
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor

class Song:
    def __init__(self, lyrics: str):
        """
        Initialize the Song object with lyrics.
        
        Args:
            lyrics (str): The lyrics text.
        """
        self.lyrics = lyrics
        self.tokenized_lyrics = self.tokenize_lyrics(self.lyrics)
        self.blacklist = {"a", "the", "can", "an"}  # Define blacklist before detecting rhymes
        self.rhyme_groups = self.detect_rhymes(self.tokenized_lyrics)

    def tokenize_lyrics(self, lyrics: str) -> List[List[str]]:
        """
        Tokenize the lyrics into lines and words.
        
        Args:
            lyrics (str): The lyrics text.
            
        Returns:
            list: A list of lists, where each inner list contains words of a line.
        """
        lines = lyrics.split('\n')
        return [re.findall(r'\b\w+\b', line.lower()) for line in lines]

    @lru_cache(maxsize=10000)
    def get_phonetic_code(self, word: str) -> str:
        """
        Get the phonetic code of a word using the pronouncing library, with caching.
        
        Args:
            word (str): The word to be converted into a phonetic code.
            
        Returns:
            str: The phonetic code of the word.
        """
        pronunciations = pronouncing.phones_for_word(word)
        return pronunciations[0] if pronunciations else ''

    def get_rhyme_part(self, phonetic_code: str) -> str:
        """
        Extract the rhyming part (last syllable) from the phonetic code.
        
        Args:
            phonetic_code (str): The phonetic code of the word.
            
        Returns:
            str: The rhyming part of the phonetic code.
        """
        return phonetic_code.split()[-1] if phonetic_code else ''

    def detect_rhymes(self, tokenized_lyrics: List[List[str]]) -> Dict[str, List[str]]:
        """
        Detect rhymes in the tokenized lyrics using phonetic codes.
        
        Args:
            tokenized_lyrics (list): A list of lists containing tokenized lyrics.
            
        Returns:
            dict: A dictionary where keys are phonetic codes and values are lists of rhyming words.
        """
        rhyme_groups = defaultdict(list)
        
        def process_line(line):
            for word in line:
                if word not in self.blacklist:
                    phonetic_code = self.get_phonetic_code(word)
                    rhyme_part = self.get_rhyme_part(phonetic_code)
                    rhyme_groups[rhyme_part].append(word)

        with ThreadPoolExecutor() as executor:
            executor.map(process_line, tokenized_lyrics)

        # Filter out non-rhyming groups
        rhyme_groups = {k: v for k, v in rhyme_groups.items() if len(v) > 1}
        
        return rhyme_groups

    def assign_colors(self, rhyme_groups: Dict[str, List[str]]) -> Dict[str, str]:
        """
        Assign random colors to each rhyme group.
        
        Args:
            rhyme_groups (dict): A dictionary of rhyme groups.
            
        Returns:
            dict: A dictionary where keys are phonetic codes and values are colors.
        """
        color_palette = ["#FF6347", "#4682B4", "#32CD32", "#FFD700", "#6A5ACD", "#FF69B4", "#8B4513"]
        return {k: random.choice(color_palette) for k in rhyme_groups.keys()}

    def highlight_lyrics(self, tokenized_lyrics: List[List[str]], rhyme_colors: Dict[str, str]) -> str:
        """
        Highlight the lyrics with HTML/CSS.
        
        Args:
            tokenized_lyrics (list): A list of lists containing tokenized lyrics.
            rhyme_colors (dict): A dictionary of rhyme colors.
            
        Returns:
            str: The highlighted lyrics in HTML format.
        """
        highlighted_lyrics = []
        for line in tokenized_lyrics:
            highlighted_line = []
            for word in line:
                phonetic_code = self.get_phonetic_code(word)
                rhyme_part = self.get_rhyme_part(phonetic_code)
                color = rhyme_colors.get(rhyme_part, "white")  # Default color for non-rhyming words is white
                highlighted_line.append(f'<span style="color: {color};">{word}</span>')
            highlighted_lyrics.append(" ".join(highlighted_line))
        
        return "<br>".join(highlighted_lyrics)

    def display_rhyme_groups(self):
        """
        Display all rhyming words together.
        """
        rhyme_groups_str = []
        for rhyme_part, words in self.rhyme_groups.items():
            rhyme_groups_str.append(f"Rhyme part '{rhyme_part}': {', '.join(words)}")
        
        return "<br>".join(rhyme_groups_str)

@lru_cache(maxsize=100)
def fetch_lyrics(song_title: str, artist_name: str, genius_api_token: str) -> str:
    """
    Fetch lyrics using the Genius API, with caching.
    
    Args:
        song_title (str): The title of the song.
        artist_name (str): The name of the artist.
        genius_api_token (str): The Genius API token.
        
    Returns:
        str: The lyrics of the song.
    """
    genius = lyricsgenius.Genius(genius_api_token)
    song = genius.search_song(song_title, artist_name)
    return song.lyrics if song else ""

def main():
    st.title("Lyric Rhyme Analyzer")    
    
    genius_api_token = "put your genius api token here"
    
    song_title = st.text_input("Enter song title:")
    artist_name = st.text_input("Enter artist name:")
    
    if st.button("Fetch and Analyze Lyrics"):
        if song_title and artist_name:
            lyrics = fetch_lyrics(song_title, artist_name, genius_api_token)
            if lyrics:
                song = Song(lyrics)
                
                st.header("Highlighted Lyrics")
                rhyme_colors = song.assign_colors(song.rhyme_groups)
                highlighted_lyrics_html = song.highlight_lyrics(song.tokenized_lyrics, rhyme_colors)
                st.markdown(highlighted_lyrics_html, unsafe_allow_html=True)
                
                st.header("Rhyme Groups")
                rhyme_groups_html = song.display_rhyme_groups()
                st.markdown(rhyme_groups_html, unsafe_allow_html=True)
            else:
                st.error("Could not fetch lyrics. Please check the song title and artist name.")
        else:
            st.error("Please enter the song title and artist name.")

if __name__ == "__main__":
    main()
