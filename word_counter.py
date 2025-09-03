import sys
import re
from collections import Counter
import string

def analyze_text(text):
    """
    Analyzes a string of text to count words, characters, and lines,
    and finds the top 3 most common words.

    Args:
        text (str): The text to be analyzed.
    """
    # 1. Count words, characters, and lines
    char_count = len(text)
    
    # Split the text by whitespace to count words
    words = text.split()
    word_count = len(words)
    
    # Count lines by counting newline characters
    line_count = text.count('\n') + 1

    # 2. Find the 3 most common words (case-insensitive)
    # Remove punctuation and convert to lowercase for accurate counting
    translator = str.maketrans('', '', string.punctuation)
    clean_text = text.lower().translate(translator)
    
    # Split the clean text into a list of words
    clean_words = re.findall(r'\b\w+\b', clean_text)
    
    # Use collections.Counter to find the most common words
    word_counts = Counter(clean_words)
    most_common = word_counts.most_common(3)
    
    # 3. Display a summary
    print("\n--- Text Analysis Report ---")
    print("-" * 28)
    print(f"Total Characters: {char_count}")
    print(f"Total Words: {word_count}")
    print(f"Total Lines: {line_count}")
    print("\nTop 3 Most Common Words:")
    if most_common:
        for word, count in most_common:
            print(f"  - '{word}': {count} times")
    else:
        print("  (No words found)")
    print("----------------------------\n")

if __name__ == "__main__":
    # Check if a command-line argument was provided
    if len(sys.argv) < 2:
        print("Error: No text provided.")
        print('Usage: python word_counter.py "Your text here"')
    else:
        # Join all arguments into a single string to handle phrases with spaces
        input_text = " ".join(sys.argv[1:])
        analyze_text(input_text)
