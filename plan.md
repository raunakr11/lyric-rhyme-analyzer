# LYRIC RHYMING BOT

### Steps:
1. _(done)_ Retrieve Lyrics from `Genius`
    - _(done)_ get lyrics for a song from the Genius API 
    - _(done)_ take any song from input (song title and artist) and retrieve its lyrics
    <!-- - Cache lyrics locally to minimize API calls for repeated requests -->

2. _(done)_ Apply NLP to Find Different Rhymes
    - _(done)_ tokenize the lyrics into words and lines
    - _(done)_ identify rhyming syllables using a phonetic algorithm like Soundex or Metaphone
    - _(done)_ categorize words based on their rhyming patterns
    <!-- - handle edge cases such as compound words, contractions, and punctuation -->

3. Highlight Rhymes in the Lyrics
    - _(done)_ create a mapping of rhyming words to unique colors
    - annotate the lyrics with HTML/CSS for color highlighting
    - ensure that the highlighting is consistent and visually appealing

4. Prepare for Website Integration
    - design a simple web interface for inputting songs
    - develop a backend API to handle song requests and return highlighted lyrics

5. Deploy and Monitor
    - deploy the website on a cloud platform or web server free or github pages