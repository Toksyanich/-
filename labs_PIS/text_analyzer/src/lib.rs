// Подсчитывает количество слов в строке. Слова разделены пробелами.
pub fn count_words(text: &str) -> usize {
    text.split_whitespace().count()
}

// Находит самое длинное слово в строке.
// Возвращает None, если строка пустая.
// Если несколько слов имеют одинаковую максимальную длину, возвращает первое из них.
pub fn find_longest_word(text: &str) -> Option<&str> {
    text.split_whitespace().max_by_key(|word| word.len())
}

// Проверяет, является ли строка палиндромом.
// Игнорирует регистр, пробелы и знаки препинания.
pub fn is_palindrome(text: &str) -> bool {
    let cleaned: String = text
        .chars()
        .filter(|c| c.is_alphanumeric())
        .map(|c| c.to_lowercase().to_string())
        .collect();

    if cleaned.is_empty() {
        return true; // Считаем пустую строку палиндромом
    }

    cleaned == cleaned.chars().rev().collect::<String>()
}

// Unit tests
#[cfg(test)]
mod tests {
    use super::*;

    // --- Тесты для функции count_words ---
    #[test]
    fn test_count_words_simple() {
        assert_eq!(count_words("hello world from rust pivo"), 4);
    }

    #[test]
    fn test_count_words_empty_string() {
        assert_eq!(count_words(""), 0);
    }

    #[test]
    fn test_count_words_extra_spaces() {
        assert_eq!(count_words("  leading and trailing spaces  "), 4);
    }

    // --- Тесты для функции find_longest_word ---
    #[test]
    fn test_find_longest_word_basic() {
        assert_eq!(
            find_longest_word("find the longest word here"),
            Some("longest")
        );
    }

    #[test]
    fn test_find_longest_word_in_empty_string() {
        assert_eq!(find_longest_word(""), None);
    }

    #[test]
    fn test_find_longest_word_with_tie() {
        // Должен вернуть первое из самых длинных слов
        assert_eq!(find_longest_word("one two three four five"), Some("three"));
    }

    // --- Тесты для функции is_palindrome ---
    #[test]
    fn test_is_palindrome_true() {
        assert!(is_palindrome("A man, a plan, a canal: Panama"));
    }

    #[test]
    fn test_is_palindrome_false() {
        assert!(!is_palindrome("hello world")); // Используем ! для проверки false
    }

    #[test]
    fn test_is_palindrome_empty_string() {
        // Пустая строка или строка только из знаков препинания считается палиндромом
        assert!(is_palindrome(" ,.?!"));
    }

    #[test]
    fn test_is_palindrome_with_numbers() {
        assert!(is_palindrome("12321"));
    }
}
