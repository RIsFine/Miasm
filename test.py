from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer


def get_most_important_words(tokens, num_words=5):
    # Convert the list of tokens into a string
    text = ' '.join(tokens)

    # Create a TfidfVectorizer
    vectorizer = TfidfVectorizer()

    # Fit and transform the text
    tfidf_matrix = vectorizer.fit_transform([text])

    # Get feature names (words)
    feature_names = vectorizer.get_feature_names_out()

    # Get the TF-IDF scores for each word
    tfidf_scores = tfidf_matrix.toarray()[0]

    # Create a dictionary mapping each word to its TF-IDF score
    word_scores = dict(zip(feature_names, tfidf_scores))
    print(word_scores)

    # Sort the words based on their TF-IDF scores in descending order
    sorted_words = sorted(word_scores.items(), key=lambda x: x[1], reverse=True)

    # Return the most important words
    return [word for word, score in sorted_words[:num_words]]


# Example usage:
"""tokens = ["natural", "language", "processing", "is", "important", "for", "understanding", "text", "data"]
important_words = get_most_important_words(tokens, num_words=3)
print(important_words)"""


def standardize_synonyms_advanced(ingredient):
    synonym_mapping = {
        'all-purpose flour': 'flour',
        'plain flour': 'flour',
        'granulated sugar': 'sugar',
        'unsalted butter': 'butter',
        # Add more mappings as needed
    }

    # Tokenize and stem the ingredient for more flexibility
    tokens = word_tokenize(ingredient.lower(), language="french")
    print(tokens)
    stemmed_tokens = [SnowballStemmer("french").stem(token) for token in tokens]
    print(stemmed_tokens)
    ingredient_key = ' '.join(stemmed_tokens)

    # Check if the standardized version exists in the mapping
    standardized_ingredient = synonym_mapping.get(ingredient_key, ingredient)

    return standardized_ingredient


# Example usage
ingredients = ['Bœuf (rôti)', 'Oignon jaune', 'Carotte (frais)', 'Bouillon de bœuf (cube)', 'Pommes de terre (primeur)',
               'Thym (branches)', 'Farine de blé', 'Sauce Worcester']
for ingredient in ingredients:
    print(f"ingredient: {ingredient}, fun: {standardize_synonyms_advanced(ingredient)}")
"""standardized_ingredient = standardize_synonyms_advanced(ingredient)
print("Standardized Ingredient:", standardized_ingredient)"""
